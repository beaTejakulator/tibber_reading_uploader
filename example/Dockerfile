# Verwenden Sie das Basisimage, das von der Build-Umgebung bereitgestellt wird
ARG BUILD_FROM
FROM $BUILD_FROM

# Setzen Sie Umgebungsvariablen
ENV LANG C.UTF-8

# Installieren Sie notwendige Pakete und Werkzeuge
RUN apk add --no-cache \
    udev \
    curl \
    python3 \
    py3-pip

# Installieren Sie Tempio für die Verwendung in Home Assistant Add-ons
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}" \
    && chmod a+x /usr/bin/tempio

# Kopieren Sie das rootfs-Verzeichnis in das Image
COPY rootfs /

# Stellen Sie sicher, dass das Startskript ausführbar ist
RUN chmod a+x /etc/services.d/example/run

# Definieren Sie das Startkommando
CMD [ "/etc/services.d/example/run" ]
