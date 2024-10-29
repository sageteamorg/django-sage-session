import pytest
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from sage_session.backends.session import SessionBackend
from sage_session.models import UserSession
from unittest.mock import patch
from django.utils import timezone
from django.utils.crypto import get_random_string


@pytest.mark.django_db
class TestSessionBackend:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="testuser", password="testpass")

    def create_django_session(self, user):
        """Helper function to create a Django session object."""
        session = Session(
            session_key=get_random_string(32),
            expire_date=timezone.now() + timezone.timedelta(minutes=5),
        )
        session.save()
        return session

    def test_create_session(self, user):
        # Create a valid Django session object
        session = self.create_django_session(user)

        # Create a mock request object with a session and user
        request = type("Request", (), {})()  # Mock request object
        request.user = user
        request.session = session  # Use the real Django session object
        request.META = {
            "HTTP_USER_AGENT": "FakeUserAgent/1.0",
            "REMOTE_ADDR": "123.123.123.123",
        }

        # Patch GeoIP2 and other static methods
        with patch("sage_session.backends.session.GeoIP2") as mock_geoip2, patch(
            "sage_session.backends.session.SessionBackend.get_browser_info"
        ) as mock_browser_info, patch(
            "sage_session.backends.session.SessionBackend.get_device_info"
        ) as mock_device_info:

            # Set the return values for mocked methods
            mock_geoip2.return_value.city.return_value = {"city": "Fake City"}
            mock_geoip2.return_value.country.return_value = {
                "country_name": "Fake Country"
            }
            mock_browser_info.return_value = "Fake Browser 1.0"
            mock_device_info.return_value = "Fake Device OS 2.0"

            # Ensure no conflicting session exists
            existing_sessions = UserSession.objects.filter(session=session)
            if existing_sessions.exists():
                existing_sessions.delete()

            # Call the backend function to create the session
            SessionBackend.create_or_update_session(request, expiry_time=5)

            # Verify the session was created
            session_manager = UserSession.objects.filter(user=user).first()
            assert session_manager is not None
            assert session_manager.ip_address == "123.123.123.123"
            assert session_manager.browser_info == "Fake Browser 1.0"
            assert session_manager.device_info == "Fake Device OS 2.0"
            assert session_manager.city is not None
            assert session_manager.country is not None
            assert session_manager.session.session_key == session.session_key
            assert session_manager.expires_at <= (
                timezone.now() + timezone.timedelta(minutes=5)
            )
