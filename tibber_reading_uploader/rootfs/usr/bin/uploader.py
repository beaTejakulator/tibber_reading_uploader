#!/usr/bin/env python3
import logging
import requests

GQL_URL = "https://api.tibber.com/v1-beta/gql"
logger = logging.getLogger(__name__)

class TibberUploader:
    MUTATION = """
    mutation ($input: SendMeterReadingInput!) {
      sendMeterReading(input: $input) {
        accepted
        reason
      }
    }
    """

    def __init__(self, token: str, hass_interactions, meter_sensor: str,
                 home_id: str | None = None,
                 meter_id: str | None = None,
                 register_id: str | None = None):
        self.token = token
        self.hass = hass_interactions
        self.meter_sensor = meter_sensor
        self.home_id = home_id or ""
        self.meter_id = meter_id or ""
        self.register_id = register_id or ""

    def _gql(self, query: str, variables: dict | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        r = requests.post(GQL_URL, headers=headers, json={"query": query, "variables": variables or {}}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            raise RuntimeError(data["errors"])
        return data["data"]

    def sanity_check(self):
        data = self._gql("{ viewer { name homes { id address { city } } } }")
        viewer = data.get("viewer", {})
        homes = viewer.get("homes", [])
        logger.info("Eingeloggt als: %s", viewer.get("name"))
        if homes:
            logger.info("Homes: %s", ", ".join(h["id"] for h in homes))
        else:
            logger.warning("Keine Homes gefunden.")
        if not self.home_id and homes:
            self.home_id = homes[0]["id"]
            logger.info("HOME_ID nicht gesetzt – verwende erstes Home: %s", self.home_id)

    def upload_reading(self):
        # 1) Token/Home sanity
        self.sanity_check()

        # 2) Messwert & Zeitstempel
        value = float(self.hass.get_meter_reading(self.meter_sensor))
        ts_iso = self.hass.get_reading_date_iso()

        # 3) Input-Objekt zusammenstellen (je nach Konfig)
        input_obj = {"value": value, "timestamp": ts_iso}
        if self.meter_id and self.register_id:
            input_obj.update({"meterId": self.meter_id, "registerId": self.register_id})
            logger.info("Sende Lesung (%.3f) via meterId/registerId…", value)
        elif self.home_id:
            input_obj.update({"homeId": self.home_id})
            logger.info("Sende Lesung (%.3f) via homeId…", value)
        else:
            raise ValueError("Weder (METER_ID & REGISTER_ID) noch HOME_ID vorhanden.")

        data = self._gql(self.MUTATION, {"input": input_obj})
        out = data.get("sendMeterReading", {})
        if out.get("accepted"):
            logger.info("✅ Zählerstand akzeptiert (%.3f @ %s).", value, ts_iso)
        else:
            logger.warning("⚠️ Nicht akzeptiert: %s", out)
