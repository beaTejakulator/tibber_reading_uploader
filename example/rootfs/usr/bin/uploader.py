import logging
import os
import requests
from datetime import datetime, timedelta
from logger import setup_logging

# Logging konfigurieren
setup_logging()

_LOGGER = logging.getLogger(__name__)

class TibberUploader:
    def __init__(self, token: str, meter_id: str, register_id: str, meter_sensor: str):
        self.token = token
        self.meter_id = meter_id
        self.register_id = register_id
        self.meter_sensor = meter_sensor
        self.supervisor_token = os.getenv('SUPERVISOR_TOKEN')
        
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
    
            # Konvertieren Sie den Meterstand in eine Fließkommazahl und runden Sie ihn
            meter_reading_value = float(meter_reading)
            rounded_meter_reading = round(meter_reading_value)
            _LOGGER.info(f"Rounded meter reading to nearest whole number: {rounded_meter_reading}")
        else:
            _LOGGER.error(f"Failed to get meter reading from Home Assistant: {meter_reading_response.status_code} - {meter_reading_response.text}")
            return
    
        # Tibber API-Abfrage für "meterId" und "registerId"
        tibber_url = "https://app.tibber.com/v4/gql"
        tibber_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        tibber_data = {
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
                "value": rounded_meter_reading  # Verwenden Sie den gerundeten Wert
            },
        }
        
        # Senden Sie die Mutation-Anfrage an die Tibber API
        tibber_mutation_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_data)
        if tibber_mutation_response.status_code == 200:
            _LOGGER.info("Meter reading uploaded successfully")
        else:
            _LOGGER.error(f"Failed to upload meter reading: {tibber_mutation_response.status_code} - {tibber_mutation_response.text}")


        # Beispiel für das Abrufen der aktuellen Zeit von Home Assistant
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

        # Beispiel für das Abrufen des Zählerstands vom angegebenen Sensor
        meter_reading_url = f"http://supervisor/core/api/states/{self.meter_sensor}"
        meter_reading_response = requests.get(meter_reading_url, headers=headers)
        if meter_reading_response.status_code == 200:
            meter_reading = meter_reading_response.json()['state']
            _LOGGER.info(f"Meter reading retrieved: {meter_reading}")
            # Hier würden Sie den Wert verarbeiten und an Tibber senden
        else:
            _LOGGER.error(f"Failed to get meter reading from Home Assistant: {meter_reading_response.status_code} - {meter_reading_response.text}")
            return

        # Beispiel für das Senden des Zählerstands an Tibber
        tibber_url = "https://api.tibber.com/v1/gql"
        tibber_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        tibber_data = {
            # Hier würden Sie die Mutation für das Hochladen des Zählerstands einfügen
        }
        tibber_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_data)
        if tibber_response.status_code == 200:
            _LOGGER.info("Meter reading uploaded successfully")
        else:
            _LOGGER.error(f"Failed to upload meter reading: {tibber_response.status_code} - {tibber_response.text}")
