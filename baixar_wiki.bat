@echo off
title Cortana - Baixar Wiki Local
color 0B
cd /d "%~dp0"

echo ============================================
echo    CORTANA - DOWNLOAD DA WIKI
echo ============================================
echo.
echo   Este processo leva 30 a 60 minutos.
echo   Nao feche esta janela.
echo.
echo   Se interromper, pode rodar de novo depois.
echo   Ele retoma de onde parou.
echo.
echo ============================================
echo.

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado.
    echo Execute iniciar.bat primeiro.
    pause
    exit /b
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt

python baixar_wiki.py

echo.
echo ============================================
echo  Download finalizado. Pressione qualquer tecla.
echo ============================================
pause
