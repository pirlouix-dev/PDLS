@echo off
setlocal ENABLEEXTENSIONS

:: Variables
set INSTALLER_URL=https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/Windows.exe
set INSTALLER_PATH=%TEMP%\PDLS_Installer.exe
set APP_PATH=%ProgramFiles%\Plat de la Semaine\PlatDeLaSemaine.exe
set APP_PARENT_PATH=%ProgramFiles%\Plat de la Semaine

:: Colors
set GREEN=[92m
set RED=[91m
set RESET=[0m

:: Check for errors
:check_error
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ %~1%RESET%
    exit /b 1
)

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

:: Clean up
echo %GREEN%🧹 Nettoyage...%RESET%
del /F "%INSTALLER_PATH%"

:: Launch the application

echo %GREEN%✅ Plat de la Semaine a été correctement installé !%RESET%
start "" "%APP_PATH%"


endlocal
