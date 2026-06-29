@echo off
echo === A iniciar EspecialistaSIR ===
echo.

call "%~dp0limpar_gpu.bat"
echo.

call "%~dp0limpar_bd.bat"
echo.

echo A arrancar especialista.py...
python "%~dp0especialista.py"
