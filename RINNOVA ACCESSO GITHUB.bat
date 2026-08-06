@echo off
chcp 65001 >nul
title Rinnova l'accesso a GitHub
cd /d "%~dp0"
python rinnova_accesso.py
echo.
pause
