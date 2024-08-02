import requests
import logging
from datetime import datetime, timedelta

# Konfigurieren Sie das Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TibberUploader:
    def __init__(self, token, hass_interactions, meter_sensor):
        self.token = token
        self.hass_interactions = hass_interactions
        self.meter_sensor = meter_sensor
        self.meter_id = None
        self.register_id = None

    def get_account_info(self, from_date, to_date):
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
                "readingsFromDate": from_date,
                "readingsToDate": to_date
            },
        }
        response = requests.post(tibber_url, headers=tibber_headers, json=tibber_data)
        response.raise_for_status()
        return response.json()

    def extract_meter_info(self, account_info):
        if not account_info or 'data' not in account_info:
            raise ValueError("Keine gültigen Account-Informationen erhalten.")

        me = account_info['data'].get('me', {})
        homes = me.get('homes', [])
        meters_items = me.get('meters', {}).get('items', [])
        
        for home in homes:
            current_meter = home.get('currentMeter')
            if current_meter:
                current_meter_id = current_meter.get('id')
                if current_meter_id:
                    for item in meters_items:
                        meter = item.get('meter')
                        if meter and meter.get('id') == current_meter_id:
                            self.meter_id = current_meter_id
                            if 'registers' in meter and len(meter['registers']) > 0:
                                self.register_id = meter['registers'][0]['id']
                            if not self.register_id:
                                raise ValueError("Kein gültiger Register-ID gefunden.")
                            return
        raise ValueError("Konnte keine gültige meter_id oder register_id finden.")

    def upload_reading(self):
        reading_date = self.hass_interactions.get_reading_date()
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        current_date = datetime.now().strftime("%Y-%m-%d")

        meter_reading = self.hass_interactions.get_meter_reading(self.meter_sensor)

        try:
            account_info = self.get_account_info(yesterday_date, current_date)
            self.extract_meter_info(account_info)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Account-Informationen: {e}")
            return

        rounded_value = round(float(meter_reading))

        tibber_url = "https://app.tibber.com/v4/gql"
        tibber_headers = {
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
                "value": rounded_value
            },
        }

        try:
            tibber_mutation_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_mutation_data)
            tibber_mutation_response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Fehler beim Hochladen des Zählerstands: {e}")
            return
        
        response_data = tibber_mutation_response.json()
        success = response_data.get('data', {}).get('me', {}).get('addMeterReadings', {}).get('success')
        
        if success is not None:
            description_html = success.get('descriptionHtml')
            if description_html:
                logger.info(f"Tibber API-Antwort: {description_html}")
        
            logger.info(f"Zählerstand ({rounded_value}) wurde am {reading_date} übermittelt")
        else:
            logger.warning("Keine erfolgreiche Antwort von Tibber erhalten oder unerwartetes Antwortformat.")
