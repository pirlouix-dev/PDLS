@echo off
chcp 1252
setlocal EnableDelayedExpansion

:: Variables
set "INSTALLER_URL=https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/Windows.exe"
set "INSTALLER_LOCATION=%TEMP%\PDLS_Installer.exe"
set "APP_PATH=%AppData%\Plat de la Semaine\Plat de la Semaine.exe"
set "APP_PARENT_PATH=%AppData%\Plat de la Semaine"

echo Telechargement de Plat de la Semaine
::powershell -Command "Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%INSTALLER_LOCATION%'" 
powershell -Command "(New-Object Net.WebClient).DownloadFile('%INSTALLER_URL%', '%INSTALLER_LOCATION%')"
set "ERR=%errorlevel%"
call :check_error "Echec du telechargement. Verifiez votre connexion Internet." %ERR%

if not exist "%INSTALLER_LOCATION%" (
    echo Le fichier installe est introuvable. Veuillez reessayer.
    exit /b 1
)

echo Installation de l'application

:: Vrifier si l'application est ouverte
tasklist /FI "IMAGENAME eq Plat de la Semaine.exe" 2>NUL | find /I "Plat de la Semaine.exe" >NUL
if %errorlevel%==0 (
    taskkill /IM "Plat de la Semaine.exe" /F >nul 2>&1
    timeout /T 2 /NOBREAK >nul
)

:: Suppression de l'ancienne version si elle existe
if %errorlevel%==0 (
    taskkill /IM "Plat de la Semaine.exe" /F >nul 2>&1
    timeout /T 2 /NOBREAK >nul
    :wait_loop
    tasklist /FI "IMAGENAME eq Plat de la Semaine.exe" 2>NUL | find /I "Plat de la Semaine.exe" >NUL
    if %errorlevel%==0 (
        echo En attente de la fermeture de l'ancienne version...
        timeout /T 1 /NOBREAK >nul
        goto wait_loop
    )
)

:: Création du dossier de destination si nécessaire
if not exist "%APP_PARENT_PATH%" (
    mkdir "%APP_PARENT_PATH%"
)

:: Installation de l'application (copie du .exe téléchargé)
copy /Y "%INSTALLER_LOCATION%" "%APP_PATH%" >NUL
set "ERR=%errorlevel%"
call :check_error "Echec de l'installation. Veuillez reessayer." %ERR%

:: Suppression du fichier d'installation temporaire
del /F /Q "%INSTALLER_LOCATION%"

:: Lancement de l'application
start "" "%APP_PATH%"
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Plat de la Semaine.lnk'); $s.TargetPath='%APP_PATH%'; $s.WorkingDirectory='%APP_PARENT_PATH%'; $s.IconLocation='%APP_PATH%'; $s.Save()"

echo Plat de la Semaine a ete correctement installe
exit /b 0

:check_error
if not "%~2"=="0" (
    echo Erreur: %~1
    exit /b 1
)
goto :eof
