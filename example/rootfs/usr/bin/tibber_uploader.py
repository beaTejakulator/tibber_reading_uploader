#!/usr/bin/env python3

import logging
import aiohttp
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class TibberUploader:
    def __init__(self, hass: HomeAssistant, token: str, meter_id: str, register_id: str, meter_sensor: str):
        self.hass = hass
        self.token = token
        self.meter_id = meter_id
        self.register_id = register_id
        self.meter_sensor = meter_sensor

    async def upload_reading(self, reading: int):
        """Upload the meter reading to Tibber."""
        url = "https://app.tibber.com/v4/gql"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = {
            "query": """
                mutation AddMeterReadings($meterId: ID!, $readingDate: String!, $registerId: String!, $value: Int!) {
                    me {
                        addMeterReadings(
                            meterId: $meterId,
                            readingDate: $readingDate,
                            readings: [
                                {
                                    id: $registerId,
                                    value: $value
                                }
                            ]
                        ) {
                            success {
                                inputTitle
                                inputValue
                                title
                                descriptionHtml
                                doneButtonText
                            }
                            error {
                                statusCode
                                title
                                message
                            }
                        }
                    }
                }
            """,
            "variables": {
                "meterId": self.meter_id,
                "readingDate": self.hass.helpers.dt.now().isoformat(),
                "registerId": self.register_id,
                "value": reading,
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    _LOGGER.info("Meter reading uploaded successfully")
                else:
                    _LOGGER.error("Failed to upload meter reading: %s", response.status)
