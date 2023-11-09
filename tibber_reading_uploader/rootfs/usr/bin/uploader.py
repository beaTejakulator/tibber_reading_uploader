# uploader.py
import requests
import logging
from datetime import datetime, timedelta

# Konfigurieren Sie das Logging mit einem einfacheren Format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',  # Hier entfernen wir den Logger-Namen und das Level
    datefmt='%Y-%m-%d %H:%M:%S'  # Sie können das Datum- und Zeitformat hier anpassen
)

logger = logging.getLogger(__name__)

class TibberUploader:
    def __init__(self, token, hass_interactions, meter_sensor):
        self.token = token
        self.hass_interactions = hass_interactions
        self.meter_sensor = meter_sensor

    def upload_reading(self):
        # Datum und Uhrzeit von Home Assistant abrufen
        reading_date = self.hass_interactions.get_reading_date()

        # Datum für gestern und heute berechnen
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Zählerstand vom angegebenen Sensor abrufen
        meter_reading = self.hass_interactions.get_meter_reading(self.meter_sensor)

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

        # Senden Sie die Anfrage an die Tibber API, um Account-Informationen zu erhalten
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

        # Senden Sie die Anfrage an die Tibber API
        tibber_mutation_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_mutation_data)
        if tibber_mutation_response.status_code != 200:
            return
        
        # Überprüfen Sie die API-Antwort und geben Sie die "descriptionHtml" aus, falls verfügbar
        tibber_response_data = tibber_mutation_response.json()
        success = tibber_response_data.get('data', {}).get('me', {}).get('addMeterReadings', {}).get('success', {})
        description_html = success.get('descriptionHtml')
        
        # Wenn "descriptionHtml" verfügbar ist, geben Sie es im Protokoll aus
        if description_html:
            logger.info(f"Tibber API-Antwort: {description_html}")
        
        # Wenn der Upload erfolgreich war, geben Sie eine Protokollmeldung aus
        if tibber_mutation_response.status_code == 200 and success:
            # Datum und Uhrzeit von Home Assistant abrufen
            reading_date = self.hass_interactions.get_reading_date()
            logger.info(f"Zählerstand ({rounded_value}) wurde am {reading_date} übermittelt")
        
        # Beenden Sie die Funktion, wenn die API-Antwort einen Statuscode ungleich 200 hat
        if tibber_mutation_response.status_code != 200:
            logger.error(f"Fehler beim Hochladen des Zählerstands: {tibber_mutation_response.text}")
            return
