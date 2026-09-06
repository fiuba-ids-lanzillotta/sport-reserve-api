#!/bin/bash

set -e

echo "=== Configuración del ambiente con pipenv ==="

# Verificar e instalar Python, pip y dependencias si es necesario
if ! command -v python3 &> /dev/null; then
    echo "Python3 no está instalado. Instalando..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-full
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo "No se pudo instalar Python3. Por favor, instálalo manualmente."
        exit 1
    fi
else
    echo "✓ Python3 ya está instalado: $(python3 --version)"
fi

# Verificar e instalar pipx si es necesario (para instalar pipenv de forma segura)
if ! command -v pipx &> /dev/null; then
    echo "pipx no está instalado. Instalando..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y pipx
    elif command -v yum &> /dev/null; then
        sudo yum install -y pipx
    elif command -v brew &> /dev/null; then
        brew install pipx
    fi
else
    echo "✓ pipx ya está instalado: $(pipx --version)"
fi

# Verificar e instalar pipenv si es necesario
if ! command -v pipenv &> /dev/null; then
    echo "pipenv no está instalado. Instalando con pipx..."
    pipx install pipenv
    # Asegurar que pipenv está en el PATH
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "✓ pipenv ya está instalado: $(pipenv --version)"
fi

# Crear el Pipfile desde requirements.txt si no existe
if [ ! -f "Pipfile" ]; then
    echo "Creando Pipfile..."
    pipenv install --requirements requirements.txt
    echo "✓ Pipfile creado e instaladas dependencias"
else
    echo "✓ El Pipfile ya existe"
    echo "Instalando dependencias con pipenv..."
    pipenv install
fi

# Mostrar información final
echo ""
echo "=== ✓ Configuración completada ==="
echo "Para activar el ambiente virtual en futuras sesiones, ejecuta:"
echo "  pipenv shell"
echo ""
echo "Para desactivar el ambiente virtual, ejecuta:"
echo "  exit"
echo ""
echo "Iniciando la aplicación..."
echo ""

# Levantar la aplicación
pipenv run python app.py
