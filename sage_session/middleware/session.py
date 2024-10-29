import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from sage_session.handlers.session import SessionHandler
from sage_session.backends.session import SessionBackend
from sage_session.models import UserSession

logger = logging.getLogger(__name__)


class SessionManagementMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if not request.session.session_key:
                request.session.save()
            session_handler = SessionHandler(request)

            session_name = getattr(settings, "CUSTOM_SESSION_NAME", "default_session")
            expiry_time = getattr(settings, "EXPIRY_TIME", 5)

            if not session_handler.exists(session_name):
                max_sessions = getattr(settings, "MAX_USER_SESSIONS", 10)

                active_sessions_count = UserSession.objects.filter(
                    user=request.user
                ).count()

                if active_sessions_count < max_sessions:
                    session_handler.set(session_name, "Rc", expiry_time)
                    SessionBackend.create_or_update_session(request, expiry_time)
                else:
                    logger.info(
                        "User %s has reached the maximum number of allowed sessions.",
                        request.user,
                    )
            else:
                if session_handler.is_expired(session_name):
                    session_handler.handle_expiration(session_name)
                    return
