import os
from auth import get_tibber_token
from uploader import TibberUploader

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
    meter_id = os.getenv('METER_ID')
    register_id = os.getenv('REGISTER_ID')
    meter_sensor = os.getenv('METER_SENSOR')

    # TibberUploader-Instanz erstellen und Ausführung starten
    uploader = TibberUploader(token, meter_id, register_id, meter_sensor)
    uploader.upload_reading()
