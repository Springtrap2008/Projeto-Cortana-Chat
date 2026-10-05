@echo off
title Cortana - Relatorio da Wiki
color 0B
cd /d "%~dp0"

call venv\Scripts\activate.bat
python arrumar.py --só-relatorio

pause
