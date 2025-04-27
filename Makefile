# Makefile para el proyecto MetaInfo

.PHONY: all clean build run install requirements

# Variables
PYTHON = python
PIP = pip
MAIN = metainfo.py
OUTPUT = dist/metainfo
BINNAME = metainfo

# Target predeterminado
all: build

install: build
	sudo cp dist/$(BINNAME) /usr/local/bin/	

# Instalar dependencias
requirements:
	$(PIP) install -r requirements.txt
	$(PIP) install pyinstaller

# Construir el binario ejecutable
build:
	pyinstaller --clean --onefile --name $(BINNAME) --hidden-import=PIL --hidden-import=PIL._imagingtk --hidden-import=PIL._tkinter_finder $(MAIN)

# Ejecutar el programa
run:
	$(PYTHON) $(MAIN)

# Ejecutar el binario generado
run-bin:
	$(OUTPUT)

# Limpiar archivos generados
clean:
	rm -rf build dist __pycache__ *.spec

# Ayuda
help:
	@echo "Targets disponibles:"
	@echo "  all      - Construir el binario ejecutable (predeterminado)"
	@echo "  install  - Instalar el binario en /usr/local/bin/"
	@echo "  requirements  - Instalar todas las dependencias"
	@echo "  build    - Construir el binario ejecutable con PyInstaller"
	@echo "  run      - Ejecutar el programa con Python"
	@echo "  run-bin  - Ejecutar el binario generado"
	@echo "  clean    - Eliminar archivos generados"
	@echo "  help     - Mostrar esta ayuda" 