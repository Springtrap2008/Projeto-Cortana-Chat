@echo off
title Cortana Chat - Inicializando
color 0B
cd /d "%~dp0"

echo ============================================
echo    CORTANA CHAT - INICIALIZANDO
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale em python.org
    pause
    exit /b
)

if not exist "venv" (
    echo [1/3] Criando ambiente virtual...
    python -m venv venv
)

echo [2/3] Instalando dependencias...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

if not exist "wiki_local.json" (
    echo.
    echo ============================================
    echo  AVISO: wiki_local.json NAO ENCONTRADO
    echo ============================================
    echo.
    echo  Sem esse arquivo, a Cortana so funciona ONLINE.
    echo  Para funcionar offline, execute: baixar_wiki.bat
    echo.
    timeout /t 5 /nobreak >nul
)

set "CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
)
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
)

echo [3/3] Iniciando servidor...

if defined CHROME (
    start "" cmd /c "timeout /t 3 >nul && start "" "%CHROME%" http://localhost:5000"
) else (
    start "" cmd /c "timeout /t 3 >nul && start http://localhost:5000"
)

python app.py

pause
