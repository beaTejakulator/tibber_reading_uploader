import os
import logging
import socket
import time
from auth import get_tibber_token
from uploader import TibberUploader
from hass_interactions import HASSInteractions  # Sie benötigen HASSInteractions

# Konfigurieren Sie das Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False

MAX_RETRIES = 60  # Erhöht auf 60 Versuche
RETRY_DELAY = 5   # 5 Sekunden Verzögerung

if __name__ == "__main__":
    retries = 0
    while not is_connected() and retries < MAX_RETRIES:
        logger.info(f"Keine Internetverbindung. Warte {RETRY_DELAY} Sekunden... (Versuch {retries + 1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)
        retries += 1

    if not is_connected():
        logger.error("Fehler: Keine Internetverbindung nach mehreren Versuchen.")
        exit(1)

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
        logger.info("Upload-Prozess erfolgreich gestartet.")  # Meldung vor dem Start des Upload-Prozesses
        uploader.upload_reading()  # Upload-Prozess starten
    except Exception as e:
        logger.error(f"Fehler beim Starten des Upload-Prozesses: {e}")
        raise
