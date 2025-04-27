# Makefile para el proyecto MetaInfo

.PHONY: all clean build run install requirements test test-unit test-integration test-coverage

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

# Instalar dependencias de desarrollo
requirements-dev: requirements
	$(PIP) install -r requirements-dev.txt

# Construir el binario ejecutable
build:
	pyinstaller --clean --onefile --name $(BINNAME) --hidden-import=PIL --hidden-import=PIL._imagingtk --hidden-import=PIL._tkinter_finder $(MAIN)

# Ejecutar el programa
run:
	$(PYTHON) $(MAIN)

# Ejecutar el binario generado
run-bin:
	$(OUTPUT)

# Ejecutar todas las pruebas
test: requirements-dev
	$(PYTHON) tests/run_tests.py

# Ejecutar pruebas unitarias
test-unit: requirements-dev
	$(PYTHON) -m unittest tests/test_metainfo.py

# Ejecutar pruebas de integración
test-integration: requirements-dev
	$(PYTHON) -m unittest tests/test_integration.py

# Ejecutar pruebas con informe de cobertura
test-coverage: requirements-dev
	pytest --cov=src tests/
	coverage html
	@echo "Informe de cobertura generado en htmlcov/index.html"

# Limpiar archivos generados
clean:
	rm -rf build dist __pycache__ *.spec htmlcov .coverage .pytest_cache

# Ayuda
help:
	@echo "Targets disponibles:"
	@echo "  all      - Construir el binario ejecutable (predeterminado)"
	@echo "  install  - Instalar el binario en /usr/local/bin/"
	@echo "  requirements  - Instalar todas las dependencias"
	@echo "  requirements-dev  - Instalar dependencias de desarrollo y pruebas"
	@echo "  build    - Construir el binario ejecutable con PyInstaller"
	@echo "  run      - Ejecutar el programa con Python"
	@echo "  run-bin  - Ejecutar el binario generado"
	@echo "  test     - Ejecutar todas las pruebas"
	@echo "  test-unit - Ejecutar solo pruebas unitarias"
	@echo "  test-integration - Ejecutar solo pruebas de integración"
	@echo "  test-coverage - Ejecutar pruebas y generar informe de cobertura"
	@echo "  clean    - Eliminar archivos generados"
	@echo "  help     - Mostrar esta ayuda" 