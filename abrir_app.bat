@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo Calendario da Copa 2026 - Inicializador
echo ===============================================

where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python 3.11 ou superior e marque a opcao "Add Python to PATH".
    pause
    exit /b 1
)

python --version

if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ERRO: nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERRO: nao foi possivel ativar o ambiente virtual.
    pause
    exit /b 1
)

echo Instalando/validando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: falha ao instalar dependencias.
    pause
    exit /b 1
)

echo Validando dados...
python scripts\validate_data.py
if errorlevel 1 (
    echo ERRO: os dados JSON falharam na validacao.
    pause
    exit /b 1
)

echo Abrindo aplicativo...
python main.py
if errorlevel 1 (
    echo ERRO: o aplicativo encerrou com falha.
    pause
    exit /b 1
)

pause
