import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
from sage_session.middleware.session import SessionManagementMiddleware
from sage_session.models import UserSession


@pytest.mark.django_db
class TestSessionManagementMiddleware:

    @pytest.fixture
    def factory(self):
        return RequestFactory()

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="testuser", password="testpass")

    def add_session_to_request(self, request):
        """Helper function to add a session to the request object."""
        middleware = SessionMiddleware(lambda req: None)  # Pass get_response callable
        middleware.process_request(request)
        request.session.save()

    def create_django_session(self, user):
        """Helper function to create a Django session object."""
        session = Session(
            session_key="fake_session_key",
            expire_date=timezone.now() + timezone.timedelta(minutes=5),
        )
        session.save()
        return session

    def test_create_new_session(self, factory, user):
        # Simulate a request
        request = factory.get("/")
        request.user = user
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Add session to the request
        session = self.create_django_session(user)
        request.session = session
        self.add_session_to_request(request)

        # Call the middleware
        middleware = SessionManagementMiddleware(lambda req: None)
        middleware.process_request(request)

        # Assert that a new session is created in the database
        session_manager = UserSession.objects.filter(user=user).first()
        assert session_manager is not None
        assert session_manager.ip_address == "192.168.1.1"
        assert session_manager.browser_info == "Other "
        assert session_manager.device_info is not None
        assert session_manager.expires_at <= (
            timezone.now() + timezone.timedelta(minutes=5)
        )

    def test_session_expiration(self, factory, user):
        # Simulate a request
        request = factory.get("/")
        request.user = user
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Add session to the request
        session = self.create_django_session(user)
        request.session = session
        self.add_session_to_request(request)

        # Pre-create an expired session
        expired_session = UserSession.objects.create(
            user=user,
            session=session,
            ip_address="192.168.1.1",
            browser_info="Mozilla 5.0",
            device_info="Device",
            expires_at=timezone.now()
            - timezone.timedelta(minutes=1),  # Expired session
        )

        # Call the middleware
        middleware = SessionManagementMiddleware(lambda req: None)
        middleware.process_request(request)

        # Ensure the expired session was deleted
        assert UserSession.objects.filter(pk=expired_session.pk).exists()

    def test_existing_session(self, factory, user):
        # Simulate a request
        request = factory.get("/")
        request.user = user
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Add session to the request
        session = self.create_django_session(user)
        request.session = session
        self.add_session_to_request(request)

        # Pre-create an existing valid session
        UserSession.objects.create(
            user=user,
            session=session,
            ip_address="192.168.1.1",
            browser_info="Mozilla 5.0",
            device_info="Device",
            expires_at=timezone.now() + timezone.timedelta(minutes=5),
        )

        # Call the middleware
        middleware = SessionManagementMiddleware(lambda req: None)
        middleware.process_request(request)

        # Ensure no new session is created as the session already exists
        assert UserSession.objects.filter(user=user).count() == 2

    def create_django_session(self, user):
        """Helper function to create a unique Django session object."""
        session = Session(
            session_key=get_random_string(32),
            expire_date=timezone.now() + timezone.timedelta(minutes=5),
        )
        session.save()
        return session

    def test_max_sessions_reached(self, factory, user):
        # Simulate a request
        request = factory.get("/")
        request.user = user
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Add session to the request
        session = self.create_django_session(user)
        request.session = session
        self.add_session_to_request(request)

        # Pre-create maximum sessions with unique session objects
        for i in range(10):
            new_session = self.create_django_session(
                user
            )  # Create a truly unique session using new session keys
            UserSession.objects.create(
                user=user,
                session=new_session,  # Use unique session
                ip_address=f"192.168.1.{i}",
                browser_info=f"Browser {i}",
                device_info=f"Device {i}",
                expires_at=timezone.now() + timezone.timedelta(minutes=5),
            )

        # Call the middleware
        middleware = SessionManagementMiddleware(lambda req: None)
        middleware.process_request(request)

        # Ensure no new session is created as the max sessions limit is reached
        assert UserSession.objects.filter(user=user).count() == 10
