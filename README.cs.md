# Glowdeck - aplikace v oznamovací oblasti pro světla Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | **Čeština** | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Ovládá LED pásky a žárovky Tuya přes vaši místní síť, bez aplikací výrobce, a po přerušení spojení se sama znovu připojí.
Jednou se přihlaste v aplikaci Tuya Smart / Smart Life (QR kód), vyberte svá světla a každému přidělte vlastní úkol:
stálou barvu nebo synchronizaci s obrazovkou (celá obrazovka, horní nebo dolní okraj).

## Testováno s

Testováno na LED pásku k monitoru Battletron, který prodává Action (založený na Tuya, místní protokol 3.5). Jiné pásky a
žárovky založené na Tuya by měly fungovat také, ale není to zaručeno. Hlášení uvítáme v Issues tohoto repozitáře.

## Instalace (Windows)

Stáhněte `Glowdeck-Setup.exe` ze stránky **Releases** tohoto repozitáře.

Spusťte `Glowdeck-Setup.exe` (pro jednoho uživatele, bez práv správce, Python je součástí; volitelně "Start with Windows").
Windows SmartScreen může varovat, protože instalátor není podepsaný: Další informace -> Přesto spustit.

## První spuštění

1. V aplikaci Tuya Smart / Smart Life: Me -> ozubené kolo (nastavení) -> Account and Security -> **User Code** (názvy se v češtině mohou lišit).
2. Zadejte kód do Glowdeck, stiskněte **Show QR code** a naskenujte kód toutéž aplikací (ikona skenování vpravo nahoře na úvodní obrazovce).
3. Zaškrtněte světla, která chcete ovládat. Aplikace si adresu každého světla v síti najde sama.

Ukládají se jen vybraná světla (ID, název, místní klíč), do `%APPDATA%\Glowdeck\config.json`. Samotné
přihlášení se neuchovává, takže pro přidání dalších světel později je třeba znovu skenovat (kód uživatele se pamatuje).

Světla, která nejsou v účtu Tuya Smart / Smart Life (aplikace s značkou prodejce), lze přidat ručně
pomocí ID zařízení a místního klíče (`python -m tinytuya wizard`): Settings -> Add a light manually.

Rozhraní aplikace je v angličtině.

## Používání

Klikněte na ikonu kroužku v oznamovací oblasti (někdy pod šipkou ^); kliknutím jinam nebo klávesou Esc okno zavřete.
Pravé tlačítko: Open, Lights on, Start with Windows, Quit.

- Tlačítka nahoře přepínají mezi světly; každé světlo má vlastní režim, barvu, jas a vypínač.
- **Režim:** Colour (stálá barva), White (žárovky s nastavitelnou bílou: paleta se změní na lištu od teplé po studenou bílou,
  2700-6500 K), Screen (průměr celé obrazovky), Top, Bottom. Dlaždice, které světlo nepodporuje, se po připojení skryjí.
- Každé světlo má pod tlačítky vlastní vypínač.
- **Oblíbené:** 6 sdílených pozic (Edit nebo pravé tlačítko na pozici uloží aktuální barvu).
- **All off / All on** dole. **Settings** (ozubené kolo): světla, spuštění s Windows, **Log off**.
- Log off z tohoto počítače odstraní všechna světla, klíče a kód uživatele.

Ladění synchronizace s obrazovkou je v `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Volby: `--demo` (tři umělá světla), `--hidden` (start v oznamovací oblasti), `--no-tray`. Protokol: `glowdeck.log` vedle konfigurace.

## Poznámky

- Najednou běží jen jedna kopie. Při používání zavřete Smart Life nebo aplikaci prodejce: světlo přijímá jedno místní spojení.
- Světlům v routeru rezervujte pevnou IP adresu; pokud se adresa změní, aplikace světlo vyhledá znovu.
- Přihlášení používá veřejného sdíleného klienta Tuya, který používá i Home Assistant; Tuya jej může změnit nebo omezit.
  Lze přepsat proměnnými prostředí `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Žárovky jen s bílým světlem mají jen režim White; v režimech obrazovky sledují pouze jas.
- Aktualizace existující instalace Glowdeck zachová nastavení v `%APPDATA%\Glowdeck`. Nastavení starších instalací pod
  jiným názvem aplikace se automaticky nepřebírá.

## Prohlášení

Glowdeck je nezávislý, neoficiální projekt. Není spojen s Tuya, Smart Life ani s žádným výrobcem či prodejcem světel,
ani jimi podporován či sponzorován. Battletron, Action a další názvy produktů nebo firem patří jejich vlastníkům. Vše běží na vašem počítači
a se světly komunikuje přes místní síť; internet se používá jen pro volitelné přihlášení k Tuya. Používáte na vlastní riziko
(viz `LICENSE`).

## Licence

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): zdarma k používání, úpravám a sdílení pro
nekomerční účely; prodej ani komerční využití není povoleno. Jde o "source-available", nikoli "open source"
ve smyslu OSI. Knihovny třetích stran mají vlastní licence (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
