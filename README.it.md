# Glowdeck - app nell'area di notifica per luci Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | **Italiano** | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Controlla strisce LED e lampadine Tuya tramite la rete locale, senza le app del produttore, e si riconnette da sola se il collegamento cade.
Accedi una volta con l'app Tuya Smart / Smart Life (codice QR), scegli le tue luci e dai a ciascuna un compito:
un colore fisso oppure la sincronizzazione con lo schermo (schermo intero, bordo superiore o bordo inferiore).

## Testato con

Testato sulla striscia LED per monitor Battletron venduta da Action (basata su Tuya, protocollo locale 3.5). Altre strisce e
lampadine basate su Tuya dovrebbero funzionare, ma senza garanzia. Le segnalazioni sono benvenute nelle Issues del repository.

## Installazione (Windows)

Scarica `Glowdeck-Setup.exe` dalla pagina **Releases** di questo repository.

Avvia `Glowdeck-Setup.exe` (per singolo utente, senza privilegi di amministratore, Python è incluso; opzione "Start with Windows").
Windows SmartScreen può avvisare perché il programma di installazione non è firmato: Ulteriori informazioni -> Esegui comunque.

## Primo avvio

1. Nell'app Tuya Smart / Smart Life: Me -> ingranaggio (impostazioni) -> Account and Security -> **User Code** (i nomi possono differire nella tua lingua).
2. Digitalo in Glowdeck, premi **Show QR code** e inquadra il codice con la stessa app (icona di scansione in alto a destra nella Home).
3. Spunta le luci che vuoi usare. L'app trova da sola l'indirizzo di ogni luce nella tua rete.

Vengono salvate solo le luci scelte (ID, nome, chiave locale), in `%APPDATA%\Glowdeck\config.json`. La
sessione di accesso non viene conservata: per aggiungere altre luci più tardi bisogna scansionare di nuovo (il codice utente viene ricordato).

Le luci che non sono in un account Tuya Smart / Smart Life (app con il marchio del venditore) si possono aggiungere a mano
con l'ID del dispositivo e la chiave locale (`python -m tinytuya wizard`): Settings -> Add a light manually.

L'interfaccia dell'app è in inglese.

## Uso

Fai clic sull'icona ad anello nell'area di notifica (a volte sotto la freccia ^); clicca altrove o premi Esc per chiudere.
Tasto destro: Open, Lights on, Start with Windows, Quit.

- I pulsanti in alto permettono di passare da una luce all'altra; ogni luce ha la propria modalità, colore, luminosità e interruttore.
- **Modalità:** Colour (fisso), White (lampadine con bianco regolabile: la tavolozza diventa una barra dal bianco caldo al freddo,
  2700-6500 K), Screen (media dell'intero schermo), Top, Bottom. I riquadri che una luce non supporta vengono nascosti una volta connessa.
- Ogni luce ha il proprio interruttore sotto i pulsanti.
- **Preferiti:** 6 posti condivisi (Edit o tasto destro su un posto per salvare il colore attuale).
- **All off / All on** in basso. **Settings** (ingranaggio): luci, avvio con Windows, **Log off**.
- Log off elimina da questo PC tutte le luci, le chiavi e il codice utente.

La regolazione della sincronizzazione con lo schermo è in `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Opzioni: `--demo` (tre luci finte), `--hidden` (avvio nell'area di notifica), `--no-tray`. Registro: `glowdeck.log` accanto alla configurazione.

## Note

- Può essere in esecuzione una sola copia. Chiudi Smart Life o l'app del venditore mentre usi questa app: una luce accetta una sola connessione locale.
- Riserva un indirizzo IP fisso alle luci nel router; se un indirizzo cambia, l'app cerca di nuovo la luce.
- L'accesso usa il client pubblico di condivisione Tuya che usa anche Home Assistant; Tuya può modificarlo o limitarlo.
  Sostituibile con le variabili d'ambiente `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Le lampadine solo bianche hanno solo la modalità White; nelle modalità schermo seguono solo la luminosità.
- Aggiornare un'installazione esistente di Glowdeck mantiene le impostazioni in `%APPDATA%\Glowdeck`. Le impostazioni di vecchie installazioni con un
  altro nome di app non vengono importate automaticamente.

## Avvertenza

Glowdeck è un progetto indipendente e non ufficiale. Non è affiliato a Tuya, Smart Life né ad alcun produttore o venditore di luci,
né da essi approvato o sponsorizzato. Battletron, Action e gli altri nomi di prodotti o aziende appartengono ai rispettivi proprietari. Tutto funziona sul tuo PC e
comunica con le luci tramite la rete locale; internet serve solo per l'accesso facoltativo a Tuya. Uso a proprio rischio
(vedi `LICENSE`).

## Licenza

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): libero uso, modifica e condivisione per
scopi non commerciali; vendita e uso commerciale non sono consentiti. È "source-available", non "open source"
nel senso dell'OSI. Le librerie di terze parti mantengono le proprie licenze (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
