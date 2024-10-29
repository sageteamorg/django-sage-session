Middleware Layer
================

The middleware layer contains the core logic for managing user sessions, tracking activity, and handling session expirations. Below are detailed descriptions of the key middlewares and their usage examples.

SessionManagementMiddleware Class
---------------------------------

The `SessionManagementMiddleware` class is responsible for managing user sessions, enforcing maximum session limits, and handling session expiration.

Methods
^^^^^^^

- `process_request(self, request)`
  Manages the request by checking the user’s session, handling session expiration, and enforcing the maximum number of concurrent sessions.

  **Arguments:**
  - `request`: The HTTP request object passed to the middleware.

  **Key Functionality:**
  - If the session does not exist, it creates a new session.
  - If the maximum number of concurrent sessions is reached, it prevents new sessions from being created.
  - If the session is expired, the user is logged out, and the session is terminated.

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

    # Add this middleware to your Django settings
    MIDDLEWARE = [
        ...
        "sage_session.middleware.SessionManagementMiddleware",
        ...
    ]

TrackUserActivityMiddleware Class
---------------------------------

The `TrackUserActivityMiddleware` class tracks the user's activity by updating the `last_activity` field of the session in the database.

Methods
^^^^^^^

- `__call__(self, request)`
  Updates the last activity time for the user’s session on each request.

  **Arguments:**
  - `request`: The HTTP request object passed to the middleware.

  **Key Functionality:**
  - On each request, the `last_activity` field in the session model is updated with the current time to track when the user was last active.

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

    # Add this middleware to your Django settings
    MIDDLEWARE = [
        ...
        "sage_session.middleware.TrackUserActivityMiddleware",
        ...
    ]