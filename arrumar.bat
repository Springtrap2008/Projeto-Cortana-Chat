@echo off
title Cortana - Arrumar Wiki Local
color 0B
cd /d "%~dp0"

echo ============================================
echo    CORTANA - ARRUMAR WIKI LOCAL
echo ============================================
echo.
echo   Este script vai:
echo   1. Fazer backup do wiki_local.json
echo   2. Retraduzir artigos em ingles
echo   3. Remover artigos duplicados
echo.
echo   Pode demorar 15 a 30 minutos.
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

python arrumar.py

pause
