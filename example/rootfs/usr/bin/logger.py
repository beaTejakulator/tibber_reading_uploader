import logging
import sys

def setup_logging():
    # Konfigurieren Sie das Logging, um auf die Standardausgabe zu schreiben
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Log-Ausgabe auf stdout
        ]
    )
