# Glowdeck - tray app for Tuya lights

Controls Tuya LED strips and bulbs over your LAN, without the vendor apps, and reconnects by itself.
Sign in once with the Tuya Smart / Smart Life app (QR code), pick your lights, and give each one its own job:
a steady colour, or screen sync of the whole screen, the top edge or the bottom edge.

## Install (Windows)

Download `Glowdeck-Setup.exe` from the **Releases** page of this repository.


Run `Glowdeck-Setup.exe` (per-user, no admin needed, Python is bundled; optional "Start with Windows").
Windows SmartScreen may warn because the installer is unsigned: More info -> Run anyway.

### Building the installer
Share `installer_out\Glowdeck-Setup.exe` - NOT the `build\` or `dist\` folders (the exe in `build\` is an
unfinished stub and fails with "Failed to load Python DLL").

- Easiest: push this folder to GitHub and run the "Build installer" Action; download the artifact.
- Or on your PC: install Python 3.10+ (tick "Add to PATH") and Inno Setup 6, then run `build.bat`.
- From source: `pip install -r requirements.txt`, then `pythonw glowdeck.py`.

## First start

1. In the Tuya Smart / Smart Life app: Me -> settings gear -> Account and Security -> **User Code**.
2. Type it in the app, press **Show QR code**, and scan the code with that app (scan icon, top right of Home).
3. Tick the lights you want. The app finds each light's address on your network by itself.

Only the lights you pick (ID, name, local key) are stored, in `%APPDATA%\Glowdeck\config.json`. The
sign-in session itself is not kept, so adding more lights later means scanning again (the user code is remembered).

Lights that are not in a Tuya Smart / Smart Life account (apps branded by the light's seller) can be added by hand
with the device ID and local key (`python -m tinytuya wizard`): Settings -> Add a light manually.

## Using it

Click the tray ring icon (maybe under the ^ arrow); click elsewhere or press Esc to close. Right-click: Open,
Lights on, Start with Windows, Quit.

- The chips at the top switch between lights; each light has its own mode, colour, brightness and power.
- **Mode:** Colour (steady), White (bulbs with adjustable white: the palette turns into a warm-to-cold temperature bar,
  2700-6500 K), Screen (average of the whole screen), Top, Bottom. Tiles a light can't do are hidden once it is connected.
- Each light has its own on/off switch under the chips.
- **Favourites:** 6 shared slots (Edit or right-click a slot to save the current colour).
- **All off / All on** in the footer. **Settings** (gear): lights, start with Windows, **Log off**.
- Log off deletes every light, key and the user code from this PC.

Screen-sync tuning is in `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Flags: `--demo` (three fake lights), `--hidden` (start in the tray), `--no-tray`. Log: `glowdeck.log` next to the config.

## Notes

- Only one copy runs at a time. Close Smart Life or the seller's own app while using this app: a light accepts one local connection.
- Give your lights a reserved IP in the router; if an address changes the app searches for the light again.
- The sign-in uses the public Tuya sharing client that Home Assistant uses; Tuya may change or limit it.
  Override with env `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- White-only bulbs only have the White mode; in screen modes they follow brightness only.
- Updating an existing Glowdeck installation keeps its settings in `%APPDATA%\Glowdeck`. Settings from older installations under a
  different app name are not imported automatically.

## Disclaimer

Glowdeck is an independent, unofficial project. It is not affiliated with, endorsed by or sponsored by Tuya, Smart Life,
or any light manufacturer or seller. Product and company names belong to their owners. Everything runs on your PC and
talks to your lights over your local network; the only internet use is the optional Tuya sign-in. Use at your own risk
(see `LICENSE`).

## Licence

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): free to use, change and share for
noncommercial purposes; selling it or using it commercially is not allowed. This is "source-available", not "open source"
in the OSI sense. Third-party libraries keep their own licences (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
