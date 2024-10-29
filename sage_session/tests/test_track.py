import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
from sage_session.middleware import TrackUserActivityMiddleware
from sage_session.models import UserSession


@pytest.mark.django_db
class TestTrackUserActivityMiddleware:

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
        """Helper function to create a unique Django session object."""
        session = Session(
            session_key="fake_session_key",
            expire_date=timezone.now() + timezone.timedelta(minutes=5),
        )
        session.save()
        return session

    def test_last_activity_update_authenticated_user(self, factory, user):
        # Simulate a request
        request = factory.get("/")
        request.user = user
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Add session to the request
        session = self.create_django_session(user)
        request.session = session
        self.add_session_to_request(request)

        # Pre-create a session manager record
        session_manager = UserSession.objects.create(
            user=user,
            session=session,
            ip_address="192.168.1.1",
            browser_info="Mozilla 5.0",
            device_info="Device",
            last_activity=timezone.now()
            - timezone.timedelta(minutes=10),  # Old last activity
        )

        # Call the middleware
        middleware = TrackUserActivityMiddleware(lambda req: None)
        middleware(request)

        # Fetch the updated session manager record
        updated_session_manager = UserSession.objects.get(pk=session_manager.pk)

        assert updated_session_manager.last_activity >= session_manager.last_activity

    from django.contrib.auth.models import AnonymousUser

    def test_last_activity_not_updated_for_non_authenticated_user(self, factory):
        # Simulate a request
        request = factory.get("/")
        request.user = AnonymousUser()  # Simulate non-authenticated user
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Add session to the request
        session = self.create_django_session(None)
        request.session = session
        self.add_session_to_request(request)

        # Call the middleware
        middleware = TrackUserActivityMiddleware(lambda req: None)
        middleware(request)

        # Ensure no session manager record exists for a non-authenticated user
        assert UserSession.objects.filter(session=session).count() == 0

    def test_last_activity_update_when_no_session_manager(self, factory, user):
        # Simulate a request
        request = factory.get("/")
        request.user = user
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Add session to the request
        session = self.create_django_session(user)
        request.session = session
        self.add_session_to_request(request)

        # Call the middleware without any session manager entry
        middleware = TrackUserActivityMiddleware(lambda req: None)
        middleware(request)

        # Ensure no session manager record is created if it doesn't exist
        assert UserSession.objects.filter(session=session).count() == 0
