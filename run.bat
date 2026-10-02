@echo off
title Minecraft 1.21 Auto-Miner Launcher
color 0A
echo ===================================================
echo   Minecraft 1.21 Auto-Miner - Запуск...
echo ===================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден на компьютере!
    echo Установите Python 3.9 или новее с официального сайта python.org
    pause
    exit /b
)

echo Проверка и установка зависимостей...
python -m pip install -r requirements.txt --quiet

echo.
echo Запуск приложения Minecraft Auto-Miner...
python main.py

pause
