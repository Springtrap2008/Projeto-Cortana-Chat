@echo off
title Cortana - Limpar Erros
color 0B
cd /d "%~dp0"

echo ============================================
echo   CORTANA - LIMPAR ENTRADAS ERRADAS
echo ============================================
echo.

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado.
    pause
    exit /b
)

call venv\Scripts\activate.bat

python limpar_errados.py

pause
