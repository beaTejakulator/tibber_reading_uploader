import os
from auth import get_tibber_token
from uploader import TibberUploader
import logging

# Konfigurieren Sie das Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Anmeldeinformationen aus Umgebungsvariablen lesen
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')

    # Überprüfen, ob Anmeldeinformationen vorhanden sind
    if not email or not password:
        logger.error("Die Anmeldeinformationen für Tibber sind nicht gesetzt.")
        raise ValueError("Die Anmeldeinformationen für Tibber sind nicht gesetzt.")

    # Token abrufen
    try:
        token = get_tibber_token(email, password)
        logger.info("Token erfolgreich abgerufen.")
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Tokens: {e}")
        raise

    # Umgebungsvariablen für die restlichen Parameter lesen
    meter_id = os.getenv('METER_ID')
    register_id = os.getenv('REGISTER_ID')
    meter_sensor = os.getenv('METER_SENSOR')

    # TibberUploader-Instanz erstellen und Ausführung starten
    try:
        uploader = TibberUploader(token, meter_id, register_id, meter_sensor)
        uploader.upload_reading()
        logger.info("Upload-Prozess erfolgreich gestartet.")
    except Exception as e:
        logger.error(f"Fehler beim Starten des Upload-Prozesses: {e}")
        raise

