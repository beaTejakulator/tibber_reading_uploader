# Basisimage vom Add-on Build-Umfeld
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Locale
ENV LANG C.UTF-8

# Systempakete (schlank gehalten)
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash

# Python-Dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
 && rm -f /tmp/requirements.txt

# App-Skripte
COPY run.sh /run.sh
RUN chmod a+x /run.sh

# Python-App
COPY usr/bin/ /usr/bin/
RUN chmod a+x /usr/bin/*.py

# s6-Services (Start & Finish)
COPY rootfs/ /    # enthält /etc/services.d/tibber_reading_uploader/run + finish

# Standard-Command – s6 kümmert sich um Services; keine extra CMD nötig
