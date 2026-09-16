@echo off
TITLE Sincronizar Excel con GitHub y la Nube
color 0B
echo ========================================================
echo   SUBIENDO CAMBIOS DE EXCEL A LA NUBE...
echo ========================================================

:: Agrega todos los archivos modificados (Excel y codigo)
git add .

:: Crea un registro con la fecha y hora actual
git commit -m "Actualizacion automatica de Excel: %date% %time%"

:: Sube los cambios a tu repositorio de GitHub
git push origin main

echo ========================================================
echo   ¡LISTO! Los cambios ya estan en GitHub. 
echo   Tu pagina en la nube se actualizara en un momento.
echo ========================================================
pause