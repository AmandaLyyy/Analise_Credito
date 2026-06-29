@echo off
title ECIL - Sistema de Crédito
echo Iniciando o sistema ECIL...
echo.
cd /d "C:\Users\Micheli\Documents\CRÉDITOECIL\CreditoProjeto\CreditoProjetoI"
start "" "http://localhost:5000"
py app.py
pause