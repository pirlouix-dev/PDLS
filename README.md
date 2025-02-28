# Installation de Plat de la Semaine

## Sur MacOS

### Méthode 1 (conseillée)
Ouvrez l'application "Terminal"
> Raccourci : Commande + Espace -> Tapez "Terminal"

Entrez la commande

    curl -s https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/MacOS.sh > PDLS_Script.sh; sh ./PDLS_Script.sh; rm ./PDLS_Script.sh

### Méthode 2 (déconseillée)
- Téléchargez l'installateur [ici](https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/MacOS.dmg)

- Ouvrez l'installateur

- Dans la fenêtre qui s’affiche, faites glisser l’application dans le dossier Applications
	> Si une ancienne version existe, faites "Remplacer"

- Ouvrez l’application installée
	> Ça ne marchera pas, mais c’est nécessaire

- Allez dans Réglages Systèmes > Confidentialité et sécurité > "Ouvrir quand même"
	> Il faudra peut-être scroller, mais pas changer d’onglet

## Sur Windows

### Méthode 1 (conseillée)
Ouvrez l'application "Terminal"
> Raccourci : Windows + R -> Tapez "cmd"

Entrez la commande

    curl -s -o PDLS_Installer.bat https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/Windows.bat && PDLS_Installer.bat && del PDLS_Installer.bat

### Méthode 2 (déconseillée)

- Téléchargez l'application [ici](https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Installers/Windows.exe)

- Persuadez votre navigateur internet de télécharger le fichier

- Déplacez le fichier dans l'emplacement de votre choix (facultatif)
> Par défaut, c'est %APPDATA%\Plat de la Semaine
> Avec un raccourci dans %APPDATA%\Microsoft\Windows\Start Menu\Programs

- Lancez le fichier
