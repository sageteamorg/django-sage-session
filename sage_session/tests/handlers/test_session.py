import time
from datetime import timedelta

import pytest
from django.conf import settings
from django.http import HttpRequest

from sage_session.handlers.session import SessionHandler


@pytest.fixture(autouse=True)
def set_up_django_settings():
    settings.SECRET_KEY = "secret"
    settings.FERNET_SECRET_KEY = "o34uN6k2bR5Vz8XWcN7uFgfpX_Q0G63BRw8RXBbHrZI=!"
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    settings.INSTALLED_APPS = ["django.contrib.sessions"]


@pytest.fixture
def http_request():
    request = HttpRequest()
    request.session = {}
    return request


def test_storge_and_retrieve_value(http_request):

    session_handler = SessionHandler(http_request)
    session_handler.set("username", "user_test")
    assert session_handler.get("username") == "user_test"


def test_storge_value_with_expiry(http_request):

    session_handler = SessionHandler(http_request)
    session_handler.set("username", "user_test", lifespan=timedelta(seconds=2))
    assert session_handler.get("username") == "user_test"

    time.sleep(2)

    assert session_handler.get("username") is None


def test_delete_value(http_request):

    session_handler = SessionHandler(http_request)
    session_handler.set("username", "user_test")

    session_handler.delete("username")

    assert session_handler.get("username") is None


def test_check_value_existence(http_request):
    session_handler = SessionHandler(http_request)

    assert not session_handler.exists("username")

    session_handler.set("username", "user_test")

    assert session_handler.exists("username")


def test_store_and_retrieve_value_without_encryption(http_request):

    session_handler = SessionHandler(http_request)
    session_handler.set("username", "user_test", encrypt=False)
    assert session_handler.get("username", decrypt=False) == "user_test"
