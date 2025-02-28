@echo off
setlocal EnableDelayedExpansion

:: Fonction :echo_utf8
:: Usage: call :echo_utf8 "Texte avec accents: é, è, à, ô, û, ç"
:echo_utf8
    rem Récupérer la page de code actuelle (ex: "Active code page: 850")
    for /f "tokens=4" %%a in ('chcp') do set "origCP=%%a"
    rem Passer temporairement en UTF-8
    chcp 65001 >nul
    rem Afficher le texte fourni en paramètre
    echo %~1
    rem Rétablir la page de code originale
    chcp %origCP% >nul
    goto :eof

:: Exemple d'utilisation :
call :echo_utf8 "Ceci est un texte avec des caractères accentués : é, è, à, ô, û, ç"
pause
