from django.views.generic import ListView, View
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.sessions.models import Session
from sage_session.models import UserSession

BROWSER_ICONS = {
    "Chrome": "fa-chrome",
    "Firefox": "fa-firefox",
    "Safari": "fa-safari",
    "Edge": "fa-edge",
    "Opera": "fa-opera",
    "Internet Explorer": "fa-internet-explorer",
}


class DynamicTemplateMixin:
    template_name = None
    context_object_name = "sessions"

    def get_template_name(self):
        return self.template_name or "default_template.html"

    def get_queryset(self):
        """Fetches and processes the user session data."""
        sessions = UserSession.objects.filter(user=self.request.user)

        session_data = []
        for session in sessions:
            browser_name = session.browser_info.split()[0]
            icon_class = BROWSER_ICONS.get(
                browser_name, "fa-question-circle"
            )  # Default icon if not found
            session_data.append(
                {
                    "device_info": session.device_info,
                    "ip_address": session.ip_address,
                    "browser_info": session.browser_info,
                    "browser_icon": icon_class,
                    "last_activity": session.last_activity,
                    "session_id": session.session_id,
                }
            )
        return session_data

    def get_context_data(self, **kwargs):
        """Adds session data to the context."""
        context = super().get_context_data(**kwargs)
        context[self.context_object_name] = self.get_queryset()
        return context


class UserSessionsView(DynamicTemplateMixin, LoginRequiredMixin, ListView):
    template_name = "user_sessions.html"


class DeleteSessionMixin(DynamicTemplateMixin, LoginRequiredMixin):
    """Mixin for handling session deletion with dynamic template."""

    def post(self, request, session_id):
        try:
            session = Session.objects.get(session_key=session_id)
            session.delete()  # Remove session from session store
        except Session.DoesNotExist:
            messages.error(request, "Session not found.")
        else:
            messages.success(request, "Session successfully deleted.")
        return redirect(reverse_lazy("usermanagement"))


class DeleteSessionView(DeleteSessionMixin, View):
    """View that uses DeleteSessionMixin to delete a session."""

    pass
