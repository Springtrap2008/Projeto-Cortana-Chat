@echo off
title Cortana - Limpeza geral
color 0B
cd /d "%~dp0"

echo ============================================
echo    LIMPEZA GERAL
echo ============================================
echo.

echo [1/4] Apagando __pycache__...
if exist "__pycache__" rmdir /S /Q "__pycache__"

echo [2/4] Apagando arquivos .pyc...
del /S /Q *.pyc 2>nul

echo [3/4] Apagando backups antigos...
del /Q wiki_local.backup_*.json 2>nul

echo [4/4] Apagando arquivo de falhas...
if exist "falhas.txt" del /Q "falhas.txt"

echo.
echo ============================================
echo  Pronto.
echo ============================================
echo.
echo Mantidos:
echo   - wiki_local.json (base de dados)
echo   - wiki_local.backup.json (backup)
echo   - memoria.json (suas contas)
echo   - diario.json (diario da Cortana)
echo   - cache_wiki.json (cache de busca)
echo.
pause
