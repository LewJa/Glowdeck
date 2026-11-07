# Glowdeck - application de barre d'état pour lampes Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | **Français** | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Pilote les bandes LED et ampoules Tuya via votre réseau local, sans les applications du fabricant, et se reconnecte tout seul en cas de coupure.
Connectez-vous une fois avec l'application Tuya Smart / Smart Life (code QR), choisissez vos lampes et donnez à chacune son rôle :
une couleur fixe, ou la synchronisation avec l'écran entier, le bord supérieur ou le bord inférieur.

## Testé avec

Testé sur la bande LED pour moniteur Battletron vendue par Action (basée sur Tuya, protocole local 3.5). Les autres bandes et
ampoules basées sur Tuya devraient fonctionner aussi, mais sans garantie. Les retours sont les bienvenus dans les Issues du dépôt.

## Installation (Windows)

Téléchargez `Glowdeck-Setup.exe` depuis la page **Releases** de ce dépôt.

Lancez `Glowdeck-Setup.exe` (par utilisateur, sans droits d'administrateur, Python est inclus ; option "Start with Windows").
Windows SmartScreen peut afficher un avertissement car l'installeur n'est pas signé : Informations complémentaires -> Exécuter quand même.

## Premier lancement

1. Dans l'application Tuya Smart / Smart Life : Me -> roue dentée (paramètres) -> Account and Security -> **User Code** (les noms peuvent différer dans votre langue).
2. Saisissez-le dans Glowdeck, appuyez sur **Show QR code** et scannez le code avec cette même application (icône de scan en haut à droite de l'accueil).
3. Cochez les lampes voulues. L'application trouve elle-même l'adresse de chaque lampe sur votre réseau.

Seules les lampes choisies (ID, nom, clé locale) sont enregistrées, dans `%APPDATA%\Glowdeck\config.json`. La
session de connexion elle-même n'est pas conservée : pour ajouter d'autres lampes plus tard, il faut scanner à nouveau (le code utilisateur est mémorisé).

Les lampes qui ne sont pas dans un compte Tuya Smart / Smart Life (applications à la marque du vendeur) peuvent être ajoutées à la main
avec l'ID de l'appareil et la clé locale (`python -m tinytuya wizard`) : Settings -> Add a light manually.

L'interface de l'application est en anglais.

## Utilisation

Cliquez sur l'icône en anneau dans la zone de notification (parfois sous la flèche ^) ; cliquez ailleurs ou appuyez sur Échap pour fermer.
Clic droit : Open, Lights on, Start with Windows, Quit.

- Les pastilles en haut permettent de passer d'une lampe à l'autre ; chaque lampe a son propre mode, sa couleur, sa luminosité et son interrupteur.
- **Mode :** Colour (fixe), White (ampoules à blanc réglable : la palette devient une barre du blanc chaud au blanc froid,
  2700-6500 K), Screen (moyenne de tout l'écran), Top, Bottom. Les tuiles qu'une lampe ne gère pas sont masquées une fois connectée.
- Chaque lampe a son propre interrupteur sous les pastilles.
- **Favoris :** 6 emplacements communs (Edit ou clic droit sur un emplacement pour enregistrer la couleur actuelle).
- **All off / All on** en bas. **Settings** (roue dentée) : lampes, démarrage avec Windows, **Log off**.
- Log off supprime de ce PC toutes les lampes, les clés et le code utilisateur.

Le réglage de la synchronisation d'écran se trouve dans `config.json` : `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Options : `--demo` (trois lampes factices), `--hidden` (démarrer dans la zone de notification), `--no-tray`. Journal : `glowdeck.log` à côté de la configuration.

## Remarques

- Une seule copie fonctionne à la fois. Fermez Smart Life ou l'application du vendeur pendant l'utilisation : une lampe n'accepte qu'une connexion locale.
- Réservez une adresse IP à vos lampes dans le routeur ; si une adresse change, l'application recherche de nouveau la lampe.
- La connexion utilise le client public de partage Tuya que Home Assistant utilise aussi ; Tuya peut le modifier ou le limiter.
  Remplaçable avec les variables d'environnement `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Les ampoules à lumière blanche seule n'ont que le mode White ; dans les modes d'écran, elles ne suivent que la luminosité.
- La mise à jour d'une installation existante de Glowdeck conserve ses réglages dans `%APPDATA%\Glowdeck`. Les réglages d'anciennes installations sous un
  autre nom d'application ne sont pas importés automatiquement.

## Avertissement

Glowdeck est un projet indépendant et non officiel. Il n'est ni affilié à Tuya, Smart Life ou à un fabricant ou vendeur de lampes,
ni approuvé ou sponsorisé par eux. Battletron, Action et les autres noms de produits ou d'entreprises appartiennent à leurs propriétaires. Tout fonctionne sur votre PC et
communique avec vos lampes via votre réseau local ; Internet n'est utilisé que pour la connexion Tuya facultative. Utilisation à vos risques
(voir `LICENSE`).

## Licence

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0) : libre d'utilisation, de modification et de partage à des
fins non commerciales ; la vente ou l'usage commercial ne sont pas autorisés. C'est du "source-available", pas de l'"open source"
au sens de l'OSI. Les bibliothèques tierces gardent leurs propres licences (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
