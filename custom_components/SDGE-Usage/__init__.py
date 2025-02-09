import logging
from datetime import timedelta
import os
import pandas as pd

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from .scraper import run_scraper  # Import the scraper function

_LOGGER = logging.getLogger(__name__)

DOMAIN = "sdge_usage"
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

    async def async_update(self):
        """Update the sensor state."""
        # Call the method to fetch the daily usage using the scraper
        self._state = await self.fetch_daily_usage()

    async def fetch_daily_usage(self):
        """Scrape the data and return the daily gas usage."""
        try:
            _LOGGER.info("Fetching gas usage data...")
            # Call the scraper's run_scraper function to get the latest data
            data = await self.hass.async_add_executor_job(run_scraper, self.username, self.password)

            # Extract the daily usage from the data
            if data is not None:
                # Assuming 'Consumed' is the column with the daily usage values
                daily_usage = data['Consumed'].iloc[-1]  # Get the last entry
                _LOGGER.info(f"Daily usage fetched: {daily_usage} kWh")
                return daily_usage
            else:
                return None
        except Exception as e:
            _LOGGER.error(f"Failed to fetch gas usage data: {e}")
            return None
