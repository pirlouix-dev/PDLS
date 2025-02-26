#!/bin/sh
INSTALLER_URL="https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/MacOS.dmg"
INSTALLER_LOCATION="/private/tmp/PDLS_Installer.dmg"
OLD_APP_PATH="/Applications/Plat de la Semaine.app"
NEW_APP_PATH="/Volumes/Plat de la Semaine/Plat de la Semaine.app"
APP_PARENT_PATH="/Applications"
VOLUME_PATH="/Volumes/Plat de la Semaine"

GREEN_START="\033[1;32m"
YELLOW_START="\033[1;33m"
RED_START="\033[1;31m"
COLOR_STOP="\033[0m"

# Function to check for errors and exit if necessary
check_error() {
    if [ $? -ne 0 ]; then
        echo "${RED_START}$1${COLOR_STOP}"
        exit 1
    fi
}

echo "${GREEN_START}Téléchargement de Plat de la Semaine${COLOR_STOP}"
curl -s -o "$INSTALLER_LOCATION" "$INSTALLER_URL"
check_error "Échec du téléchargement. Vérifiez votre connexion Internet."

# Ensure the installer was actually downloaded
if [ ! -f "$INSTALLER_LOCATION" ]; then
    echo "${RED_START}Le fichier installé est introuvable. Veuillez réessayer.${COLOR_STOP}"
    exit 1
fi

echo "${GREEN_START}Montage du disque${COLOR_STOP}"
hdiutil attach "$INSTALLER_LOCATION" >/dev/null
check_error "Échec du montage du disque. Veuillez réessayer."

# Ensure the new app exists on the mounted volume
if [ ! -d "$NEW_APP_PATH" ]; then
    echo "${RED_START}Le volume ne contient pas l'application. Veuillez réessayer.${COLOR_STOP}"
    hdiutil detach "$VOLUME_PATH" >/dev/null 2>&1
    exit 1
fi

echo "${GREEN_START}Installation de la mise à jour${COLOR_STOP}"
cp -R "$NEW_APP_PATH" "$APP_PARENT_PATH"
check_error "Échec de l'installation. Veuillez réessayer."

hdiutil detach "$VOLUME_PATH" >/dev/null
touch "$OLD_APP_PATH"

echo "${GREEN_START}L'application a été correctement installée.${COLOR_STOP}"
