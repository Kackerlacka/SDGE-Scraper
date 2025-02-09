import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from . import DOMAIN
from .scraper import run_scraper  # Import the scraper function to validate credentials

_LOGGER = logging.getLogger(__name__)

class GasUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SDGE Usage Integration."""

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

        # Validate the username and password by scraping a test page
        if not await self._validate_credentials(username, password):
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

    async def _validate_credentials(self, username, password):
        """Validate the credentials by attempting to scrape data."""
        try:
            # Attempt to scrape data using the provided credentials
            data = await self.hass.async_add_executor_job(run_scraper, username, password)

            # Check if data was returned successfully
            if data is not None and not data.empty:  # Ensure data is valid (not None and not empty)
                _LOGGER.info("Credentials are valid!")
                return True
            else:
                _LOGGER.error("Failed to fetch data using provided credentials.")
                return False

        except Exception as e:
            # If an error occurs during scraping (e.g., invalid credentials or connection error)
            _LOGGER.error(f"Error validating credentials: {e}")
            return False
