from django.db import models
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _

from sage_tools.mixins.models import TimeStampMixin


class UserSession(TimeStampMixin):
    """
    UserSession Model
    
    The UserSession model serves as a bridge between Django's built-in session management framework and user-specific session metadata. 
    It is designed to extend the functionality of the default session system by associating additional data with each user session. 
    This data can be used for monitoring, auditing, and enhancing session-related functionality in a Django application. 
    
    ## Purpose and Use Cases:
    
    - `Enhanced Session Tracking:` Provides the ability to track user sessions beyond the default session framework, 
      including geographic and device-specific details, such as IP addresses, browser, and device information.
    - `Auditing and Compliance:` Supports logging and tracking of session activities for compliance with various data protection laws 
      (e.g., GDPR, CCPA) by recording timestamps and related metadata.
    - `Security Enhancements:` Enables administrators to monitor session usage patterns, detect anomalies, and implement advanced security measures 
      (e.g., geolocation-based restrictions or IP whitelisting).
    - `Session Management:` Provides a systematic approach to managing sessions, including identifying idle sessions, tracking last activity timestamps, 
      and handling session expiration.

    ## Key Features:
    
    - `Integration with Django Session Framework:` Leverages Django's session middleware and integrates seamlessly 
      with the `Session` model for managing session lifecycle and persistence.
    - `Database-Level Metadata:` Records metadata at the database level for sessions, such as IP address, geographic location, 
      and device/browser information.
    - `Customizable Table and Attributes:` The database table name, comments, and verbose descriptions are customizable, 
      providing flexibility for project-specific naming conventions and documentation.
    - `Timestamp Management:` Records creation and last activity timestamps, which are crucial for session monitoring and expiration handling.
    - `Security-Oriented Design:` Designed with security and auditability in mind, offering fields and metadata that support better control and transparency.
    
    ## Security Concerns:
    
    While the UserSession model enhances session management capabilities, it is critical to address security considerations to protect user data:
    
    1. `Session Hijacking and Replay Attacks:` Ensure that session data is transmitted securely using HTTPS. Additionally, the model 
       can be integrated with middleware to monitor changes in IP address or browser metadata that might indicate session hijacking.
       Refer to [RFC 6265](https://www.rfc-editor.org/rfc/rfc6265) for guidelines on HTTP state management and secure cookie handling.
       
    2. `Sensitive Data Exposure:` Limit access to sensitive session metadata (e.g., IP address, browser/device information) 
       using appropriate database permissions and secure logging practices. Ensure that this data is anonymized or encrypted when necessary.
       
    3. `Session Expiration and Invalidation:` The `expires_at` field is essential for ensuring sessions are invalidated after a defined duration of inactivity. 
       Consider implementing a rolling session expiration mechanism for prolonged user sessions.
       Refer to [OWASP Session Management Guidelines](https://owasp.org/www-project-top-ten/) for best practices on session expiration and renewal.
       
    4. `Cross-Site Scripting (XSS) Prevention:` Ensure that any session data displayed on the frontend is properly sanitized and escaped 
       to prevent injection vulnerabilities.
       
    5. `IP Address Privacy:` Comply with relevant privacy regulations, such as GDPR and CCPA, when storing and processing IP address data. 
       Provide mechanisms for users to request data deletion or anonymization if required by law.
    
    ## Configuration Options:
    
    - `Database Table:` The model uses a custom table name (`sage_session_user_info`), which can be modified for specific project requirements.
    - `Managed:` The `managed` attribute allows for flexibility in managing the table through Django's migrations framework or external tools.
    - `Verbose Names:` The `verbose_name` and `verbose_name_plural` provide human-readable names for administrative and documentation purposes.
    - `Comments:` Database comments (`db_comment`) are included to document field-level purposes, improving schema maintainability and readability.

    ## Examples:
    
    ### Basic Usage:
    
    ```python
    from myapp.models import UserSession
    
    # Creating a UserSession instance
    session_instance = UserSession.objects.create(
        user=some_user,
        session=some_session,
        ip_address="192.168.1.1",
        city="San Francisco",
        country="USA",
        browser_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        device_info="Dell XPS 13",
        last_activity=timezone.now(),
        expires_at=timezone.now() + timedelta(hours=1),
    )
    
    # Querying UserSession
    active_sessions = UserSession.objects.filter(
        user=some_user, expires_at__gt=timezone.now()
    )
    ```
    
    ### Security Monitoring:
    
    ```python
    from myapp.models import UserSession
    
    # Detect suspicious sessions from different countries for the same user
    user_sessions = UserSession.objects.filter(user=some_user)
    session_countries = set(session.country for session in user_sessions)
    
    if len(session_countries) > 1:
        alert_admin("Suspicious session activity detected for user: {}".format(some_user.username))
    ```
    
    This model provides a powerful tool for extending session tracking and monitoring in Django, supporting both application-specific functionality and broader compliance and security objectives.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        help_text=_("The user associated with this session. This is used to identify the owner of the session."),
        db_comment="Reference to the user associated with this session for ownership tracking.",
    )

    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        verbose_name=_("Session"),
        help_text=_("The Django session associated with this record. Ensures one session per record."),
        db_comment="Reference to the Django session instance for session tracking.",
    )

    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP Address"),
        help_text=_("The IP address from which the session originated. Used for monitoring and security purposes."),
        db_comment="Stores the IP address of the device initiating the session (IPv4/IPv6).",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("City"),
        help_text=_("The city associated with the session's IP address. This is derived from geolocation data."),
        db_comment="Optional field to store city information based on the IP address.",
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Country"),
        help_text=_("The country associated with the session's IP address. Derived from geolocation data."),
        db_comment="Optional field to store country information based on the IP address.",
    )

    browser_info = models.TextField(
        verbose_name=_("Browser Information"),
        help_text=_("Details about the browser used to access this session. Helps identify user agents."),
        db_comment="Stores detailed user-agent string or browser metadata for the session.",
    )

    device_info = models.TextField(
        verbose_name=_("Device Information"),
        help_text=_("Information about the device used for this session. Helps track device type and operating system."),
        db_comment="Stores metadata about the device (e.g., model, OS) used during the session.",
    )

    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Activity"),
        help_text=_("The timestamp of the last recorded activity during the session. Can be null if tracking is disabled."),
        db_comment="Records the last activity timestamp for the session. Useful for monitoring activity.",
    )

    expires_at = models.DateTimeField(
        null=True,
        verbose_name=_("Expires At"),
        help_text=_("The timestamp when the session is set to expire. Used for enforcing session duration policies."),
        db_comment="Indicates the expiration time for the session. Helps manage session lifecycle.",
    )

    def __str__(self):
        return f"{self.user.username}-{self.session.session_key}"

    def __repr__(self) -> str:
        return f"{self.user.username}-{self.session.session_key}"

    class Meta:
        db_table = "sage_session_user_info"
        managed = True
        verbose_name = _("User Session")
        verbose_name_plural = _("User Sessions")
