# Glowdeck - aplikacja w zasobniku do świateł Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | **Polski** | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | [Português](README.pt.md) | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Steruje paskami LED i żarówkami Tuya przez sieć lokalną, bez aplikacji producenta, i sam łączy się ponownie po zerwaniu
połączenia. Zaloguj się raz w aplikacji Tuya Smart / Smart Life (kod QR), wybierz swoje światła i przypisz każdemu
osobne zadanie: stały kolor albo synchronizację z ekranem (cały ekran, górna lub dolna krawędź).

## Testowane na

Przetestowano na pasku LED do monitora Battletron sprzedawanym w sklepie Action (oparty na Tuya, protokół lokalny 3.5).
Inne paski i żarówki oparte na Tuya powinny działać, ale nie ma gwarancji. Zgłoszenia mile widziane w zakładce Issues
tego repozytorium.

## Instalacja (Windows)

Pobierz `Glowdeck-Setup.exe` ze strony **Releases** tego repozytorium.

Uruchom `Glowdeck-Setup.exe` (instalacja dla jednego użytkownika, bez uprawnień administratora, Python jest w komplecie;
opcjonalnie "Start with Windows"). Filtr SmartScreen może ostrzegać, bo instalator nie jest podpisany:
"Więcej informacji" -> "Uruchom mimo to".

## Pierwsze uruchomienie

1. W aplikacji Tuya Smart / Smart Life: Me -> ikona ustawień -> Account and Security -> **User Code** (w polskiej wersji aplikacji nazwy mogą brzmieć inaczej).
2. Wpisz ten kod w Glowdeck, naciśnij **Show QR code** i zeskanuj kod tą samą aplikacją (ikona skanowania w prawym górnym rogu ekranu głównego).
3. Zaznacz światła, którymi chcesz sterować. Aplikacja sama znajdzie adres każdego z nich w twojej sieci.

Zapisywane są tylko wybrane światła (ID, nazwa, klucz lokalny), w `%APPDATA%\Glowdeck\config.json`. Sama sesja
logowania nie jest zapamiętywana, więc dodanie kolejnych świateł później wymaga ponownego zeskanowania kodu
(kod użytkownika jest zapamiętany).

Światła spoza konta Tuya Smart / Smart Life (aplikacje z marką sprzedawcy) można dodać ręcznie, podając ID urządzenia
i klucz lokalny (`python -m tinytuya wizard`): Settings -> Add a light manually.

Interfejs aplikacji jest po angielsku.

## Obsługa

Kliknij pierścień w zasobniku systemowym (może być pod strzałką ^); kliknięcie poza oknem lub Esc zamyka okno.
Prawy przycisk myszy: Open, Lights on, Start with Windows, Quit.

- Kafelki u góry przełączają światła; każde ma własny tryb, kolor, jasność i włącznik.
- **Tryb:** Colour (stały kolor), White (żarówki z regulowaną bielą: paleta zmienia się w pasek od ciepłej do zimnej
  bieli, 2700-6500 K), Screen (średnia z całego ekranu), Top, Bottom. Kafelki, których dane światło nie obsługuje,
  są ukryte po połączeniu z nim.
- Każde światło ma własny włącznik pod kafelkami.
- **Ulubione:** 6 wspólnych miejsc (Edit albo prawy przycisk na miejscu zapisuje aktualny kolor).
- **All off / All on** na dole. **Settings** (koło zębate): światła, uruchamianie z Windows, **Log off**.
- Log off usuwa z tego komputera wszystkie światła, klucze i kod użytkownika.

Ustawienia synchronizacji z ekranem są w `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Opcje: `--demo` (trzy sztuczne światła), `--hidden` (start w zasobniku), `--no-tray`. Dziennik: `glowdeck.log` obok pliku konfiguracji.

## Uwagi

- Działa tylko jedna kopia naraz. Zamknij Smart Life lub aplikację sprzedawcy podczas używania Glowdeck: światło przyjmuje jedno połączenie lokalne.
- Zarezerwuj światłom stały adres IP w routerze; jeśli adres się zmieni, aplikacja wyszuka światło ponownie.
- Logowanie korzysta z publicznego klienta Tuya, którego używa Home Assistant; Tuya może go zmienić lub ograniczyć.
  Można go zastąpić zmiennymi środowiskowymi `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- Żarówki tylko z białym światłem mają tylko tryb White; w trybach ekranu zmieniają jedynie jasność.
- Aktualizacja istniejącej instalacji Glowdeck zachowuje ustawienia w `%APPDATA%\Glowdeck`. Ustawienia starszych
  instalacji pod inną nazwą aplikacji nie są importowane automatycznie.

## Zastrzeżenie

Glowdeck to niezależny, nieoficjalny projekt. Nie jest powiązany z firmami Tuya, Smart Life ani z żadnym producentem
lub sprzedawcą świateł, ani przez nich popierany czy sponsorowany. Battletron, Action oraz inne nazwy produktów
i firm należą do ich właścicieli. Wszystko działa na twoim komputerze i komunikuje się ze światłami przez sieć lokalną;
jedyne użycie internetu to opcjonalne logowanie do Tuya. Używasz na własne ryzyko (zob. `LICENSE`).

## Licencja

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): wolno używać, zmieniać
i udostępniać do celów niekomercyjnych; sprzedaż ani użycie komercyjne nie są dozwolone. To licencja "source-available",
a nie "open source" w rozumieniu OSI. Biblioteki zewnętrzne mają własne licencje (tinytuya, mss, numpy, Pillow, pystray,
tuya-device-sharing-sdk, PyInstaller).
