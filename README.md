
# Tibber Reading Uploader für Home Assistant

## Überblick
Der Tibber Reading Uploader ist ein Add-on für Home Assistant, das es ermöglicht, Energieverbrauchsdaten automatisch an Tibber zu senden. Dies ist besonders nützlich für Tibber-Kunden, die ihren Energieverbrauch in Echtzeit überwachen und optimieren möchten.

## Funktionsweise
Das Add-on liest die Verbrauchsdaten einer spezifizierten Entität, die den Stromzählerstand repräsentiert, und übermittelt diese Daten über die Tibber API an Tibber. Es nutzt die Home Assistant Services, um mit dem Home Assistant Supervisor zu interagieren und benötigt gültige Anmeldeinformationen für die Authentifizierung bei Tibber.

## Voraussetzungen
Ein Home Assistant-System mit Supervisor.
Gültige Tibber-Anmeldeinformationen (E-Mail und Passwort).
Eine Entität in Home Assistant, die den aktuellen Zählerstand des Stromzählers darstellt.

## Installation

 1. Fügen Sie dieses Repository zu Ihrem Home Assistant hinzu, indem Sie die URL https://github.com/beaTejakulator/tibber_reading_uploader verwenden.
 2. Installieren Sie das Add-on über die Home Assistant Add-on-Store-Schnittstelle.
 3. Konfigurieren Sie das Add-on mit den erforderlichen Umgebungsvariablen: 
 EMAIL
 PASSWORD
 METER_SENSOR.







[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FbeaTejakulator%2Ftibber_reading_uploader)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

## Konfiguration
Konfigurieren Sie das Add-on, indem Sie die folgenden Umgebungsvariablen in Home Assistant setzen:

 - EMAIL = Tibber Email 
 - PASSWORD = Tibber Passwort 
 - METER_SENSOR = Zähler (sensor)

## Nutzung
Nach der Installation und Konfiguration wird das Add-on automatisch die Verbrauchsdaten an Tibber senden, basierend auf dem Zählerstand, der von der angegebenen Entität bereitgestellt wird. Überprüfen Sie die Protokolle des Add-ons, um sicherzustellen, dass der Upload-Prozess erfolgreich gestartet wurde.

## Beitrag
Wenn Sie zum Projekt beitragen möchten, können Sie Pull Requests stellen oder Issues im GitHub-Repository eröffnen.

## Lizenz
Dieses Add-on ist unter der MIT-Lizenz veröffentlicht. Weitere Details finden Sie in der LICENSE-Datei im Repository.




[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
