#!/usr/bin/env python3

import logging
import os
import requests

# Konfigurieren Sie das Logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

class TibberUploader:
    def __init__(self, token: str, meter_id: str, register_id: str, meter_sensor: str):
        self.token = token
        self.meter_id = meter_id
        self.register_id = register_id
        self.meter_sensor = meter_sensor
        self.supervisor_token = os.getenv('SUPERVISOR_TOKEN')

        # Debugging statement to print the METER_SENSOR value
        print(f'Debug: METER_SENSOR={self.meter_sensor}')

        # Check if the METER_SENSOR environment variable is set
        if not self.meter_sensor:
            _LOGGER.error('The METER_SENSOR environment variable is not set.')
            raise ValueError('The METER_SENSOR environment variable is not set.')

    def upload_reading(self):
        """Upload the meter reading to Tibber."""
        _LOGGER.info("Starting the upload process...")
        
        # Hier verwenden wir die Supervisor API, um die aktuelle Zeit von Home Assistant zu erhalten
        hass_url = "http://supervisor/core/api/states/sensor.date_time"
        headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(hass_url, headers=headers)
        if response.status_code == 200:
            reading_date = response.json()['state']
            _LOGGER.info(f"Current time from Home Assistant retrieved: {reading_date}")
        else:
            _LOGGER.error(f"Failed to get current time from Home Assistant: {response.status_code} - {response.text}")
            return

        # Holen Sie den Zählerstand vom angegebenen Sensor
        meter_reading_url = f"http://supervisor/core/api/states/{self.meter_sensor}"
        meter_reading_response = requests.get(meter_reading_url, headers=headers)
        if meter_reading_response.status_code == 200:
            meter_reading = meter_reading_response.json()['state']
            _LOGGER.info(f"Meter reading retrieved: {meter_reading}")
        else:
            _LOGGER.error(f"Failed to get meter reading from Home Assistant: {meter_reading_response.status_code} - {meter_reading_response.text}")
            return

        # Jetzt führen wir die Mutation auf der Tibber API durch
        tibber_url = "https://api.tibber.com/v1-beta/gql"
        tibber_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        tibber_data = {
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
                "readingDate": reading_date,
                "registerId": self.register_id,
                "value": int(meter_reading),  # Konvertieren Sie den Zählerstand in einen Integer
            },
        }

        tibber_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_data)
        if tibber_response.status_code == 200:
            _LOGGER.info("Meter reading uploaded successfully")
        else:
            _LOGGER.error(f"Failed to upload meter reading: {tibber_response.status_code} - {tibber_response.text}")

if __name__ == "__main__":
    # Hier sollten Sie die Werte durch die tatsächlichen Werte ersetzen, die Sie verwenden möchten
    token = os.getenv('TIBBER_TOKEN')
    meter_id = os.getenv('METER_ID')
    register_id = os.getenv('REGISTER_ID')
    meter_sensor = os.getenv('METER_SENSOR')

    # Debugging statement to print the METER_SENSOR value
    print(f'Debug: METER_SENSOR={meter_sensor}')

    # Check if the METER_SENSOR environment variable is set
    if not meter_sensor:
        _LOGGER.error('The METER_SENSOR environment variable is not set.')
        raise ValueError('The METER_SENSOR environment variable is not set.')

    uploader = TibberUploader(token, meter_id, register_id, meter_sensor)
    uploader.upload_reading()
