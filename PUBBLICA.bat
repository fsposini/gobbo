@echo off
chcp 65001 >nul
title Gobbo - pubblica i copioni
cd /d "%~dp0"
python pubblica.py
echo.
pause
