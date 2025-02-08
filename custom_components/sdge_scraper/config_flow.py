import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class GasUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gas Usage Integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step of the config flow (UI form for username and password)."""
        if user_input is None:
            # Display the form to the user
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_schema(),
            )
        
        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]

        # Validate the username and password (you can make a request here if needed)
        if not self._validate_credentials(username, password):
            return self.async_show_form(
                step_id="user",
                errors={"base": "invalid_credentials"},
            )

        # Successfully validated credentials, create entry
        return self.async_create_entry(
            title=f"Gas Usage for {username}",
            data={CONF_USERNAME: username, CONF_PASSWORD: password},
        )

    def _get_schema(self):
        """Return the schema for user input."""
        return vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

    def _validate_credentials(self, username, password):
        """Validate the credentials."""
        try:
            # Example: Simulate credential validation by checking hardcoded values (replace with actual validation)
            if username == "your_username" and password == "your_password":
                return True

            # You can make an HTTP request here to validate credentials with an external service
            # For example:
            # response = requests.post(SOME_URL, data={"username": username, "password": password})
            # if response.status_code == 200:
            #     return True
            
            return False
        except Exception as e:
            _LOGGER.error(f"Error validating credentials: {e}")
            return False
