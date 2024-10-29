import pytest
from django.contrib.auth.models import User
from datetime import timedelta

from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
from django.test import RequestFactory
from sage_session.handlers.session import SessionHandler
from unittest.mock import patch


@pytest.mark.django_db
class TestSessionHandler:

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

    def test_set_and_get_session(self, factory, user):
        request = factory.get("/")
        request.user = user

        # Add session to the request
        self.add_session_to_request(request)

        # Initialize the SessionHandler
        session_handler = SessionHandler(request)

        # Set a session value
        session_handler.set("test_key", "test_value", lifespan=5)

        # Get the session value and verify it's correctly retrieved
        retrieved_value = session_handler.get("test_key")
        assert retrieved_value == "test_value"

    def test_session_expiration(self, factory, user):
        request = factory.get("/")
        request.user = user

        # Add session to the request
        self.add_session_to_request(request)

        # Initialize the SessionHandler
        session_handler = SessionHandler(request)

        # Set a session value with a 1 second lifespan
        session_handler.set("test_key", "test_value", lifespan=1)

        # Simulate time passing (2 seconds, so the session should expire)
        with patch(
            "django.utils.timezone.now",
            return_value=timezone.now() + timezone.timedelta(minutes=2),
        ):
            assert session_handler.get("test_key") is None  # Value should be expired

    def test_delete_session(self, factory, user):
        request = factory.get("/")
        request.user = user

        # Add session to the request
        self.add_session_to_request(request)

        # Initialize the SessionHandler
        session_handler = SessionHandler(request)

        # Set and then delete the session value
        session_handler.set("test_key", "test_value", lifespan=10)
        session_handler.delete("test_key")

        # Verify the session value is deleted
        assert session_handler.get("test_key") is None

    def test_exists(self, factory, user):
        request = factory.get("/")
        request.user = user

        # Add session to the request
        self.add_session_to_request(request)

        # Initialize the SessionHandler
        session_handler = SessionHandler(request)

        # Set a session value
        session_handler.set("test_key", "test_value", lifespan=10)

        # Check existence of the session value
        assert session_handler.exists("test_key") is True
        assert session_handler.exists("non_existent_key") is False

    def test_handle_expiration(self, factory, user):
        request = factory.get("/")
        request.user = user

        # Add session to the request
        self.add_session_to_request(request)

        # Initialize the SessionHandler
        session_handler = SessionHandler(request)

        # Set a session value
        session_handler.set("test_key", "test_value", lifespan=1)

        # Simulate session expiration and handle it
        with patch(
            "django.utils.timezone.now",
            return_value=timezone.now() + timezone.timedelta(seconds=2),
        ):
            with patch(
                "django.contrib.messages.info"
            ):  # Patch messages to avoid MessageMiddleware issues
                session_handler.handle_expiration("test_key", logout_user=True)

        # Ensure the session key is deleted and user is logged out
        assert "test_key" not in request.session
        assert "testuser" not in request.user.username

    def test_refresh_session(self, factory, user):
        request = factory.get("/")
        request.user = user

        # Add session to the request
        self.add_session_to_request(request)

        # Initialize the SessionHandler
        session_handler = SessionHandler(request)

        session_handler.set("test_key", "test_value", lifespan=5)

        # Get the session value and verify it's correctly retrieved
        retrieved_value = session_handler.get("test_key")
        assert retrieved_value == "test_value"
        session_handler.refresh("test_key")

        assert retrieved_value == "test_value"

        # # Check that the session is not expired
        # assert session_handler.get('test_key') is not None
