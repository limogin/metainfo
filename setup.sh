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

# Verificar si se requieren dependencias de sistema para reportlab, pypandoc y pyyaml
echo "Verificando dependencias del sistema..."
if ! command -v pandoc &> /dev/null; then
    echo "pandoc no está instalado. Instalando..."
    sudo apt-get install -y pandoc
fi

# Verificar si tenemos texlive-xetex para la generación de PDF
if ! command -v xelatex &> /dev/null; then
    echo "XeLaTeX no está instalado. Instalando..."
    sudo apt-get install -y texlive-xetex texlive-latex-extra
fi

# Verificar explícitamente si PyYAML está instalado
if ! python3 -c "import yaml" &> /dev/null; then
    echo "PyYAML no está instalado. Instalando..."
    pip3 install PyYAML
fi

# Verificar explícitamente si Markdown está instalado
if ! python3 -c "import markdown" &> /dev/null; then
    echo "markdown no está instalado. Instalando..."
    pip3 install markdown
fi

# Dependencias para PIL/Pillow (si se usa para procesamiento de imágenes)
sudo apt-get install -y python3-dev python3-pip python3-setuptools python3-wheel
sudo apt-get install -y libjpeg-dev zlib1g-dev

# Limpiar compilaciones previas
echo "Limpiando compilaciones previas..."
rm -rf build dist __pycache__ *.spec

echo "Configuración completada" 