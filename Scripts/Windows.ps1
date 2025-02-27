# Define paths and URLs
$installerUrl = "https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/WindowsInstaller.exe"
$installerLocation = "$env:TEMP\PDLS_Installer.exe"
$appPath = "$env:ProgramFiles\Plat de la Semaine\PlatDeLaSemaine.exe"
$appFolder = "$env:ProgramFiles\Plat de la Semaine"

# Color codes
$green = "`e[1;32m"
$yellow = "`e[1;33m"
$red = "`e[1;31m"
$reset = "`e[0m"

# Function to check for errors
function Check-Error {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$red$($args[0])$reset"
        exit 1
    }
}

# Download the installer
Write-Host "${green}Téléchargement de Plat de la Semaine${reset}"
Invoke-WebRequest -Uri $installerUrl -OutFile $installerLocation
Check-Error "Échec du téléchargement. Vérifiez votre connexion Internet."

# Ensure the installer was downloaded
if (!(Test-Path -Path $installerLocation)) {
    Write-Host "${red}Le fichier téléchargé est introuvable. Veuillez réessayer.${reset}"
    exit 1
}

# Stop the app if it's running
Write-Host "${green}Arrêt de l'application en cours d'exécution (si présente)${reset}"
Stop-Process -Name "PlatDeLaSemaine" -Force -ErrorAction SilentlyContinue

# Remove the old version if it exists
if (Test-Path -Path $appFolder) {
    Write-Host "${green}Suppression de l'ancienne version${reset}"
    Remove-Item -Recurse -Force $appFolder
    Check-Error "L'ancienne version n'a pas pu être supprimée. Veuillez réessayer."
}

# Run the installer silently (modify for your installer type)
Write-Host "${green}Installation de la nouvelle version${reset}"
Start-Process -FilePath $installerLocation -ArgumentList "/S" -Wait
Check-Error "Échec de l'installation. Veuillez réessayer."

# Clean up and relaunch the app
Remove-Item -Path $installerLocation -Force
Start-Process -FilePath $appPath

Write-Host "${green}Plat de la Semaine a été correctement installé${reset}"
