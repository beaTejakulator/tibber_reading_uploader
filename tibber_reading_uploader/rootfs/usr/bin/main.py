#!/usr/bin/env python3
import os
import logging
from auth import get_tibber_token
from hass_interactions import HassInteractions
from tibber_uploader import TibberUploader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def env_get(name: str, default: str = "") -> str:
    v = os.getenv(name, default)
    return v if v is not None else default

def main():
    token = get_tibber_token()

    meter_sensor = env_get("METER_SENSOR")
    if not meter_sensor:
        raise SystemExit("METER_SENSOR ist nicht gesetzt.")

    home_id = env_get("HOME_ID", "")
    meter_id = env_get("METER_ID", "")
    register_id = env_get("REGISTER_ID", "")

    hass = HassInteractions()
    uploader = TibberUploader(
        token=token,
        hass_interactions=hass,
        meter_sensor=meter_sensor,
        home_id=home_id or None,
        meter_id=meter_id or None,
        register_id=register_id or None,
    )
    uploader.upload_reading()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Fehler: %s", e)
        raise
