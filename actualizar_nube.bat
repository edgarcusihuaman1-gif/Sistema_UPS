@echo off
TITLE Sincronizar Excel con GitHub y la Nube
color 0B
echo ========================================================
echo   GUARDANDO CAMBIOS LOCALES...
echo ========================================================

git add .
git commit -m "Guardado temporal antes de sincronizar: %date% %time%"

echo ========================================================
echo   DESCARGANDO CAMBIOS DE LA NUBE...
echo ========================================================

git pull origin main --rebase

echo ========================================================
echo   SUBIENDO TODO A LA NUBE...
echo ========================================================

git push origin main

echo ========================================================
echo   ¡LISTO! Los cambios ya estan en GitHub y la nube se 
echo   actualizara en un momento.
echo ========================================================
pause