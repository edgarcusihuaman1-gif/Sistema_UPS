@echo off
TITLE Sistema TI - Control de UPS (Actualizacion Automatica)
color 0A
echo ========================================================
echo   INICIANDO SISTEMA TI - CONTROL DE UPS
echo   Monitoreando cambios en los archivos Excel...
echo ========================================================

:: Ejecuta Streamlit usando la ruta exacta de Python de tu usuario
python -m streamlit run app.py --server.runOnSave=true --server.fileWatcherType=watchdog

pause