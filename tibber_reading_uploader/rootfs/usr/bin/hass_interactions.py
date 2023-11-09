import requests

class HASSInteractions:
    def __init__(self, supervisor_token: str):
        self.supervisor_token = supervisor_token
        self.headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "Content-Type": "application/json",
        }
        self.hass_url = "http://supervisor/core/api/states/"

    def get_state(self, entity_id: str) -> str:
        """Retrieve the state of a given entity from Home Assistant."""
        response = requests.get(f"{self.hass_url}{entity_id}", headers=self.headers)
        if response.status_code == 200:
            return response.json()['state']
        else:
            raise ValueError(f"Failed to get state for {entity_id}: {response.status_code}")

    def get_reading_date(self) -> str:
        """Get the current date and time from Home Assistant."""
        return self.get_state('sensor.date_time')
    
    def get_meter_reading(self, meter_sensor: str) -> float:
        """Get the meter reading from a specified sensor."""
        meter_reading = self.get_state(meter_sensor)
        return float(meter_reading)
