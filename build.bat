@echo off
rem Builds the app (dist\Glowdeck\Glowdeck.exe) and, if Inno Setup is installed,
rem the installer (installer_out\Glowdeck-Setup.exe). Share the INSTALLER, not the build\ or dist\ folders.
cd /d "%~dp0"
python -m pip install -r requirements.txt pyinstaller || goto :err
python -m PyInstaller --noconfirm --clean --windowed --onedir --name Glowdeck ^
  --icon assets\icon.ico --add-data "ui.html;." --add-data "qrcode.js;." --add-data "assets\icon.png;assets" ^
  --collect-all tinytuya --collect-all tuya_sharing --collect-submodules mss --hidden-import pystray._win32 ^
  glowdeck.py || goto :err
where iscc >nul 2>nul && iscc installer.iss
if errorlevel 1 echo Inno Setup (iscc) not found - install it from jrsoftware.org to build the installer.
if exist installer_out\Glowdeck-Setup.exe echo.& echo Installer ready: installer_out\Glowdeck-Setup.exe
echo Done.
exit /b 0
:err
echo Build failed.
exit /b 1
