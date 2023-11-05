import logging
import os
import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_METER_SENSOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Tibber Reading Uploader sensor from a config entry."""
    token = entry.data.get(CONF_TOKEN)
    meter_sensor = entry.data.get(CONF_METER_SENSOR)

    if token and meter_sensor:
        async_add_entities([TibberReadingUploaderSensor(token, meter_sensor)])

class TibberReadingUploaderSensor(SensorEntity):
    """Representation of a Tibber Reading Uploader sensor."""

    def __init__(self, token: str, meter_sensor: str):
        """Initialize the sensor."""
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
        response = requests.get(hass_url, headers=headers)
        if response.status_code == 200:
            meter_sensor_state = response.json()
        else:
            _LOGGER.error("Failed to get meter sensor state: %s", response.status_code)
            return

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
        uploader.upload_reading(meter_reading)
