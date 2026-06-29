@echo off
set BD="%~dp0conhecimentoSIR"

if not exist %BD% (
    echo A base de dados ja nao existe.
    exit /b 0
)

echo A apagar base de dados ChromaDB...
rd /s /q %BD%

if exist %BD% (
    echo Erro: nao foi possivel apagar. O especialista.py pode estar em execucao.
) else (
    echo Base de dados apagada com sucesso.
)
