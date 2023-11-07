import os
import logging
from auth import get_tibber_token
from uploader import TibberUploader
from hass_interactions import HASSInteractions  # Sie benötigen HASSInteractions

# Konfigurieren Sie das Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Anmeldeinformationen aus Umgebungsvariablen lesen
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    supervisor_token = os.getenv('SUPERVISOR_TOKEN')  # Umgebungsfaktor für HASSInteractions

    # Überprüfen, ob Anmeldeinformationen vorhanden sind
    if not email or not password or not supervisor_token:
        logger.error("Die Anmeldeinformationen oder Konfigurationen sind nicht korrekt gesetzt.")
        raise ValueError("Die Anmeldeinformationen oder Konfigurationen sind nicht korrekt gesetzt.")

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

    # HASSInteractions-Instanz erstellen
    hass_interactions = HASSInteractions(supervisor_token)

    # TibberUploader-Instanz erstellen und Ausführung starten
    try:
        uploader = TibberUploader(token, hass_interactions, meter_sensor)  # Hier den meter_sensor übergeben
        uploader.upload_reading()
        logger.info("Upload-Prozess erfolgreich gestartet.")
    except Exception as e:
        logger.error(f"Fehler beim Starten des Upload-Prozesses: {e}")
        raise
