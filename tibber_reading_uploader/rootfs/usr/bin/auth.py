import requests

def get_tibber_token(email: str, password: str) -> str:
    """
    Funktion, um den Token über eine API-Abfrage zu erhalten.
    
    Args:
        email (str): Die E-Mail-Adresse des Benutzers.
        password (str): Das Passwort des Benutzers.
    
    Returns:
        str: Der abgerufene Token.
    
    Raises:
        ValueError: Wenn die Authentifizierung fehlschlägt oder der Token nicht extrahiert werden kann.
    """
    auth_url = "https://app.tibber.com/v1/login.credentials"
    auth_data = {
        "email": email,
        "password": password
    }

    try:
        response = requests.post(auth_url, json=auth_data)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Authentifizierungsanfrage fehlgeschlagen: {e}")

    try:
        token = response.json().get('token')
        if not token:
            raise ValueError("Token konnte nicht aus der Antwort extrahiert werden.")
        return token
    except (ValueError, KeyError) as e:
        raise ValueError(f"Fehler beim Verarbeiten der Antwort: {e}")
