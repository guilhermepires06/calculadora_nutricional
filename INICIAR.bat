@echo off
chcp 65001 > nul
title Planejamento Nutricional
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 (
    echo Python nao foi encontrado.
    echo Instale o Python e marque a opcao "Add Python to PATH".
    pause
    exit /b 1
)

echo Instalando/verificando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Nao foi possivel instalar o Flask.
    pause
    exit /b 1
)

echo.
echo Sistema disponivel em: http://127.0.0.1:5000
start "" http://127.0.0.1:5000
python app.py
pause
