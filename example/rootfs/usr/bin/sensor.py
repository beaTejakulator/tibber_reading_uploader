import logging
import os
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_METER_SENSOR
from .tibber_uploader import TibberUploader  # Stellen Sie sicher, dass diese Klasse existiert und importiert wird.

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Tibber Reading Uploader sensor from a config entry."""
    token = entry.data.get(CONF_TOKEN)
    meter_sensor = entry.data.get(CONF_METER_SENSOR)

    if token and meter_sensor:
        async_add_entities([TibberReadingUploaderSensor(hass, token, meter_sensor)])

class TibberReadingUploaderSensor(SensorEntity):
    """Representation of a Tibber Reading Uploader sensor."""

    def __init__(self, hass, token: str, meter_sensor: str):
        """Initialize the sensor."""
        self.hass = hass
        self._token = token
        self._meter_sensor = meter_sensor
        self._state = None
        self.supervisor_token = os.getenv('SUPERVISOR_TOKEN')

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Tibber Reading Uploader"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        # Get the meter reading from the selected sensor using Supervisor API
        hass_url = f"http://supervisor/core/api/states/{self._meter_sensor}"
        headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "Content-Type": "application/json",
        }
        
        session = async_get_clientsession(self.hass)
        async with session.get(hass_url, headers=headers) as response:
            if response.status == 200:
                meter_sensor_state = await response.json()
                meter_reading = meter_sensor_state['state']
                if meter_reading is None:
                    _LOGGER.error("Meter reading is None")
                    return

                # Convert meter reading to float
                try:
                    meter_reading = float(meter_reading)
                except ValueError:
                    _LOGGER.error("Invalid meter reading: %s", meter_reading)
                    return

                # Send the meter reading to Tibber
                uploader = TibberUploader(self._token, meter_sensor_state['attributes']['meter_id'], meter_sensor_state['attributes']['register_id'], self._meter_sensor)
                await uploader.upload_reading(meter_reading)  # Stellen Sie sicher, dass diese Methode asynchron ist.
            else:
                _LOGGER.error("Failed to get meter sensor state: %s", response.status)
