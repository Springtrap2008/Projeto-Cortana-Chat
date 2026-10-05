@echo off
title Cortana - Limpar Duplicatas
color 0B
cd /d "%~dp0"

call venv\Scripts\activate.bat
python limpar_duplicatas.py

pause
