#!/bin/bash

# Instalar dependencias
echo "Instalando dependencias..."
pip3 install -r requirements.txt
pip3 install pyinstaller

# Verificar si exiftool está instalado
if ! command -v exiftool &> /dev/null; then
    echo "exiftool no está instalado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y libimage-exiftool-perl
fi

# Verificar si se requieren dependencias de sistema para reportlab y pypandoc
echo "Verificando dependencias del sistema..."
if ! command -v pandoc &> /dev/null; then
    echo "pandoc no está instalado. Instalando..."
    sudo apt-get install -y pandoc
fi

# Dependencias para PIL/Pillow (si se usa para procesamiento de imágenes)
sudo apt-get install -y python3-dev python3-pip python3-setuptools python3-wheel
sudo apt-get install -y libjpeg-dev zlib1g-dev

# Limpiar compilaciones previas
echo "Limpiando compilaciones previas..."
rm -rf build dist __pycache__ *.spec

echo "Configuración completada" 