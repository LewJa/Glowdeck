# Glowdeck - aplikacija u području obavijesti za Tuya svjetla

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | **Hrvatski**

Upravlja Tuya LED trakama i žaruljama preko vaše lokalne mreže, bez aplikacija proizvođača, i sama se ponovno spaja ako veza pukne.
Prijavite se jednom u aplikaciji Tuya Smart / Smart Life (QR kod), odaberite svoja svjetla i svakome dodijelite zadatak:
stalnu boju ili sinkronizaciju sa zaslonom (cijeli zaslon, gornji ili donji rub).

## Testirano s

Testirano na LED traci za monitor Battletron koju prodaje Action (temeljena na Tuya, lokalni protokol 3.5). Druge trake i
žarulje temeljene na Tuya trebale bi raditi, ali nema jamstva. Izvješća su dobrodošla u Issues ovog repozitorija.

## Instalacija (Windows)

Preuzmite `Glowdeck-Setup.exe` sa stranice **Releases** ovog repozitorija.

Pokrenite `Glowdeck-Setup.exe` (po korisniku, bez administratorskih prava, Python je uključen; opcionalno "Start with Windows").
Windows SmartScreen može upozoriti jer instalacijski program nije potpisan: Više informacija -> Svejedno pokreni.

## Prvo pokretanje

1. U aplikaciji Tuya Smart / Smart Life: Me -> zupčanik (postavke) -> Account and Security -> **User Code** (nazivi se na hrvatskom mogu razlikovati).
2. Upišite ga u Glowdeck, pritisnite **Show QR code** i skenirajte kod istom aplikacijom (ikona skeniranja gore desno na početnom zaslonu).
3. Označite svjetla koja želite upravljati. Aplikacija sama pronalazi adresu svakog svjetla u vašoj mreži.

Spremaju se samo odabrana svjetla (ID, naziv, lokalni ključ), u `%APPDATA%\Glowdeck\config.json`. Sama
prijava se ne pamti, pa za dodavanje novih svjetala kasnije treba ponovno skenirati (korisnički kod se pamti).

Svjetla koja nisu u računu Tuya Smart / Smart Life (aplikacije s markom prodavača) mogu se dodati ručno
putem ID-a uređaja i lokalnog ključa (`python -m tinytuya wizard`): Settings -> Add a light manually.

Sučelje aplikacije je na engleskom.

## Korištenje

Kliknite ikonu prstena u području obavijesti (ponekad ispod strelice ^); kliknite drugdje ili pritisnite Esc za zatvaranje.
Desni klik: Open, Lights on, Start with Windows, Quit.

- Gumbi na vrhu prebacuju između svjetala; svako svjetlo ima vlastiti način rada, boju, svjetlinu i prekidač.
- **Način rada:** Colour (stalna boja), White (žarulje s podesivom bijelom: paleta postaje traka od tople do hladne bijele,
  2700-6500 K), Screen (prosjek cijelog zaslona), Top, Bottom. Pločice koje svjetlo ne podržava skrivene su nakon spajanja.
- Svako svjetlo ima vlastiti prekidač ispod gumba.
- **Favoriti:** 6 zajedničkih mjesta (Edit ili desni klik na mjesto sprema trenutnu boju).
- **All off / All on** dolje. **Settings** (zupčanik): svjetla, pokretanje s Windowsima, **Log off**.
- Log off s ovog računala briše sva svjetla, ključeve i korisnički kod.

Podešavanje sinkronizacije sa zaslonom nalazi se u `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Opcije: `--demo` (tri lažna svjetla), `--hidden` (pokretanje u području obavijesti), `--no-tray`. Zapisnik: `glowdeck.log` pored konfiguracije.

## Napomene

- Istodobno radi samo jedna kopija. Zatvorite Smart Life ili aplikaciju prodavača dok koristite ovu: svjetlo prihvaća jednu lokalnu vezu.
- Svjetlima u routeru rezervirajte stalnu IP adresu; ako se adresa promijeni, aplikacija ponovno traži svjetlo.
- Prijava koristi javnog Tuya klijenta za dijeljenje koji koristi i Home Assistant; Tuya ga može promijeniti ili ograničiti.
  Može se zamijeniti varijablama okoline `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Žarulje samo s bijelom svjetlošću imaju samo način White; u načinima zaslona prate samo svjetlinu.
- Ažuriranje postojeće instalacije Glowdecka zadržava postavke u `%APPDATA%\Glowdeck`. Postavke starijih instalacija pod
  drugim nazivom aplikacije ne uvoze se automatski.

## Odricanje od odgovornosti

Glowdeck je neovisan, neslužben projekt. Nije povezan s Tuya, Smart Life ni s bilo kojim proizvođačem ili prodavačem svjetala,
niti ga oni podržavaju ili sponzoriraju. Battletron, Action i drugi nazivi proizvoda ili tvrtki pripadaju njihovim vlasnicima. Sve radi na vašem računalu i
komunicira sa svjetlima preko lokalne mreže; internet se koristi samo za neobaveznu prijavu u Tuya. Koristite na vlastitu odgovornost
(vidi `LICENSE`).

## Licenca

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): slobodno za korištenje, izmjenu i dijeljenje u
nekomercijalne svrhe; prodaja ni komercijalna uporaba nisu dopuštene. To je "source-available", a ne "open source"
u smislu OSI-ja. Biblioteke trećih strana zadržavaju vlastite licence (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
