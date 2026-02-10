@echo off
REM Script para executar o Automatizador de Correios
REM Uso: execute_automator.bat

chcp 65001 >nul
title Automatizador de Correios - Sistema de Postagem e Coleta
color 0A

echo.
echo ================================================================================
echo              AUTOMATIZADOR DE CORREIOS EMPRESA
echo              Sistema de Postagem e Coleta Automatizado
echo ================================================================================
echo.
echo.

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERRO] Python não encontrado!
    echo.
    echo Por favor, instale o Python antes de continuar.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Ativa ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    echo [INFO] Ativando ambiente virtual...
    call venv\Scripts\activate.bat
    echo.
)

REM Verifica se as dependências estão instaladas
echo [INFO] Verificando dependências...
python -c "import selenium" 2>nul
if errorlevel 1 (
    color 0E
    echo.
    echo [AVISO] Dependências não instaladas!
    echo.
    set /p INSTALAR="Deseja instalar as dependências agora? (S/N): "
    if /I "%INSTALAR%"=="S" (
        echo.
        echo Instalando dependências...
        pip install -r requirements.txt
        if errorlevel 1 (
            color 0C
            echo.
            echo [ERRO] Falha ao instalar dependências!
            pause
            exit /b 1
        )
        color 0A
        echo.
        echo [OK] Dependências instaladas com sucesso!
    ) else (
        color 0C
        echo.
        echo [ERRO] As dependências são necessárias para executar o sistema.
        pause
        exit /b 1
    )
)

echo [OK] Dependências verificadas
echo.
echo ================================================================================
echo.
echo O sistema solicitará:
echo   1. Suas credenciais de acesso (usuário e senha)
echo   2. O caminho da planilha com os dados
echo.
echo Após fornecer as informações, pressione ENTER para iniciar.
echo.
echo ================================================================================
echo.
pause
cls

REM Executa o programa principal
color 0B
python main.py

REM Verifica o resultado da execução
if errorlevel 1 (
    color 0C
    echo.
    echo ================================================================================
    echo   [ERRO] O processamento foi encerrado com erros
    echo ================================================================================
) else (
    color 0A
    echo.
    echo ================================================================================
    echo   [OK] Processamento concluído com sucesso
    echo ================================================================================
)

echo.
echo Pressione qualquer tecla para fechar...
pause >nul
