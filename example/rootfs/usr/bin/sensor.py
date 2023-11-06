import logging
import os
import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_METER_SENSOR
from .tibber_uploader import TibberUploader

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
        # Verify METER_SENSOR environment variable
        if not self._meter_sensor:
            _LOGGER.error('The METER_SENSOR environment variable is not set.')
            return

        # Check if the sensor is correctly configured in Home Assistant
        hass_url = f'http://supervisor/core/api/states/{self._meter_sensor}'
        headers = {
            'Authorization': f'Bearer {self.supervisor_token}',
            'Content-Type': 'application/json',
        }

        session = async_get_clientsession(self.hass)
        async with session.get(hass_url, headers=headers) as response:
            if response.status == 200:
                _LOGGER.info(f'Sensor {self._meter_sensor} is correctly configured in Home Assistant.')
                meter_sensor_state = await response.json()
                meter_reading = meter_sensor_state['state']
                # Rest of the code...
            else:
                _LOGGER.error(f'Failed to access sensor {self._meter_sensor} in Home Assistant. Status code: {response.status}')
                return

        # Rest of the async_update method...
