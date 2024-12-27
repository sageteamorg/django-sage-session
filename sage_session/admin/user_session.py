from django.contrib import admin
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _
from sage_session.models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "session",
        "ip_address",
        "city",
        "country",
        "browser_info",
        "device_info",
        "created_at",
        "last_activity",
        "expires_at",
    )
    list_filter = (
        "user",
        "created_at",
        "last_activity",
        "expires_at",
        "country",
        "browser_info",
    )
    search_fields = (
        "session__session_key",
        "user__username",
        "ip_address",
        "city",
        "country",
        "browser_info",
        "device_info",
    )
    autocomplete_fields = (
        'user',
        'session',
    )
    fieldsets = (
        (
            _("Session Details"),
            {
                "description": _(
                    "This section contains information about the user session, including browser and device details."
                ),
                "fields": (
                    "user",
                    "session",
                    "ip_address",
                    "city",
                    "country",
                    "browser_info",
                    "device_info",
                ),
            },
        ),
        (
            _("Activity Tracking"),
            {
                "description": _(
                    "This section contains timestamps tracking the session creation, last activity, and expiration."
                ),
                "fields": (
                    "last_activity",
                    "expires_at",
                ),
            },
        ),
    )
    date_hierarchy = "created_at"
    list_per_page = 20


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'expire_date']
    search_fields = ['session_key',]
