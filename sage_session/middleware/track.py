from django.utils import timezone
from sage_session.models import UserSession


class TrackUserActivityMiddleware:
    """
    Middleware to track the last activity of the user and update the 'last_activity'
    field in the session manager.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            session_manager = UserSession.objects.filter(
                user=request.user, session__session_key=request.session.session_key
            ).first()
            if session_manager:
                session_manager.last_activity = timezone.now()
                session_manager.save()

        response = self.get_response(request)
        return response
