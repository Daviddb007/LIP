@echo off
title Detener Servidor
echo.
echo Deteniendo servicios...
taskkill /f /im cloudflared.exe >nul 2>nul
taskkill /f /fi "WINDOWTITLE eq Laboratorio de Inteligencia Pública*" /im python.exe >nul 2>nul
echo Servicios detenidos.
timeout /t 2 /nobreak >nul
