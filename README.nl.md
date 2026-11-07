# Glowdeck - trayapp voor Tuya-lampen

[English](README.md) | **Nederlands** | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Bestuurt Tuya-ledstrips en -lampen via je lokale netwerk, zonder de apps van de fabrikant, en verbindt zichzelf opnieuw als de verbinding wegvalt.
Meld je één keer aan met de Tuya Smart / Smart Life-app (QR-code), kies je lampen en geef elke lamp zijn eigen taak:
een vaste kleur, of schermsynchronisatie met het hele scherm, de bovenrand of de onderrand.

## Getest met

Getest op de Battletron monitor-ledstrip die Action verkoopt (op basis van Tuya, lokaal protocol 3.5). Andere ledstrips en
lampen op basis van Tuya werken waarschijnlijk ook, maar dat is niet gegarandeerd. Meldingen zijn welkom bij de Issues van deze repository.

## Installeren (Windows)

Download `Glowdeck-Setup.exe` op de pagina **Releases** van deze repository.

Start `Glowdeck-Setup.exe` (per gebruiker, geen beheerdersrechten nodig, Python zit erbij; optioneel "Start with Windows").
Windows SmartScreen kan waarschuwen omdat het installatieprogramma niet is ondertekend: Meer info -> Toch uitvoeren.

## Eerste keer starten

1. In de Tuya Smart / Smart Life-app: Me -> tandwiel (instellingen) -> Account and Security -> **User Code** (de namen kunnen in jouw taal anders zijn).
2. Typ de code in Glowdeck, druk op **Show QR code** en scan de code met diezelfde app (scanicoon rechtsboven op het startscherm).
3. Vink de lampen aan die je wilt gebruiken. De app zoekt het adres van elke lamp zelf op in je netwerk.

Alleen de lampen die je kiest (ID, naam, lokale sleutel) worden opgeslagen, in `%APPDATA%\Glowdeck\config.json`. De
aanmeldsessie zelf wordt niet bewaard; om later meer lampen toe te voegen scan je opnieuw (de gebruikerscode wordt onthouden).

Lampen die niet in een Tuya Smart / Smart Life-account staan (apps met het merk van de verkoper) kun je handmatig toevoegen
met het apparaat-ID en de lokale sleutel (`python -m tinytuya wizard`): Settings -> Add a light manually.

De interface van de app is in het Engels.

## Gebruik

Klik op het ring-icoon in het systeemvak (soms onder de pijl ^); klik ergens anders of druk op Esc om het venster te sluiten.
Rechtsklik: Open, Lights on, Start with Windows, Quit.

- Met de knoppen bovenaan wissel je tussen lampen; elke lamp heeft een eigen modus, kleur, helderheid en aan/uit-schakelaar.
- **Modus:** Colour (vast), White (lampen met instelbaar wit: het palet wordt een balk van warm naar koud wit,
  2700-6500 K), Screen (gemiddelde van het hele scherm), Top, Bottom. Tegels die een lamp niet ondersteunt zijn verborgen zodra hij verbonden is.
- Elke lamp heeft onder de knoppen zijn eigen aan/uit-schakelaar.
- **Favorieten:** 6 gedeelde plekken (Edit of rechtsklik op een plek om de huidige kleur op te slaan).
- **All off / All on** onderaan. **Settings** (tandwiel): lampen, starten met Windows, **Log off**.
- Log off verwijdert alle lampen, sleutels en de gebruikerscode van deze pc.

De afstelling van de schermsynchronisatie staat in `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Opties: `--demo` (drie testlampen), `--hidden` (start in het systeemvak), `--no-tray`. Logbestand: `glowdeck.log` naast het configuratiebestand.

## Opmerkingen

- Er draait maar één exemplaar tegelijk. Sluit Smart Life of de app van de verkoper tijdens het gebruik: een lamp accepteert één lokale verbinding.
- Geef je lampen een gereserveerd IP-adres in de router; als een adres verandert, zoekt de app de lamp opnieuw.
- De aanmelding gebruikt de openbare Tuya-sharing-client die ook Home Assistant gebruikt; Tuya kan die wijzigen of beperken.
  Te overschrijven met de omgevingsvariabelen `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Lampen met alleen wit licht hebben alleen de modus White; in schermmodi volgen ze alleen de helderheid.
- Een bestaande Glowdeck-installatie bijwerken behoudt de instellingen in `%APPDATA%\Glowdeck`. Instellingen van oudere installaties onder een
  andere appnaam worden niet automatisch overgenomen.

## Disclaimer

Glowdeck is een onafhankelijk, onofficieel project. Het is niet verbonden aan, goedgekeurd door of gesponsord door Tuya, Smart Life
of een fabrikant of verkoper van lampen. Battletron, Action en andere product- of bedrijfsnamen zijn eigendom van hun eigenaars. Alles draait op je pc en
praat met je lampen via je lokale netwerk; internet wordt alleen gebruikt voor de optionele Tuya-aanmelding. Gebruik op eigen risico
(zie `LICENSE`).

## Licentie

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): vrij te gebruiken, aan te passen en te delen voor
niet-commerciële doeleinden; verkopen of commercieel gebruik is niet toegestaan. Dit is "source-available", niet "open source"
in de zin van de OSI. Bibliotheken van derden behouden hun eigen licenties (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
