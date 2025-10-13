# /usr/bin/main.py (relevanter Teil)
import os, requests, json
from auth import get_tibber_token

GQL_URL = "https://api.tibber.com/v1-beta/gql"

def gql(query, variables=None):
    token = get_tibber_token()
    r = requests.post(
        GQL_URL,
        json={"query": query, "variables": variables or {}},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]
