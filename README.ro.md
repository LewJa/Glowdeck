# Glowdeck - aplicație în zona de notificare pentru lumini Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | **Română** | [Hrvatski](README.hr.md)

Controlează benzi LED și becuri Tuya prin rețeaua ta locală, fără aplicațiile producătorului, și se reconectează singură dacă legătura cade.
Autentifică-te o dată în aplicația Tuya Smart / Smart Life (cod QR), alege luminile și dă fiecăreia rolul ei:
o culoare fixă sau sincronizarea cu ecranul (tot ecranul, marginea de sus sau marginea de jos).

## Testat cu

Testat pe banda LED pentru monitor Battletron vândută de Action (bazată pe Tuya, protocol local 3.5). Alte benzi și
becuri bazate pe Tuya ar trebui să funcționeze și ele, dar nu există garanție. Rapoartele sunt binevenite în Issues din depozit.

## Instalare (Windows)

Descarcă `Glowdeck-Setup.exe` de pe pagina **Releases** a acestui depozit.

Rulează `Glowdeck-Setup.exe` (per utilizator, fără drepturi de administrator, Python este inclus; opțional "Start with Windows").
Windows SmartScreen poate avertiza deoarece programul de instalare nu este semnat: Mai multe informații -> Rulează oricum.

## Prima pornire

1. În aplicația Tuya Smart / Smart Life: Me -> roata dințată (setări) -> Account and Security -> **User Code** (denumirile pot diferi în limba ta).
2. Scrie-l în Glowdeck, apasă **Show QR code** și scanează codul cu aceeași aplicație (pictograma de scanare, sus în dreapta pe ecranul principal).
3. Bifează luminile pe care vrei să le controlezi. Aplicația găsește singură adresa fiecărei lumini în rețeaua ta.

Se salvează doar luminile alese (ID, nume, cheie locală), în `%APPDATA%\Glowdeck\config.json`. Sesiunea
de autentificare nu se păstrează, deci pentru a adăuga mai târziu alte lumini trebuie scanat din nou (codul de utilizator este reținut).

Luminile care nu sunt într-un cont Tuya Smart / Smart Life (aplicații cu marca vânzătorului) pot fi adăugate manual
cu ID-ul dispozitivului și cheia locală (`python -m tinytuya wizard`): Settings -> Add a light manually.

Interfața aplicației este în engleză.

## Utilizare

Dă clic pe pictograma inel din zona de notificare (uneori sub săgeata ^); dă clic în altă parte sau apasă Esc pentru a închide.
Clic dreapta: Open, Lights on, Start with Windows, Quit.

- Butoanele de sus comută între lumini; fiecare lumină are propriul mod, culoare, luminozitate și comutator.
- **Mod:** Colour (fix), White (becuri cu alb reglabil: paleta devine o bară de la alb cald la rece,
  2700-6500 K), Screen (media întregului ecran), Top, Bottom. Casetele pe care o lumină nu le acceptă sunt ascunse după conectare.
- Fiecare lumină are propriul comutator sub butoane.
- **Favorite:** 6 locuri comune (Edit sau clic dreapta pe un loc salvează culoarea curentă).
- **All off / All on** jos. **Settings** (roata dințată): lumini, pornire cu Windows, **Log off**.
- Log off șterge de pe acest PC toate luminile, cheile și codul de utilizator.

Reglajele sincronizării cu ecranul sunt în `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Opțiuni: `--demo` (trei lumini false), `--hidden` (pornire în zona de notificare), `--no-tray`. Jurnal: `glowdeck.log` lângă configurație.

## Note

- Rulează o singură copie odată. Închide Smart Life sau aplicația vânzătorului cât folosești aceasta: o lumină acceptă o singură conexiune locală.
- Rezervă adrese IP fixe luminilor în router; dacă o adresă se schimbă, aplicația caută din nou lumina.
- Autentificarea folosește clientul public de partajare Tuya pe care îl folosește și Home Assistant; Tuya îl poate schimba sau limita.
  Poate fi înlocuit cu variabilele de mediu `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Becurile doar cu lumină albă au doar modul White; în modurile de ecran urmăresc doar luminozitatea.
- Actualizarea unei instalări existente Glowdeck păstrează setările în `%APPDATA%\Glowdeck`. Setările instalărilor mai vechi cu alt
  nume de aplicație nu sunt importate automat.

## Declinarea responsabilității

Glowdeck este un proiect independent, neoficial. Nu este afiliat cu Tuya, Smart Life sau cu vreun producător ori vânzător de lumini,
și nici susținut sau sponsorizat de aceștia. Battletron, Action și alte nume de produse sau companii aparțin proprietarilor lor. Totul rulează pe PC-ul tău și
comunică cu luminile prin rețeaua locală; internetul este folosit doar pentru autentificarea opțională în Tuya. Folosești pe propria răspundere
(vezi `LICENSE`).

## Licență

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): liber de folosit, modificat și distribuit în
scopuri necomerciale; vânzarea sau utilizarea comercială nu sunt permise. Este "source-available", nu "open source"
în sensul OSI. Bibliotecile terțe își păstrează propriile licențe (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
