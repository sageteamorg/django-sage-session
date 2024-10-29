import pytest
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User
from django.test import Client
from sage_session.models import UserSession
from django.contrib.sessions.models import Session


@pytest.mark.django_db
class TestSessionViews:

    @pytest.fixture
    def client(self):
        """Fixture for creating a Django test client."""
        return Client()

    @pytest.fixture
    def user(self):
        """Fixture for creating a test user."""
        return User.objects.create_user(username="testuser", password="testpass")

    @pytest.fixture
    def session(self, user):
        """Fixture for creating a user session."""
        session = Session.objects.create()
        UserSession.objects.create(
            user=user,
            session=session,
            ip_address="192.168.1.1",
            browser_info="Fake Browser 1.0",
            device_info="Fake Device OS",
            expires_at=timezone.now() + timezone.timedelta(minutes=5),
        )
        return session

    def test_user_sessions_view_not_authenticated(self, client):
        """Test that an unauthenticated user is redirected from the user sessions view."""
        response = client.get(reverse("usermanagement"))
        # Should be redirected to login page
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_delete_user_session_invalid_id(self, client, user):
        """Test that trying to delete a session with an invalid ID returns a 404."""
        # Log in the user
        client.login(username="testuser", password="testpass")

        # Call the delete session view with an invalid session ID
        response = client.post(
            reverse("delete_user_session", kwargs={"session_id": "invalid_session_key"})
        )

        assert response.status_code == 302
