@echo off
title Laboratorio de Inteligencia Pública - Servidor
color 0A
cls
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  LABORATORIO DE INTELIGENCIA PÚBLICA     ║
echo  ╚══════════════════════════════════════════╝
echo.

:: Verificar que cloudflared esta instalado
where cloudflared >nul 2>nul
if %errorlevel% neq 0 (
    echo  [ERROR] cloudflared no esta instalado.
    echo  Instalar con: winget install Cloudflare.cloudflared
    echo.
    pause
    exit /b 1
)

:: Matar procesos anteriores
taskkill /f /im cloudflared.exe >nul 2>nul

echo  [1/2] Iniciando Cloudflare Tunnel...
echo.

:: Iniciar tunnel nombrado (usa config.yml automaticamente)
set PROJECT_DIR=%~dp0
start "Cloudflare Tunnel" /min cmd /c "cloudflared tunnel --config C:\Users\Usuario\.cloudflared\config_inteligenciapublica.yml run inteligenciapublica > "%PROJECT_DIR%tunnel.log" 2>&1"

:: Esperar a que el tunnel levante
echo  Esperando que el tunnel conecte...
timeout /t 6 /nobreak >nul

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║           URLs DEL SERVIDOR              ║
echo  ╠══════════════════════════════════════════╣
echo  ║  Local:   http://localhost:13000         ║
echo  ║  Publico: https://inteligenciapublica.stonelytics.tech ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  [2/2] Iniciando servidor Flask...
echo.

"%PROJECT_DIR%venv\Scripts\python.exe" run.py
