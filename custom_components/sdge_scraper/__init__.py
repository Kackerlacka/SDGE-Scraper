import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gas_usage"  # Ensure this matches your config flow and other files
SCAN_INTERVAL = timedelta(hours=24)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SDGE Usage Integration."""
    _LOGGER.info("Setting up SDGE Usage Integration")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SDGE Usage from a config entry."""
    _LOGGER.info("Setting up SDGE Usage from config entry")
    
    # Retrieve username and password from config entry data
    username = entry.data["username"]
    password = entry.data["password"]
    
    # Store the username and password in hass data for use by the sensor
    hass.data[DOMAIN] = {"username": username, "password": password}
    
    # Register the sensor platform directly without discovery
    hass.helpers.entity_component.async_add_entities(
        [GasUsageSensor(hass, username, password)], update_before_add=True
    )

    return True


class GasUsageSensor(Entity):
    """Representation of a Gas Usage Sensor."""

    def __init__(self, hass, username, password):
        """Initialize the sensor."""
        self.hass = hass
        self.username = username
        self.password = password
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Gas Usage - {self.username}"

    @property
    def state(self):
        """Return the state of the sensor (daily usage)."""
        return self._state

    def update(self):
        """Update the sensor state."""
        # Call the method to fetch the daily usage (you should implement the scraping logic)
        self._state = self.fetch_daily_usage()

    def fetch_daily_usage(self):
        """Scrape the data and return the daily gas usage."""
        try:
            _LOGGER.info("Fetching gas usage data...")
            # Example: Sending login request and fetching data
            # response = requests.post(url, data={'username': self.username, 'password': self.password})
            # Parse the fetched data
            # For now, returning a dummy value
            return 1.03  # Example daily consumption value in your case
        except Exception as e:
            _LOGGER.error(f"Failed to fetch gas usage data: {e}")
            return None
