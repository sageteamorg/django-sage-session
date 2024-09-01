from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SageSessionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sage_session"
    verbose_name = _("Sage Session Management")