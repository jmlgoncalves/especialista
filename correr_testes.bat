@echo off
cd /d "%~dp0"
echo A correr testes do EspecialistaSIR...
echo.
python -m pytest test_especialista.py -v
echo.
pause
