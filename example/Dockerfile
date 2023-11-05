# Verwenden Sie das offizielle Python-Image als Basis
FROM python:3.8

# Setzen Sie Umgebungsvariablen
ENV LANG C.UTF-8

# Setzen Sie das Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Installieren Sie Abhängigkeiten für Home Assistant Add-ons
RUN apt-get update && apt-get install -y \
    libudev-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopieren Sie die Anforderungsdatei und installieren Sie die Python-Abhängigkeiten
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie die Add-on-Quelldateien in das Arbeitsverzeichnis
COPY tibber_uploader.py ./
COPY sensor.py ./
COPY run.sh ./

# Setzen Sie die Berechtigungen für das Startskript
RUN chmod a+x /run.sh

# Definieren Sie das Startkommando
CMD [ "./run.sh" ]
