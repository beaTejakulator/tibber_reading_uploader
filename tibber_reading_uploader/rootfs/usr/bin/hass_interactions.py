#!/usr/bin/env python3
import os
import requests

class HassInteractions:
    def __init__(self):
        self.supervisor_token = os.getenv("SUPERVISOR_TOKEN")
        self.base_url = "http://supervisor/core/api"
        if not self.supervisor_token:
            raise RuntimeError("SUPERVISOR_TOKEN nicht verfügbar – läuft das als Add-on?")

    def get_meter_reading(self, entity_id: str) -> float:
        url = f"{self.base_url}/states/{entity_id}"
        headers = {"Authorization": f"Bearer {self.supervisor_token}"}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        state = data.get("state")
        if state in (None, "unknown", "unavailable", ""):
            raise ValueError(f"Entity {entity_id} hat keinen gültigen State: {state}")
        return float(state)

    def get_reading_date_iso(self) -> str:
        from datetime import datetime, timezone
        dt = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return dt.isoformat().replace("+00:00", "Z")
