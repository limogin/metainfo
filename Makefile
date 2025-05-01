# Makefile para el proyecto MetaInfo

.PHONY: all clean build run install requirements test test-unit test-integration test-coverage pdf docx docs check-mermaid

# Variables
PYTHON = python3
PIP = pip3
MAIN = metainfo.py
OUTPUT = dist/metainfo
BINNAME = metainfo
DOCS_SRC = docs
DOCS_BUILD = docs/build
PANDOC = pandoc
PANDOC_OPTS = --toc --toc-depth=3 --number-sections

# Orden específico de archivos para la documentación
MD_FILES = $(DOCS_SRC)/README.md \
           $(DOCS_SRC)/indice.md \
		   $(DOCS_SRC)/indice_tecnico.md \
		   $(DOCS_SRC)/modelo_dominio.md \
		   $(DOCS_SRC)/arquitectura_capas.md \
		   $(DOCS_SRC)/arquitectura_modular.md \
		   $(DOCS_SRC)/diagrama_flujo_datos.md \
		   $(DOCS_SRC)/diagramas_interaccion.md \
           $(DOCS_SRC)/casos_uso.md \
           $(DOCS_SRC)/diagrama_componentes.md \
           $(DOCS_SRC)/diagrama_clases.md \
		   
		   

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

# Verificar dependencias críticas
check-dependencies:
	@echo "Verificando dependencias críticas..."
	@$(PYTHON) -c "import PIL" || (echo "Error: Pillow no está instalado. Instalando..." && $(PIP) install pillow>=9.0.0)
	@echo "Verificando versión de Python..."
	@$(PYTHON) -c "import sys; assert sys.version_info[0] >= 3, 'Se requiere Python 3+'; print('✓ Python {} detectado'.format(sys.version.split()[0]))"
	@echo "Dependencias OK"

# Verificar dependencias para documentación básica
check-docs-simple:
	@echo "Verificando pandoc..."
	@which $(PANDOC) > /dev/null || (echo "Error: Pandoc no está instalado. Por favor, instálelo con 'apt-get install pandoc' o similar"; exit 1)
	@echo "Pandoc disponible ✓"
	@echo "Archivos Markdown que se procesarán (en este orden):"
	@for file in $(MD_FILES); do echo "  - $$file"; done

# Verificar si mermaid-filter está disponible
check-mermaid: check-docs-simple
	@echo "Verificando mermaid-filter para Pandoc..."
	@pandoc -v | grep mermaid-filter > /dev/null 2>&1 || which mermaid-filter > /dev/null 2>&1 || npm list -g | grep mermaid-filter > /dev/null 2>&1 || ( \
		echo "⚠️  mermaid-filter no está instalado. Instalando..."; \
		npm install -g mermaid-cli; \
		npm install -g mermaid-filter; \
		echo "✓ mermaid-filter instalado."; \
	)
	@echo "✓ Herramientas de renderizado de Mermaid disponibles"

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
test: requirements-dev check-dependencies
	$(PYTHON) tests/run_tests.py

# Ejecutar pruebas unitarias
test-unit: requirements-dev check-dependencies
	$(PYTHON) -m unittest tests/test_metainfo.py

# Ejecutar pruebas de integración
test-integration: requirements-dev check-dependencies
	$(PYTHON) -m unittest tests/test_integration.py

# Ejecutar pruebas con informe de cobertura
test-coverage: requirements-dev check-dependencies
	$(PYTHON) -m pytest --cov=src tests/
	$(PYTHON) -m coverage html
	@echo "Informe de cobertura generado en htmlcov/index.html"

# Crear directorio para documentación
$(DOCS_BUILD):
	@mkdir -p $(DOCS_BUILD)

# Generar documentación en PDF con soporte para diagramas Mermaid
pdf: check-mermaid $(DOCS_BUILD)
	@echo "Generando documentación en PDF con diagramas Mermaid..."
	@$(PANDOC) $(PANDOC_OPTS) \
		--from=markdown \
		--output=$(DOCS_BUILD)/MetaInfo-Manual.pdf \
		--pdf-engine=xelatex \
		--variable geometry:margin=2.5cm \
		--variable colorlinks=true \
		-F mermaid-filter \
		--metadata title="Manual de MetaInfo" \
		--metadata author="Equipo de Desarrollo" \
		--metadata date="`date +'%d/%m/%Y'`" \
		$(MD_FILES)
	@echo "✓ Documentación PDF generada en $(DOCS_BUILD)/MetaInfo-Manual.pdf"

# Generar documentación en DOCX con soporte para diagramas Mermaid
docx: check-mermaid $(DOCS_BUILD)
	@echo "Generando documentación en DOCX con diagramas Mermaid..."
	@$(PANDOC) $(PANDOC_OPTS) \
		--from=markdown \
		--output=$(DOCS_BUILD)/MetaInfo-Manual.docx \
		-F mermaid-filter \
		--metadata title="Manual de MetaInfo" \
		--metadata author="Equipo de Desarrollo" \
		--metadata date="`date +'%d/%m/%Y'`" \
		$(MD_FILES)
	@echo "✓ Documentación DOCX generada en $(DOCS_BUILD)/MetaInfo-Manual.docx"

# Generar toda la documentación
docs: pdf docx
	@echo "Generación de documentación completada."
	@echo "Los diagramas Mermaid han sido renderizados en los documentos."

# Limpiar archivos generados
clean:
	rm -rf build dist __pycache__ *.spec htmlcov .coverage .pytest_cache $(DOCS_BUILD)

# Ayuda
help:
	@echo "Targets disponibles:"
	@echo "  all      - Construir el binario ejecutable (predeterminado)"
	@echo "  install  - Instalar el binario en /usr/local/bin/"
	@echo "  requirements  - Instalar todas las dependencias"
	@echo "  requirements-dev  - Instalar dependencias de desarrollo y pruebas"
	@echo "  check-dependencies - Verificar dependencias críticas"
	@echo "  check-mermaid - Verificar e instalar mermaid-filter para diagramas"
	@echo "  build    - Construir el binario ejecutable con PyInstaller"
	@echo "  run      - Ejecutar el programa con Python"
	@echo "  run-bin  - Ejecutar el binario generado"
	@echo "  test     - Ejecutar todas las pruebas"
	@echo "  test-unit - Ejecutar solo pruebas unitarias"
	@echo "  test-integration - Ejecutar solo pruebas de integración"
	@echo "  test-coverage - Ejecutar pruebas con informe de cobertura"
	@echo "  pdf      - Generar documentación en PDF con diagramas Mermaid"
	@echo "  docx     - Generar documentación en DOCX con diagramas Mermaid"
	@echo "  docs     - Generar toda la documentación (PDF y DOCX)"
	@echo "  clean    - Eliminar archivos generados"
	@echo "  help     - Mostrar esta ayuda" 