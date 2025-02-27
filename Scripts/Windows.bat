@echo off
setlocal EnableDelayedExpansion

:: Variables
set "INSTALLER_URL=https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/Windows.exe"
set "INSTALLER_LOCATION=%TEMP%\PDLS_Installer.exe"
set "APP_PATH=%AppData%\Plat de la Semaine\Plat De La Semaine.exe"
set "APP_PARENT_PATH=%AppData%\Plat de la Semaine"

:: Couleurs (si ANSI est supporté, sinon laisser vide)
::set "GREEN_START=<ESC>[92m"
::set "RED_START=<ESC>[91m"
::set "COLOR_STOP=<ESC>[0m"
set "GREEN_START="
set "RED_START="
set "COLOR_STOP="

echo %GREEN_START%Téléchargement de Plat de la Semaine%COLOR_STOP%
::powershell -Command "Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%INSTALLER_LOCATION%'" 
powershell -Command "(New-Object Net.WebClient).DownloadFile('%INSTALLER_URL%', '%INSTALLER_LOCATION%')"
set "ERR=%errorlevel%"
call :check_error "Échec du téléchargement. Vérifiez votre connexion Internet." %ERR%

if not exist "%INSTALLER_LOCATION%" (
    echo %RED_START%Le fichier installé est introuvable. Veuillez réessayer.%COLOR_STOP%
    exit /b 1
)

echo %GREEN_START%Installation de l'application%COLOR_STOP%

:: Fermeture de l'application si elle est en cours d'exécution
taskkill /IM "Plat De La Semaine.exe" /F >nul 2>&1

:: Suppression de l'ancienne version si elle existe
if exist "%APP_PATH%" (
    del /F /Q "%APP_PATH%"
    set "ERR=%errorlevel%"
    call :check_error "L'ancienne version n'a pas pu être supprimée. Veuillez réessayer." %ERR%
)

:: Création du dossier de destination si nécessaire
if not exist "%APP_PARENT_PATH%" (
    mkdir "%APP_PARENT_PATH%"
)

:: Installation de l'application (copie du .exe téléchargé) sans afficher "1 fichier(s) copié(s)"
copy /Y /Q "%INSTALLER_LOCATION%" "%APP_PATH%"
set "ERR=%errorlevel%"
call :check_error "Échec de l'installation. Veuillez réessayer." %ERR%

:: Création d'un raccourci dans le menu Démarrer pour qu'il soit repérable via la recherche Windows
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut(\"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Plat de la Semaine.lnk\"); $s.TargetPath=\"%APP_PATH%\"; $s.WorkingDirectory=\"%APP_PARENT_PATH%\"; $s.IconLocation=\"%APP_PATH%\"; $s.Save()"

:: Suppression du fichier d'installation temporaire
del /F /Q "%INSTALLER_LOCATION%"

:: Lancement de l'application
start "" "%APP_PATH%"

echo %GREEN_START%Plat de la Semaine a été correctement installé%COLOR_STOP%
exit /b 0

:check_error
if not "%~2"=="0" (
    echo %RED_START%%~1%COLOR_STOP%
    exit /b 1
)
goto :eof
