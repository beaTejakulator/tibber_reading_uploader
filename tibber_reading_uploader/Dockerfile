# Verwenden Sie das Basisimage, das von der Build-Umgebung bereitgestellt wird
ARG BUILD_FROM
FROM $BUILD_FROM

# Setzen Sie Umgebungsvariablen
ENV LANG C.UTF-8

# Installieren Sie notwendige Pakete und Werkzeuge, einschließlich Cronie anstelle von Cron
RUN apk add --no-cache \
    udev \
    curl \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    cronie

# Installieren Sie Python-Module aus der requirements.txt-Datei
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt

# Installieren Sie Tempio für die Verwendung in Home Assistant Add-ons
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}" \
    && chmod a+x /usr/bin/tempio

# Kopieren Sie das rootfs-Verzeichnis in das Image
COPY rootfs /

# Kopieren Sie die Cron-Job-Datei in den Container
COPY mycron /etc/crontabs/root

# Stellen Sie sicher, dass das Startskript ausführbar ist
RUN chmod a+x /etc/services.d/tibber_reading_uploader/run

# Stellen Sie sicher, dass das Endskript ausführbar ist
RUN chmod a+x /etc/services.d/tibber_reading_uploader/finish

# Führen Sie den Cron-Daemon aus
CMD ["crond", "-n"]

