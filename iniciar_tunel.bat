@echo off
title Cortana - Tunel Remoto
color 0B
cd /d "%~dp0"

echo ============================================
echo    CORTANA - ACESSO REMOTO (Cloudflare)
echo ============================================
echo.

REM Verifica se cloudflared existe
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo [ERRO] cloudflared nao encontrado.
    echo Instale com: winget install Cloudflare.Cloudflared
    pause
    exit /b
)

echo [1/2] Iniciando servidor Cortana em segundo plano...

REM Inicia o Flask em segundo plano (mesma janela, sem bloquear)
start "Cortana Servidor" cmd /c "call venv\Scripts\activate.bat && python app.py"

echo [2/2] Aguardando servidor subir (5s)...
timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo   CRIANDO TUNEL PUBLICO...
echo ============================================
echo.
echo   Copie o endereco https://....trycloudflare.com
echo   que aparecera abaixo. Esse e o seu link.
echo.
echo   Pressione CTRL+C para encerrar o tunel.
echo ============================================
echo.

cloudflared tunnel --url http://localhost:5000

pause