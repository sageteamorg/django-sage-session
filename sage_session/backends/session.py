import logging
from ipware import get_client_ip
from django.utils import timezone
from sage_session.models import UserSession
from user_agents import parse
from django.contrib.gis.geoip2 import GeoIP2

logger = logging.getLogger(__name__)


class SessionBackend:
    """
    A utility class responsible for managing and updating session-related data,
    including user IP address, browser, and device information. This class
    ensures that the session data is tracked and updated with relevant
    information such as geographic location, device details, and time.
    """

    @staticmethod
    def create_or_update_session(request, expiry_time):
        """
        Creates or updates a session for the authenticated user by extracting
        information such as the IP address, geographic location (city and
        country), browser information, and device information. The session
        expiration time is also set.
        """
        g = GeoIP2()
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        ip_address, is_routable = get_client_ip(request)

        if ip_address in ["127.0.0.1", "localhost"] or not is_routable:
            city = {
                "accuracy_radius": None,
                "city": "Local",
                "continent_code": None,
                "continent_name": None,
                "country_code": None,
                "country_name": "Local Network",
                "dma_code": None,
                "is_in_european_union": None,
                "latitude": None,
                "longitude": None,
                "metro_code": None,
                "postal_code": None,
                "region": None,
                "region_code": None,
                "region_name": None,
                "time_zone": None,
            }
            country = {
                "continent_code": None,
                "continent_name": None,
                "country_code": None,
                "country_name": "Local Network",
                "is_in_european_union": None,
            }
        else:
            city = g.city(ip_address)
            country = g.country(ip_address)

        browser_info = SessionBackend.get_browser_info(user_agent)
        device_info = SessionBackend.get_device_info(user_agent)

        UserSession.objects.create(
            user=request.user,
            session_id=request.session.session_key,
            ip_address=ip_address,
            browser_info=browser_info,
            device_info=device_info,
            last_activity=timezone.now(),
            city=city,
            country=country,
            expires_at=timezone.now() + timezone.timedelta(minutes=expiry_time),
        )

    @staticmethod
    def get_browser_info(user_agent):
        """
        Extracts and returns the browser information from the `User-Agent`
        string.
        """
        ua = parse(user_agent)
        return f"{ua.browser.family} {ua.browser.version_string}"

    @staticmethod
    def get_device_info(user_agent):
        """
        Extracts and returns the device and operating system (OS) information
        from the `User-Agent` string.
        """
        ua = parse(user_agent)
        return f"{ua.device.family} {ua.os.family} {ua.os.version_string}"
