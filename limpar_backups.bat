@echo off
title Cortana - Limpar backups antigos
color 0B
cd /d "%~dp0"

echo Apagando backups antigos...
del /Q wiki_local.backup_*.json 2>nul

if errorlevel 1 (
    echo Nenhum backup com data para apagar.
) else (
    echo Backups apagados.
)

echo.
echo Backup atual mantido: wiki_local.backup.json
echo.
pause
