@echo off
setlocal
title NetScan — Network Anomaly Detection
cd /d "%~dp0"
python netscan.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo NetScan exited with error code %ERRORLEVEL%.
    pause
)
