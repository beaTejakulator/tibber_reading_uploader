import logging
import sys

# Konfigurieren Sie das Logging, um auf die Standardausgabe zu schreiben
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log-Ausgabe auf stdout
    ]
)

_LOGGER = logging.getLogger(__name__)

def get_tibber_token(email: str, password: str) -> str:
    """
    Funktion, um den Token über eine API-Abfrage zu erhalten.
    """
    auth_url = "https://app.tibber.com/v1/login.credentials"
    auth_data = {
        "email": email,
        "password": password
    }
    response = requests.post(auth_url, json=auth_data)
    if response.status_code == 200:
        token = response.json().get('token')
        if token:
            _LOGGER.info("Token erfolgreich abgerufen.")
            return token
        else:
            _LOGGER.error("Token konnte nicht aus der Antwort extrahiert werden.")
            raise ValueError("Token konnte nicht aus der Antwort extrahiert werden.")
    else:
        _LOGGER.error(f"Authentifizierung fehlgeschlagen: {response.status_code} - {response.text}")
        raise ValueError(f"Authentifizierung fehlgeschlagen: {response.status_code} - {response.text}")
