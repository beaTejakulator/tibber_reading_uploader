# /usr/bin/auth.py
import os

class MissingToken(Exception): pass

def get_tibber_token():
    token = os.getenv("TIBBER_TOKEN")
    if not token:
        raise MissingToken("Setze die Umgebungsvariable TIBBER_TOKEN im Add-on!")
    return token
