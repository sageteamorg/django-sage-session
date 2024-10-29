SessionHandler Class
--------------------

The `SessionHandler` class handles session-related logic, including encryption, expiration, and management of session variables.

Methods
^^^^^^^

- `set(self, key: str, value: str, lifespan=timedelta(minutes=10), encrypt=True)`
  Sets an encrypted session variable with an optional lifespan.

  **Arguments:**
  - `key`: The key for the session variable.
  - `value`: The value to store in the session.
  - `lifespan`: The time duration (in minutes) for which the session should remain active. Default is 10 minutes.
  - `encrypt`: Whether to encrypt the session data.

- `get(self, key: str, decrypt=True) -> Optional[str]`
  Retrieves a session variable. If `decrypt` is `True`, it will decrypt the data before returning.

  **Arguments:**
  - `key`: The key for the session variable.
  - `decrypt`: Whether to decrypt the session data.

- `delete(self, key: str)`
  Deletes the session variable associated with the given key.

- `is_expired(self, key: str) -> bool`
  Checks if the session variable has expired.

- `handle_expiration(self, key: str, logout_user=True)`
  Handles session expiration by logging out the user and deleting the session.

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

    # Initialize the SessionHandler with the request object
    from sage_session.handlers.session import SessionHandler

    session_handler = SessionHandler(request)

    # Set a session variable with encryption
    session_handler.set("user_data", "some_value", lifespan=20, encrypt=True)

    # Get the session variable
    value = session_handler.get("user_data")

    # Delete the session variable
    session_handler.delete("user_data")

    # Check if the session has expired
    if session_handler.is_expired("user_data"):
        session_handler.handle_expiration("user_data", logout_user=True)
