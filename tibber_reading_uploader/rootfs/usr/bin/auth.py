import requests

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
            return token
        else:
            raise ValueError("Token konnte nicht aus der Antwort extrahiert werden.")
    else:
        raise ValueError(f"Authentifizierung fehlgeschlagen: {response.status_code} - {response.text}")
