from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _


class UserSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        unique=False,
        verbose_name=_("user"),
        help_text=_("The user associated with this session."),
        db_comment="Reference to the user associated with this session.",
    )
    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        verbose_name=_("session"),
        help_text=_("The session associated with this record."),
        db_comment="Reference to the Django session instance.",
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP address"),
        help_text=_("The IP address from which the session originated."),
        db_comment="IP address of the device initiating the session.",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("city"),
        help_text=_("The city associated with the IP address."),
        db_comment="City information based on the IP address.",
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("country"),
        help_text=_("The country associated with the IP address."),
        db_comment="Country information based on the IP address.",
    )
    browser_info = models.TextField(
        verbose_name=_("browser information"),
        help_text=_("Information about the browser used for this session."),
        db_comment="Details about the browser used in the session.",
    )
    device_info = models.TextField(
        verbose_name=_("device information"),
        help_text=_("Information about the device used for this session."),
        db_comment="Details about the device used in the session.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
        help_text=_("The date and time when the session was created."),
        db_comment="Timestamp when the session record was created.",
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("last activity"),
        help_text=_("The date and time of the last activity in the session."),
        db_comment="Timestamp of the last activity recorded in the session.",
    )
    expires_at = models.DateTimeField(
        null=True,
        verbose_name=_("expires at"),
        help_text=_("The date and time when the session expires."),
        db_comment="Timestamp indicating when the session expires.",
    )

    def __str__(self):
        return f"{self.user.username}-{self.session.session_key}"

    def __repr__(self) -> str:
        return f"{self.user.username}-{self.session.session_key}"

    class Meta:
        db_table = "sage_session_user_info"
        managed = True
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
