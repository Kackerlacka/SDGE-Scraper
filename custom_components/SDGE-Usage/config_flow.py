import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from . import DOMAIN
from .scraper import run_scraper  # Import the scraper function

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

        # Skip validation, just run the scraper and log the result
        try:
            data = await self.hass.async_add_executor_job(run_scraper, username, password)
            _LOGGER.debug(f"Scraped data: {data}")  # Log the scraped data for debugging

            # After running the scraper, create the config entry
            return self.async_create_entry(
                title=f"Gas Usage for {username}",
                data={CONF_USERNAME: username, CONF_PASSWORD: password},
            )
        except Exception as e:
            _LOGGER.error(f"Error running scraper: {e}")
            return self.async_abort(reason="scraper_error")

    def _get_schema(self):
        """Return the schema for user input."""
        return vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
