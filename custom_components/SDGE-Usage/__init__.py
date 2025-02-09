import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity

# Import your scraper class
from .scraper import Scraper  # Assuming scraper.py is in the same directory

_LOGGER = logging.getLogger(__name__)

DOMAIN = "sdge_usage"  # Ensure this matches your config flow and other files
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
    
    # Initialize the scraper
    scraper = Scraper(username, password)

    # Start the scraper task asynchronously
    hass.loop.create_task(scraper.run())  # Make sure scraper.run() is an async method

    # Register the sensor platform directly without discovery
    hass.helpers.entity_component.async_add_entities(
        [GasUsageSensor(hass, scraper)], update_before_add=True
    )

    return True


class GasUsageSensor(Entity):
    """Representation of a Gas Usage Sensor."""

    def __init__(self, hass, scraper: Scraper):
        """Initialize the sensor."""
        self.hass = hass
        self.scraper = scraper  # Store the scraper instance
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Gas Usage - {self.scraper.username}"

    @property
    def state(self):
        """Return the state of the sensor (daily usage)."""
        return self._state

    def update(self):
        """Update the sensor state."""
        # Call the scraper to fetch the daily usage
        self._state = self.scraper.fetch_daily_usage()

    def fetch_daily_usage(self):
        """Fetch the daily gas usage data."""
        try:
            _LOGGER.info("Fetching gas usage data...")
            return self.scraper.fetch_daily_usage()  # Use the scraper's method to fetch data
        except Exception as e:
            _LOGGER.error(f"Failed to fetch gas usage data: {e}")
            return None
