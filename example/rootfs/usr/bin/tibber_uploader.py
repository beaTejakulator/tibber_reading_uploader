#!/usr/bin/env python3

import logging
import os
import requests
from datetime import datetime, timedelta

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
        _LOGGER.debug(f'Debug: METER_SENSOR={self.meter_sensor}')

        # Check if the METER_SENSOR environment variable is set
        if not self.meter_sensor:
            _LOGGER.error('The METER_SENSOR environment variable is not set.')
            raise ValueError('The METER_SENSOR environment variable is not set.')

        # Debugging statement to print the token value
        _LOGGER.debug(f'Debug: TOKEN={self.token}')

        # Check if the token is set
        if not self.token:
            _LOGGER.error('The TOKEN environment variable is not set.')
            raise ValueError('The TOKEN environment variable is not set.')

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

        # Aktuelles Datum
        current_date = datetime.now().strftime('%Y-%m-%d')
        _LOGGER.info(f"Current date: {current_date}")
        
        # Datum von gestern
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        _LOGGER.info(f"Yesterday's date: {yesterday_date}")

        # Now perform the mutation to add the meter reading
        tibber_mutation_url = "https://app.tibber.com/v4/gql"
        tibber_mutation_data = {
            "query": """
                mutation AddMeterReadings($meterId: String!, $readingDate: String!, $registerId: String!, $value: Float!) {
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
                "value": float(meter_reading)
            },
        }
        
        # Debug-Ausgabe für die gesendeten Daten
        _LOGGER.debug(f"Sending mutation to Tibber API with data: {tibber_mutation_data}")

        # Senden Sie die Mutation-Anfrage an die Tibber API
        tibber_mutation_response = requests.post(tibber_mutation_url, headers=tibber_headers, json=tibber_mutation_data)
        if tibber_mutation_response.status_code == 200:
            _LOGGER.info("Meter reading uploaded successfully")
            # Hier fügen wir die Ausgabe der vollständigen Antwort hinzu
            _LOGGER.info(f"Full response from Tibber API: {tibber_mutation_response.json()}")
        else:
            _LOGGER.error(f"Failed to upload meter reading: {tibber_mutation_response.status_code} - {tibber_mutation_response.text}")
            # Hier fügen wir auch die Ausgabe der vollständigen Fehlerantwort hinzu
            _LOGGER.error(f"Full error response from Tibber API: {tibber_mutation_response.json()}")

if __name__ == "__main__":
    # Hier sollten Sie die Werte durch die tatsächlichen Werte ersetzen, die Sie verwenden möchten
    token = os.getenv('TOKEN')
    meter_id = os.getenv('METER_ID')  # Wenn Sie auch meter_id konfigurieren möchten
    register_id = os.getenv('REGISTER_ID')  # Liest die register_id aus der Umgebung
    meter_sensor = os.getenv('METER_SENSOR')

    uploader = TibberUploader(token, meter_id, register_id, meter_sensor)
    uploader.upload_reading()
