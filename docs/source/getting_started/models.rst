Models Layer
============

The models layer defines the database models used to track user sessions, including IP addresses, device information, and activity tracking. These models can be easily integrated into Django's admin interface.

UserSession Model
--------------------

The `UserSession` model is responsible for tracking individual user sessions. Each session stores the following information, including the IP address, browser, and device used, as well as timestamps for session creation and last activity.

Fields
^^^^^^

- `user`: The user associated with this session. This is a foreign key to Django's built-in `User` model.
- `session`: A one-to-one field to Django’s `Session` model to uniquely track each session.
- `ip_address`: The IP address from which the session originated.
- `browser_info`: Information about the browser used for this session.
- `device_info`: Information about the device used for this session.
- `city`: City information based on the user's IP address (optional).
- `country`: Country information based on the user's IP address (optional).
- `created_at`: The date and time when the session was created.
- `last_activity`: The date and time of the last recorded activity in the session.
- `expires_at`: The date and time when the session is set to expire.

Session Tracking Example
^^^^^^^^^^^^^^^^^^^^^^^^

This example shows how the `UserSession` model tracks and stores details for each user session.

.. code-block:: python

    from django.contrib.auth.models import User
    from django.contrib.sessions.models import Session
    from sage_session.models import UserSession

    # Create a new session for a user
    user = User.objects.get(username='testuser')
    session = Session.objects.create(session_key='example_session_key')

    # Create a UserSession entry to track the session
    session_manager = UserSession.objects.create(
        user=user,
        session=session,
        ip_address='192.168.1.1',
        browser_info='Chrome 95.0',
        device_info='Windows 10',
        city='New York',
        country='USA',
        expires_at=timezone.now() + timezone.timedelta(hours=1)
    )

    # Update the last activity of the session
    session_manager.last_activity = timezone.now()
    session_manager.save()


Session Expiration
------------------

The `expires_at` field defines when the session should expire. This field is managed automatically, based on the session timeout settings defined in your project. You can adjust the session expiration with the following setting:

.. code-block:: python

    EXPIRY_TIME = 30 
