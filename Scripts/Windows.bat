@echo off
setlocal ENABLEEXTENSIONS

:: Variables
set INSTALLER_URL=https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/Windows.exe
set INSTALLER_PATH=%TEMP%\Plat de la Semaine.exe
set APP_PATH=%AppData%\Plat de la Semaine\Plat De La Semaine.exe
set APP_PARENT_PATH=%AppData%\Plat de la Semaine

:: Colors
set GREEN=\\033[1;32m
set RED=\\033[1;31m
set RESET=\\033[0m

:: Check for errors
:check_error
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ %~1% %RESET%
    exit /b 1
)
goto :eof

:: Download the installer
echo %GREEN%📥 Téléchargement de Plat de la Semaine...%RESET%
powershell -Command "(New-Object Net.WebClient).DownloadFile('%INSTALLER_URL%', '%INSTALLER_PATH%')"
call :check_error "Échec du téléchargement. Vérifiez votre connexion Internet."

:: Stop the app if running
echo %GREEN%🔨 Fermeture de l'application existante...%RESET%
taskkill /F /IM PlatDeLaSemaine.exe > nul 2>&1

:: Remove old version if it exists
if exist "%APP_PATH%" (
    echo %GREEN%🗑️ Suppression de l'ancienne version...%RESET%
    rmdir /S /Q "%APP_PARENT_PATH%"
    call :check_error "Échec de la suppression de l'ancienne version."
)

:: Run the installer
echo %GREEN%🚀 Installation en cours...%RESET%
move /Y "%INSTALLER_PATH%" "%APP_PARENT_PATH%"
call :check_error "Échec de l'installation."

:: Launch the application

echo %GREEN%✅ Plat de la Semaine a été correctement installé !%RESET%
start "" "%APP_PATH%"


endlocal
