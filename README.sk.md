# Glowdeck - aplikácia v oznamovacej oblasti pre svetlá Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | **Slovenčina** | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Ovláda LED pásiky a žiarovky Tuya cez vašu lokálnu sieť, bez aplikácií výrobcu, a po prerušení spojenia sa sama znova pripojí.
Raz sa prihláste v aplikácii Tuya Smart / Smart Life (QR kód), vyberte svoje svetlá a každému pridelte vlastnú úlohu:
stálu farbu alebo synchronizáciu s obrazovkou (celá obrazovka, horný alebo dolný okraj).

## Testované s

Testované na LED pásiku k monitoru Battletron, ktorý predáva Action (založený na Tuya, lokálny protokol 3.5). Iné pásiky a
žiarovky založené na Tuya by mali fungovať tiež, ale nie je to zaručené. Hlásenia uvítame v Issues tohto repozitára.

## Inštalácia (Windows)

Stiahnite `Glowdeck-Setup.exe` zo stránky **Releases** tohto repozitára.

Spustite `Glowdeck-Setup.exe` (pre jedného používateľa, bez práv správcu, Python je súčasťou; voliteľne "Start with Windows").
Windows SmartScreen môže varovať, pretože inštalátor nie je podpísaný: Ďalšie informácie -> Napriek tomu spustiť.

## Prvé spustenie

1. V aplikácii Tuya Smart / Smart Life: Me -> ozubené koliesko (nastavenia) -> Account and Security -> **User Code** (názvy sa v slovenčine môžu líšiť).
2. Zadajte kód do Glowdeck, stlačte **Show QR code** a naskenujte kód tou istou aplikáciou (ikona skenovania vpravo hore na úvodnej obrazovke).
3. Zaškrtnite svetlá, ktoré chcete ovládať. Aplikácia si adresu každého svetla v sieti nájde sama.

Ukladajú sa len vybrané svetlá (ID, názov, lokálny kľúč), do `%APPDATA%\Glowdeck\config.json`. Samotné
prihlásenie sa neuchováva, takže na pridanie ďalších svetiel neskôr treba znova skenovať (kód používateľa sa pamätá).

Svetlá, ktoré nie sú v účte Tuya Smart / Smart Life (aplikácie so značkou predajcu), možno pridať ručne
pomocou ID zariadenia a lokálneho kľúča (`python -m tinytuya wizard`): Settings -> Add a light manually.

Rozhranie aplikácie je v angličtine.

## Používanie

Kliknite na ikonu kruhu v oznamovacej oblasti (niekedy pod šípkou ^); kliknutím inam alebo klávesom Esc okno zatvoríte.
Pravé tlačidlo: Open, Lights on, Start with Windows, Quit.

- Tlačidlá hore prepínajú medzi svetlami; každé svetlo má vlastný režim, farbu, jas a vypínač.
- **Režim:** Colour (stála farba), White (žiarovky s nastaviteľnou bielou: paleta sa zmení na lištu od teplej po studenú bielu,
  2700-6500 K), Screen (priemer celej obrazovky), Top, Bottom. Dlaždice, ktoré svetlo nepodporuje, sa po pripojení skryjú.
- Každé svetlo má pod tlačidlami vlastný vypínač.
- **Obľúbené:** 6 zdieľaných miest (Edit alebo pravé tlačidlo na mieste uloží aktuálnu farbu).
- **All off / All on** dole. **Settings** (ozubené koliesko): svetlá, spustenie s Windows, **Log off**.
- Log off z tohto počítača odstráni všetky svetlá, kľúče a kód používateľa.

Ladenie synchronizácie s obrazovkou je v `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Voľby: `--demo` (tri umelé svetlá), `--hidden` (štart v oznamovacej oblasti), `--no-tray`. Protokol: `glowdeck.log` vedľa konfigurácie.

## Poznámky

- Naraz beží len jedna kópia. Pri používaní zatvorte Smart Life alebo aplikáciu predajcu: svetlo prijíma jedno lokálne spojenie.
- Svetlám v routeri rezervujte pevnú IP adresu; ak sa adresa zmení, aplikácia svetlo vyhľadá znova.
- Prihlásenie používa verejného zdieľaného klienta Tuya, ktorý používa aj Home Assistant; Tuya ho môže zmeniť alebo obmedziť.
  Dá sa prepísať premennými prostredia `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Žiarovky len s bielym svetlom majú len režim White; v režimoch obrazovky sledujú iba jas.
- Aktualizácia existujúcej inštalácie Glowdeck zachová nastavenia v `%APPDATA%\Glowdeck`. Nastavenia starších inštalácií pod
  iným názvom aplikácie sa automaticky neprebierajú.

## Vyhlásenie

Glowdeck je nezávislý, neoficiálny projekt. Nie je spojený s Tuya, Smart Life ani so žiadnym výrobcom či predajcom svetiel,
ani nimi podporovaný či sponzorovaný. Battletron, Action a ďalšie názvy produktov alebo firiem patria ich vlastníkom. Všetko beží na vašom počítači
a so svetlami komunikuje cez lokálnu sieť; internet sa používa len na voliteľné prihlásenie do Tuya. Používate na vlastné riziko
(pozri `LICENSE`).

## Licencia

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): zadarmo na používanie, úpravy a zdieľanie na
nekomerčné účely; predaj ani komerčné využitie nie je povolené. Ide o "source-available", nie "open source"
v zmysle OSI. Knižnice tretích strán majú vlastné licencie (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
