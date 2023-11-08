# Tibber Reading Uploader für Home Assistant

## Überblick
Der Tibber Reading Uploader ist ein Add-on für Home Assistant, das es ermöglicht, Energieverbrauchsdaten automatisch an Tibber zu senden. Dies ist besonders nützlich für Tibber-Kunden, die ihren Energieverbrauch in Echtzeit überwachen und optimieren möchten.

## Funktionsweise
Das Add-on liest die Verbrauchsdaten einer spezifizierten Entität, die den Stromzählerstand repräsentiert, und übermittelt diese Daten über die Tibber API an Tibber. Es nutzt die Home Assistant Services, um mit dem Home Assistant Supervisor zu interagieren und benötigt gültige Anmeldeinformationen für die Authentifizierung bei Tibber.

## Voraussetzungen
Ein Home Assistant-System mit Supervisor.
Gültige Tibber-Anmeldeinformationen (E-Mail und Passwort).
Eine Entität in Home Assistant, die den aktuellen Zählerstand des Stromzählers darstellt.
Installation
1.Fügen Sie dieses Repository zu Ihrem Home Assistant hinzu, indem Sie die URL https://github.com/beaTejakulator/tibber_reading_uploader verwenden.
2.Installieren Sie das Add-on über die Home Assistant Add-on-Store-Schnittstelle.
3.Konfigurieren Sie das Add-on mit den erforderlichen Umgebungsvariablen: EMAIL, PASSWORD und METER_SENSOR.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FbeaTejakulator%2Ftibber_reading_uploader)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

## Konfiguration
Konfigurieren Sie das Add-on, indem Sie die folgenden Umgebungsvariablen in Home Assistant setzen:

makefile
Copy code
EMAIL=IhreEmail@Beispiel.com
PASSWORD=IhrPasswort
METER_SENSOR=IhreZählerstandEntität
Nutzung
Nach der Installation und Konfiguration wird das Add-on automatisch die Verbrauchsdaten an Tibber senden, basierend auf dem Zählerstand, der von der angegebenen Entität bereitgestellt wird. Überprüfen Sie die Protokolle des Add-ons, um sicherzustellen, dass der Upload-Prozess erfolgreich gestartet wurde.

## Beitrag
Wenn Sie zum Projekt beitragen möchten, können Sie Pull Requests stellen oder Issues im GitHub-Repository eröffnen.

## Lizenz
Dieses Add-on ist unter der MIT-Lizenz veröffentlicht. Weitere Details finden Sie in der LICENSE-Datei im Repository.


# Example Home Assistant add-on repository

This repository can be used as a "blueprint" for add-on development to help you get started.

Add-on documentation: <https://developers.home-assistant.io/docs/add-ons>

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FbeaTejakulator%2Ftibber_reading_uploader)

## Add-ons

This repository contains the following add-ons

### [Example add-on](./example)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

_Example add-on to use as a blueprint for new add-ons._

<!--

Notes to developers after forking or using the github template feature:
- While developing comment out the 'image' key from 'example/config.yaml' to make the supervisor build the addon
  - Remember to put this back when pushing up your changes.
- When you merge to the 'main' branch of your repository a new build will be triggered.
  - Make sure you adjust the 'version' key in 'example/config.yaml' when you do that.
  - Make sure you update 'example/CHANGELOG.md' when you do that.
  - The first time this runs you might need to adjust the image configuration on github container registry to make it public
  - You may also need to adjust the github Actions configuration (Settings > Actions > General > Workflow > Read & Write)
- Adjust the 'image' key in 'example/config.yaml' so it points to your username instead of 'home-assistant'.
  - This is where the build images will be published to.
- Rename the example directory.
  - The 'slug' key in 'example/config.yaml' should match the directory name.
- Adjust all keys/url's that points to 'home-assistant' to now point to your user/fork.
- Share your repository on the forums https://community.home-assistant.io/c/projects/9
- Do awesome stuff!
 -->

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
