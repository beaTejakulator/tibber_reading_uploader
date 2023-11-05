import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_METER_SENSOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Tibber Reading Uploader sensor from a config entry."""
    token = entry.data.get(CONF_TOKEN)
    meter_sensor = entry.data.get(CONF_METER_SENSOR)

    if token and meter_sensor:
        async_add_entities([TibberReadingUploaderSensor(hass, token, meter_sensor)])

class TibberReadingUploaderSensor(SensorEntity):
    """Representation of a Tibber Reading Uploader sensor."""

    def __init__(self, hass: HomeAssistant, token: str, meter_sensor: str):
        """Initialize the sensor."""
        self._hass = hass
        self._token = token
        self._meter_sensor = meter_sensor
        self._state = None

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
        # Get the meter reading from the selected sensor
        meter_sensor_state = self._hass.states.get(self._meter_sensor)
        if meter_sensor_state is None:
            _LOGGER.error("Meter sensor not found: %s", self._meter_sensor)
            return

        meter_reading = meter_sensor_state.state
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
        uploader = self._hass.data[DOMAIN]
        await uploader.upload_reading(meter_reading)
