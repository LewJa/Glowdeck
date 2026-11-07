# Glowdeck - aplicación de bandeja del sistema para luces Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | **Español** | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Controla tiras LED y bombillas Tuya a través de tu red local, sin las aplicaciones del fabricante, y se reconecta sola si se corta la conexión.
Inicia sesión una vez con la aplicación Tuya Smart / Smart Life (código QR), elige tus luces y dale a cada una su función:
un color fijo o la sincronización con la pantalla (pantalla completa, borde superior o borde inferior).

## Probado con

Probado en la tira LED para monitor Battletron que vende Action (basada en Tuya, protocolo local 3.5). Otras tiras y
bombillas basadas en Tuya deberían funcionar también, pero no hay garantía. Los informes son bienvenidos en las Issues del repositorio.

## Instalación (Windows)

Descarga `Glowdeck-Setup.exe` desde la página **Releases** de este repositorio.

Ejecuta `Glowdeck-Setup.exe` (por usuario, sin permisos de administrador, Python incluido; opción "Start with Windows").
Windows SmartScreen puede avisar porque el instalador no está firmado: Más información -> Ejecutar de todos modos.

## Primer inicio

1. En la aplicación Tuya Smart / Smart Life: Me -> rueda dentada (ajustes) -> Account and Security -> **User Code** (los nombres pueden variar en tu idioma).
2. Escríbelo en Glowdeck, pulsa **Show QR code** y escanea el código con esa misma aplicación (icono de escaneo arriba a la derecha en Inicio).
3. Marca las luces que quieras usar. La aplicación encuentra sola la dirección de cada luz en tu red.

Solo se guardan las luces elegidas (ID, nombre, clave local), en `%APPDATA%\Glowdeck\config.json`. La
sesión de inicio no se conserva, así que para añadir más luces más tarde hay que volver a escanear (el código de usuario se recuerda).

Las luces que no están en una cuenta Tuya Smart / Smart Life (aplicaciones con la marca del vendedor) se pueden añadir a mano
con el ID del dispositivo y la clave local (`python -m tinytuya wizard`): Settings -> Add a light manually.

La interfaz de la aplicación está en inglés.

## Uso

Haz clic en el icono de anillo de la bandeja del sistema (a veces bajo la flecha ^); haz clic fuera o pulsa Esc para cerrar.
Clic derecho: Open, Lights on, Start with Windows, Quit.

- Los botones de arriba cambian entre luces; cada luz tiene su propio modo, color, brillo e interruptor.
- **Modo:** Colour (fijo), White (bombillas con blanco regulable: la paleta se convierte en una barra de blanco cálido a frío,
  2700-6500 K), Screen (media de toda la pantalla), Top, Bottom. Los botones que una luz no admite se ocultan al conectarse.
- Cada luz tiene su propio interruptor bajo los botones.
- **Favoritos:** 6 huecos compartidos (Edit o clic derecho en un hueco para guardar el color actual).
- **All off / All on** abajo. **Settings** (rueda dentada): luces, iniciar con Windows, **Log off**.
- Log off elimina de este PC todas las luces, las claves y el código de usuario.

El ajuste de la sincronización con la pantalla está en `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Opciones: `--demo` (tres luces falsas), `--hidden` (iniciar en la bandeja), `--no-tray`. Registro: `glowdeck.log` junto a la configuración.

## Notas

- Solo se ejecuta una copia a la vez. Cierra Smart Life o la aplicación del vendedor mientras uses esta: una luz acepta una sola conexión local.
- Reserva una IP fija para tus luces en el router; si una dirección cambia, la aplicación vuelve a buscar la luz.
- El inicio de sesión usa el cliente público de uso compartido de Tuya que también usa Home Assistant; Tuya puede cambiarlo o limitarlo.
  Se puede sustituir con las variables de entorno `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Las bombillas solo blancas tienen solo el modo White; en los modos de pantalla solo siguen el brillo.
- Actualizar una instalación existente de Glowdeck conserva sus ajustes en `%APPDATA%\Glowdeck`. Los ajustes de instalaciones antiguas con otro
  nombre de aplicación no se importan automáticamente.

## Aviso legal

Glowdeck es un proyecto independiente y no oficial. No está afiliado, respaldado ni patrocinado por Tuya, Smart Life
ni por ningún fabricante o vendedor de luces. Battletron, Action y otros nombres de productos o empresas pertenecen a sus propietarios. Todo funciona en tu PC y
se comunica con tus luces por la red local; internet solo se usa para el inicio de sesión opcional de Tuya. Úsalo bajo tu responsabilidad
(consulta `LICENSE`).

## Licencia

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): libre para usar, modificar y compartir con
fines no comerciales; no se permite venderlo ni usarlo comercialmente. Es "source-available", no "open source"
en el sentido de la OSI. Las bibliotecas de terceros conservan sus propias licencias (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
