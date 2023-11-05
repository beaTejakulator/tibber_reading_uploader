# Verwenden Sie das offizielle Python-Image als Basis
FROM python:3.8

# Setzen Sie Umgebungsvariablen
ENV LANG C.UTF-8

# Installieren Sie Abhängigkeiten für Home Assistant Add-ons
RUN apt-get update && apt-get install -y \
    libudev-dev \
    && rm -rf /var/lib/apt/lists/*

# Installieren Sie die erforderlichen Python-Pakete
RUN pip install --no-cache-dir requests aiohttp

# Kopieren Sie die Add-on-Quelldateien in den Container
COPY tibber_uploader.py /tibber_uploader.py
COPY sensor.py /sensor.py
COPY run.sh /run.sh

# Setzen Sie die Berechtigungen für das Startskript
RUN chmod a+x /run.sh

# Definieren Sie das Startkommando
CMD [ "/run.sh" ]
