# Glowdeck - Tray-App für Tuya-Leuchten

[English](README.md) | [Nederlands](README.nl.md) | **Deutsch** | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Steuert Tuya-LED-Streifen und -Lampen über dein lokales Netzwerk, ohne die Apps der Hersteller, und verbindet sich bei Abbrüchen von selbst neu.
Melde dich einmal mit der Tuya Smart / Smart Life App an (QR-Code), wähle deine Leuchten und gib jeder ihre eigene Aufgabe:
eine feste Farbe oder Bildschirm-Synchronisierung mit dem ganzen Bildschirm, dem oberen oder dem unteren Rand.

## Getestet mit

Getestet mit dem Battletron Monitor-LED-Streifen, der bei Action verkauft wird (auf Tuya-Basis, lokales Protokoll 3.5). Andere LED-Streifen und
Lampen auf Tuya-Basis sollten ebenfalls funktionieren, eine Garantie gibt es aber nicht. Rückmeldungen sind in den Issues dieses Repositorys willkommen.

## Installation (Windows)

Lade `Glowdeck-Setup.exe` von der Seite **Releases** dieses Repositorys herunter.

Starte `Glowdeck-Setup.exe` (pro Benutzer, keine Administratorrechte nötig, Python ist enthalten; optional "Start with Windows").
Windows SmartScreen kann warnen, weil das Installationsprogramm nicht signiert ist: Weitere Informationen -> Trotzdem ausführen.

## Erster Start

1. In der Tuya Smart / Smart Life App: Me -> Zahnrad (Einstellungen) -> Account and Security -> **User Code** (die Bezeichnungen können in deiner Sprache abweichen).
2. Gib den Code in Glowdeck ein, drücke **Show QR code** und scanne den Code mit derselben App (Scan-Symbol oben rechts auf dem Startbildschirm).
3. Hake die gewünschten Leuchten an. Die App findet die Adresse jeder Leuchte in deinem Netzwerk selbst.

Gespeichert werden nur die ausgewählten Leuchten (ID, Name, lokaler Schlüssel), in `%APPDATA%\Glowdeck\config.json`. Die
Anmeldesitzung selbst wird nicht gespeichert; um später weitere Leuchten hinzuzufügen, musst du erneut scannen (der User Code wird gemerkt).

Leuchten, die nicht in einem Tuya Smart / Smart Life Konto sind (Apps mit der Marke des Verkäufers), kannst du von Hand hinzufügen,
mit Geräte-ID und lokalem Schlüssel (`python -m tinytuya wizard`): Settings -> Add a light manually.

Die Oberfläche der App ist auf Englisch.

## Bedienung

Klicke auf das Ring-Symbol im Infobereich (evtl. unter dem Pfeil ^); zum Schließen woanders klicken oder Esc drücken.
Rechtsklick: Open, Lights on, Start with Windows, Quit.

- Mit den Schaltflächen oben wechselst du zwischen den Leuchten; jede hat ihren eigenen Modus, ihre Farbe, Helligkeit und ihren Schalter.
- **Modus:** Colour (fest), White (Lampen mit einstellbarem Weiß: die Palette wird zu einer Leiste von warm bis kalt,
  2700-6500 K), Screen (Durchschnitt des ganzen Bildschirms), Top, Bottom. Kacheln, die eine Leuchte nicht kann, werden nach der Verbindung ausgeblendet.
- Jede Leuchte hat unter den Schaltflächen ihren eigenen Ein/Aus-Schalter.
- **Favoriten:** 6 gemeinsame Plätze (Edit oder Rechtsklick auf einen Platz speichert die aktuelle Farbe).
- **All off / All on** unten. **Settings** (Zahnrad): Leuchten, Start mit Windows, **Log off**.
- Log off entfernt alle Leuchten, Schlüssel und den User Code von diesem PC.

Die Feinabstimmung der Bildschirm-Synchronisierung steht in `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Optionen: `--demo` (drei Testleuchten), `--hidden` (im Infobereich starten), `--no-tray`. Protokoll: `glowdeck.log` neben der Konfiguration.

## Hinweise

- Es läuft immer nur eine Kopie. Schließe Smart Life oder die App des Verkäufers, solange du diese App nutzt: Eine Leuchte akzeptiert nur eine lokale Verbindung.
- Reserviere deinen Leuchten im Router feste IP-Adressen; ändert sich eine Adresse, sucht die App die Leuchte neu.
- Die Anmeldung nutzt den öffentlichen Tuya-Sharing-Client, den auch Home Assistant verwendet; Tuya kann ihn ändern oder einschränken.
  Überschreibbar mit den Umgebungsvariablen `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Lampen, die nur weißes Licht können, haben nur den Modus White; in den Bildschirmmodi folgen sie nur der Helligkeit.
- Beim Aktualisieren einer bestehenden Glowdeck-Installation bleiben die Einstellungen in `%APPDATA%\Glowdeck` erhalten. Einstellungen älterer Installationen unter
  einem anderen App-Namen werden nicht automatisch übernommen.

## Haftungsausschluss

Glowdeck ist ein unabhängiges, inoffizielles Projekt. Es steht in keiner Verbindung zu Tuya, Smart Life oder einem Hersteller oder Verkäufer
von Leuchten und wird von diesen weder unterstützt noch gesponsert. Battletron, Action und andere Produkt- oder Firmennamen gehören ihren Inhabern. Alles läuft auf deinem PC und
spricht über dein lokales Netzwerk mit deinen Leuchten; das Internet wird nur für die optionale Tuya-Anmeldung genutzt. Nutzung auf eigene Gefahr
(siehe `LICENSE`).

## Lizenz

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): frei nutzbar, veränderbar und weitergebbar für
nicht kommerzielle Zwecke; Verkauf oder kommerzielle Nutzung sind nicht erlaubt. Das ist "source-available", nicht "Open Source"
im Sinne der OSI. Bibliotheken von Drittanbietern behalten ihre eigenen Lizenzen (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
