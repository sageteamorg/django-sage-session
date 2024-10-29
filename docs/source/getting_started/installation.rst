Installation
============

Installing `django-sage-session` is easy with the following steps:

Using `pip` with `virtualenv`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create a Virtual Environment**:

   .. code-block:: bash

      python -m venv .venv

2. **Activate the Virtual Environment**:

   - On Windows:

     .. code-block:: bash

        .venv\Scripts\activate

   - On macOS/Linux:

     .. code-block:: bash

        source .venv/bin/activate

3. **Install `django-sage-session`**:

   .. code-block:: bash

      pip install django-sage-session

4. **Apply Migrations**:

   After installation, make sure to run the following commands to create the necessary database tables:

   .. code-block:: bash

      python manage.py makemigrations
      python manage.py migrate

Using `poetry`
~~~~~~~~~~~~~~

1. **Initialize Poetry** (if not already initialized):

   .. code-block:: bash

      poetry init

2. **Install `django-sage-session`**:

   .. code-block:: bash

      poetry add django-sage-session


3. **Apply Migrations**:

   After installation, make sure to run the following commands to create necessary database tables:

   .. code-block:: bash

      poetry run python manage.py makemigrations
      poetry run python manage.py migrate


GeoIP2 Installation and Configuration
-------------------------------------

To enable IP-based geolocation tracking for user sessions, you need to configure GeoIP2. This allows the system to track the city and country associated with the user’s IP address.

1. **Install `GeoIP2` library**:

   .. code-block:: bash

      pip install geoip2

2. **Download the GeoIP2 Database**:

   The GeoIP2 database is required for accurate geolocation. You can download the free versions from MaxMind:

   - **GeoLite2 City Database**: [Download from MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en)
   - **GeoLite2 Country Database**: [Download from MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en)

3. **Extract the downloaded files** and place them in a directory accessible by your Django project.

4. **Configure GeoIP2 in Django Settings**:

   In your `settings.py` file, configure the `GEOIP_PATH` to point to the directory where the GeoIP2 database files are stored.

   .. code-block:: python

      import os

      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

      # Set the path to the GeoIP2 database files
      GEOIP_PATH = os.path.join(BASE_DIR, 'geoip')

   You can now track the geolocation of users' IP addresses using the GeoIP2 database.

   **Full GeoIP2 Documentation**:
   For more information on GeoIP2 setup and usage, refer to the official documentation:
   - [GeoIP2 Django Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/gis/geoip2/)
   - [MaxMind GeoLite2 Databases](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en)

Django Settings Configuration
-----------------------------

To use `django-sage-session`, add it to your `INSTALLED_APPS` in the Django settings:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "sage_session",
        ...
    ]

Middleware
----------

Add the session management middleware to your `MIDDLEWARE` configuration to track session data:

.. code-block:: python

    MIDDLEWARE = [
        ...
        "sage_session.middleware.SessionManagementMiddleware",
        "sage_session.middleware.TrackUserActivityMiddleware",
        ...
    ]

Settings
--------

The following settings can be customized based on your requirements:

- **CUSTOM_SESSION_NAME**: Set a custom name for the session.

  .. code-block:: python

     CUSTOM_SESSION_NAME = "custom_session_name"

- **MAX_USER_SESSIONS**: The maximum number of concurrent sessions allowed per user (default is `10`).

  .. code-block:: python

     MAX_USER_SESSIONS = 10

- **EXPIRY_TIME**: Set the expiration time for sessions in minutes.

  .. code-block:: python

     EXPIRY_TIME = 30

URL Configuration
-----------------

To include the session management URLs, add the following to your root `urls.py`:

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        path('sessions/', include('sage_session.urls')),
    ]

