@echo off
TITLE Sincronizar Excel con GitHub y la Nube
color 0B
echo ========================================================
echo   SINCRONIZANDO CON GITHUB...
echo ========================================================

:: Descarga primero los cambios remotos para evitar conflictos
git pull origin main --rebase

echo ========================================================
echo   SUBIENDO TUS CAMBIOS DE EXCEL A LA NUBE...
echo ========================================================

:: Agrega todos los archivos modificados
git add .

:: Guarda los cambios localmente
git commit -m "Actualizacion automatica de Excel: %date% %time%"

:: Sube los cambios al repositorio
git push origin main

echo ========================================================
echo   ¡LISTO! Los cambios ya estan en GitHub y la nube se 
echo   actualizara en un momento.
echo ========================================================
pause