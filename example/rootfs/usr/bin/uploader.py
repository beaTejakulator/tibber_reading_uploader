#!/usr/bin/env python3

import os
import requests
from datetime import datetime, timedelta

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

        # Check if the METER_SENSOR environment variable is set
        if not self.meter_sensor:
            raise ValueError('The METER_SENSOR environment variable is not set.')

        # Check if the token is set
        if not self.token:
            raise ValueError('The TOKEN environment variable is not set.')

    def upload_reading(self):
        """Upload the meter reading to Tibber."""
        
        # Hier verwenden wir die Supervisor API, um die aktuelle Zeit von Home Assistant zu erhalten
        hass_url = "http://supervisor/core/api/states/sensor.date_time"
        headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(hass_url, headers=headers)
        if response.status_code != 200:
            return

        reading_date = response.json()['state']

        # Holen Sie den Zählerstand vom angegebenen Sensor
        meter_reading_url = f"http://supervisor/core/api/states/{self.meter_sensor}"
        meter_reading_response = requests.get(meter_reading_url, headers=headers)
        if meter_reading_response.status_code != 200:
            return

        meter_reading = meter_reading_response.json()['state']

        # Konvertieren Sie den Meterstand in eine Fließkommazahl und runden Sie ihn
        meter_reading_value = float(meter_reading)
        rounded_meter_reading = round(meter_reading_value)

        # Aktuelles Datum
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Datum von vor einem Tag
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

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
        if tibber_response.status_code != 200:
            return

        # Extrahieren Sie die meter_id und register_id dynamisch
        tibber_response_data = tibber_response.json()
        homes = tibber_response_data['data']['me']['homes']
        meters_items = tibber_response_data['data']['me']['meters']['items']
        
        # Angenommen, Sie möchten die meter_id und register_id des aktuellen Zählers extrahieren
        for home in homes:
            current_meter_id = home.get('currentMeter', {}).get('id')
            if current_meter_id:
                # Finden Sie das entsprechende Meter-Objekt in den Meter-Items
                for item in meters_items:
                    meter = item.get('meter')
                    if meter and meter.get('id') == current_meter_id:
                        # Angenommen, Sie möchten die erste Register-ID aus diesem Meter extrahieren
                        register_id = meter['registers'][0]['id']
                        # Setzen Sie die gefundenen IDs als Eigenschaften des Uploader-Objekts
                        self.meter_id = current_meter_id
                        self.register_id = register_id
                        break
                else:
                    break
            else:
                return  # Beenden Sie die Funktion, da kein weiterer Fortschritt möglich ist
        
        # Runden Sie den Wert, bevor Sie ihn hochladen
        rounded_value = round(float(meter_reading))

        # Now perform the mutation to add the meter reading
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
        tibber_mutation_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_mutation_data)
        if tibber_mutation_response.status_code != 200:
            return

if __name__ == "__main__":
    # Anmeldeinformationen aus Umgebungsvariablen lesen
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')

    # Überprüfen, ob Anmeldeinformationen vorhanden sind
    if not email or not password:
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
