@echo off
title Cortana - Retraduzir pendentes
color 0B
cd /d "%~dp0"

echo ============================================
echo   CORTANA - RETRADUZIR PENDENTES
echo ============================================
echo.
echo   Retraduz os artigos que ficaram em ingles.
echo.
echo ============================================
echo.

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado.
    pause
    exit /b
)

call venv\Scripts\activate.bat

echo.
echo --- RELATORIO ---
python baixar_wiki.py --relatorio

echo.
echo --- RETRADUZINDO ---
python baixar_wiki.py --retry

pause
