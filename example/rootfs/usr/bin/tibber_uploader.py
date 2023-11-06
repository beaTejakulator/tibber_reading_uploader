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
        print(f'Debug: METER_SENSOR={self.meter_sensor}')

        # Check if the METER_SENSOR environment variable is set
        if not self.meter_sensor:
            _LOGGER.error('The METER_SENSOR environment variable is not set.')
            raise ValueError('The METER_SENSOR environment variable is not set.')

        # Debugging statement to print the token value
        print(f'Debug: TOKEN={self.token}')

        # Check if the METER_SENSOR environment variable is set
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
        
        tibber_response = requests.post(tibber_url, headers=tibber_headers, json=tibber_data)
        if tibber_response.status_code == 200:
            _LOGGER.info("Data successfully fetched from Tibber API")

            # Extract meter and register IDs from the Tibber response
            tibber_response_data = tibber_response.json()
            meters_items = tibber_response_data['data']['me']['meters']['items']
            for item in meters_items:
                if item['meter']['id'] == self.meter_id:
                    meter = item['meter']
                    for register in meter['registers']:
                        if register['id'] == self.register_id:
                            # Found the correct register, no need to continue
                            break
                    else:
                        _LOGGER.error(f"No register with id {self.register_id} found for meter {self.meter_id}")
                        return
                    break
            else:
                _LOGGER.error(f"No meter with id {self.meter_id} found")
                return
            _LOGGER.info(f"Meter and register IDs confirmed: {self.meter_id}, {self.register_id}")

            # Now perform the mutation to add the meter reading
            tibber_mutation_url = "https://app.tibber.com/v4/gql"
            tibber_mutation_data = {
                "query": """
                    mutation AddMeterReadings($meterId: ID!, $readingDate: String!, $registerId: String!, $value: Float!) {
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
                    "value": float(meter_reading),  # Convert the reading to float
                },
            }

            # Send the mutation request to Tibber
            tibber_mutation_response = requests.post(tibber_mutation_url, headers=tibber_headers, json=tibber_mutation_data)
            if tibber_mutation_response.status_code == 200:
                _LOGGER.info("Meter reading uploaded successfully")
            else:
                _LOGGER.error(f"Failed to upload meter reading: {tibber_mutation_response.status_code} - {tibber_mutation_response.text}")

        else:
            _LOGGER.error(f"Failed to get a successful response from Tibber API. Status code: {tibber_response.status_code}")
            return

if __name__ == "__main__":
    # Hier sollten Sie die Werte durch die tatsächlichen Werte ersetzen, die Sie verwenden möchten
    token = os.getenv('TOKEN')
    meter_id = os.getenv('METER_ID')
    register_id = os.getenv('REGISTER_ID')
    meter_sensor = os.getenv('METER_SENSOR')

    uploader = TibberUploader(token, meter_id, register_id, meter_sensor)
    uploader.upload_reading()
