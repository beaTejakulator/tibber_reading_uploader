#!/usr/bin/env python3

import logging
import os
import requests
import time
from datetime import datetime, timedelta

# Konfigurieren Sie das Logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

# Funktion, um den Token über eine API-Abfrage zu erhalten
def get_tibber_token(email: str, password: str) -> str:
    auth_url = "https://app.tibber.com/v1/login.credentials"
    auth_data = {
        "email": email,
        "password": password
    }
    response = requests.post(auth_url, json=auth_data)
    if response.status_code == 200:
        token = response.json().get('token')
        if token:
            return token
        else:
            raise ValueError("Token konnte nicht aus der Antwort extrahiert werden.")
    else:
        raise ValueError(f"Authentifizierung fehlgeschlagen: {response.status_code} - {response.text}")

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

        # Debugging statement to print the token value
        print(f'Debug: TOKEN={self.token}')

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

            # Konvertieren Sie den Meterstand in eine Fließkommazahl und runden Sie ihn
            meter_reading_value = float(meter_reading)
            rounded_meter_reading = round(meter_reading_value)
            _LOGGER.info(f"Rounded meter reading to nearest whole number: {rounded_meter_reading}")
        else:
            _LOGGER.error(f"Failed to get meter reading from Home Assistant: {meter_reading_response.status_code} - {meter_reading_response.text}")
            return

        # Aktuelles Datum
        current_date = datetime.now().strftime('%Y-%m-%d')
        _LOGGER.info(f"Current date: {current_date}")
        
        # Datum von vor einem Tag
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        _LOGGER.info(f"Yesterday's date: {yesterday_date}")

        # Tibber API-Abfrage für "meterId" und "registerId"
        tibber_url = "https://app.tibber.com/v4/gql"
        tibber_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        tibber_data = {
            "query": """
                query AccountInfo($readingsFromDate: String!, $readingsToDate: String!) {
                    me {
                        id
                        firstName
                        lastName
                        email
                        meters {
                            items {
                                meter {
                                    id
                                    title
                                    description
                                    registers {
                                        id
                                    }
                                }
                            }
                        }
                        homes {
                            id
                            address {
                                addressText
                                city
                                postalCode
                                country
                            }
                            currentMeter {
                                id
                                meterNo
                                isUserRead
                            }
                            consumptionAnalysisItemsForUserReadMeter(from: $readingsFromDate, to: $readingsToDate, useDemoData: false) {
                                from
                                to
                                meterReadingForCurrentMonthIsRecommended
                                meterReadingForPreviousMonthIsRecommended
                                meterReadings {
                                    date
                                    registers {
                                        value
                                    }
                                }
                            }
                        }
                    }
                }
            """,
            "variables": {
                "readingsFromDate": yesterday_date,
                "readingsToDate": current_date
            },
        }

        # Senden Sie die Anfrage an die Tibber API
        tibber_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_data)
        if tibber_response.status_code == 200:
            _LOGGER.info("Data successfully fetched from Tibber API")
            tibber_response_data = tibber_response.json()
            
            # Extrahieren Sie die meter_id und register_id dynamisch
            homes = tibber_response_data['data']['me']['homes']
            meters_items = tibber_response_data['data']['me']['meters']['items']
            
            # Angenommen, Sie möchten die meter_id und register_id des aktuellen Zählers extrahieren
            for home in homes:
                current_meter_id = home.get('currentMeter', {}).get('id')
                if current_meter_id:
                    _LOGGER.info(f"Found current meter_id: {current_meter_id}")
                    # Finden Sie das entsprechende Meter-Objekt in den Meter-Items
                    for item in meters_items:
                        meter = item.get('meter')
                        if meter and meter.get('id') == current_meter_id:
                            # Angenommen, Sie möchten die erste Register-ID aus diesem Meter extrahieren
                            register_id = meter['registers'][0]['id']
                            _LOGGER.info(f"Found register_id: {register_id}")
                            # Setzen Sie die gefundenen IDs als Eigenschaften des Uploader-Objekts
                            self.meter_id = current_meter_id
                            self.register_id = register_id
                            break
                    else:
                        _LOGGER.error(f"No meter found for current meter_id: {current_meter_id}")
                    break
            else:
                _LOGGER.error("No current meter_id found in homes")
                return  # Beenden Sie die Funktion, da kein weiterer Fortschritt möglich ist
        
            # Runden Sie den Wert, bevor Sie ihn hochladen
            rounded_value = round(float(meter_reading))

            
            time.sleep(2)  # Fügen Sie eine Verzögerung von 2 Sekunden hinzu

            
            # Now perform the mutation to add the meter reading
            tibber_mutation_url = "https://app.tibber.com/v4/gql"
            tibber_mutation_headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
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
                    "value": rounded_value  # Verwenden Sie den gerundeten Wert
                },
            }
            
            # Senden Sie die Mutation-Anfrage an die Tibber API
            tibber_mutation_response = requests.post(tibber_mutation_url, headers=tibber_mutation_headers, json=tibber_mutation_data)
            if tibber_mutation_response.status_code == 200:
                _LOGGER.info("Meter reading uploaded successfully")
            else:
                _LOGGER.error(f"Failed to upload meter reading: {tibber_mutation_response.status_code} - {tibber_mutation_response.text}")
        else:
            _LOGGER.error(f"Failed to fetch data from Tibber API: {tibber_response.status_code} - {tibber_response.text}")

if __name__ == "__main__":
    # Anmeldeinformationen aus Umgebungsvariablen lesen
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')

    # Überprüfen, ob Anmeldeinformationen vorhanden sind
    if not email or not password:
        _LOGGER.error("Die Anmeldeinformationen für Tibber sind nicht gesetzt.")
        raise ValueError("Die Anmeldeinformationen für Tibber sind nicht gesetzt.")

    # Token abrufen
    token = get_tibber_token(email, password)

    # Umgebungsvariablen für die restlichen Parameter lesen
    meter_id = os.getenv('METER_ID')  # Wenn Sie auch meter_id konfigurieren möchten
    register_id = os.getenv('REGISTER_ID')  # Liest die register_id aus der Umgebung
    meter_sensor = os.getenv('METER_SENSOR')

    # TibberUploader-Instanz erstellen und Ausführung starten
    uploader = TibberUploader(token, meter_id, register_id, meter_sensor)
    uploader.upload_reading()
