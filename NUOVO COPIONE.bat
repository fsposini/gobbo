@echo off
chcp 65001 >nul
title Nuovo copione per il Gobbo
cd /d "%~dp0"
python nuovo_copione.py
echo.
pause
