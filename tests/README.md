# Pruebas para Metainfo

Este directorio contiene pruebas unitarias y de integración para verificar la funcionalidad de Metainfo.

## Estructura

```
tests/
  ├── README.md                  # Este archivo
  ├── __init__.py                # Hace que tests sea un paquete Python
  ├── run_tests.py               # Script para ejecutar todas las pruebas
  ├── check_dependencies.py      # Script para verificar dependencias
  ├── test_metainfo.py           # Pruebas unitarias para Metainfo
  ├── test_integration.py        # Pruebas de integración
  └── test_files/                # Archivos de prueba
      ├── __init__.py            # Hace que test_files sea un paquete Python
      ├── sample.py              # Script para generar archivos con metadatos simulados
      └── files/                 # Archivos generados para pruebas
```

## Requisitos

Las dependencias necesarias para ejecutar las pruebas están definidas en `requirements-dev.txt`. Puedes instalarlas con:

```bash
pip install -r requirements-dev.txt
```

Las principales dependencias incluyen:

- **Pillow (PIL)**: Para el procesamiento de imágenes y generación de archivos de prueba
- **PyExifTool**: Para la manipulación de metadatos
- **PyYAML**: Para el procesamiento de archivos YAML
- **pytest/pytest-cov**: Para pruebas con cobertura
- **mock**: Para la simulación de objetos en pruebas

## Verificación automática de dependencias

El sistema ahora incluye verificación automática de dependencias:

1. **Script de verificación**: `check_dependencies.py` comprueba si todas las dependencias necesarias están instaladas y trata de instalar las que faltan automáticamente.

2. **Integración con Makefile**: Se ha añadido un objetivo `check-dependencies` al Makefile que verifica Pillow antes de ejecutar las pruebas.

3. **Verificación en tiempo de ejecución**: El script `run_tests.py` ahora verifica las dependencias antes de ejecutar las pruebas y muestra advertencias apropiadas.

Si alguna dependencia falta, el sistema intentará instalarla o mostrará un mensaje claro sobre lo que se necesita instalar.

## Ejecución de las pruebas

### Ejecutar todas las pruebas

```bash
# Usando make (recomendado)
make test

# O directamente
python tests/run_tests.py
```

### Ejecutar pruebas específicas

```bash
# Ejecutar solo pruebas unitarias
make test-unit

# Ejecutar solo pruebas de integración 
make test-integration

# Directamente con unittest
python -m unittest tests/test_metainfo.py
python -m unittest tests/test_integration.py
```

### Verificar dependencias manualmente

Si quieres verificar las dependencias sin ejecutar las pruebas:

```bash
# Usando make
make check-dependencies

# O directamente
python tests/check_dependencies.py
```

### Generar archivos de prueba

Los archivos de prueba con metadatos simulados se generan automáticamente al ejecutar `run_tests.py`. 
Si deseas generarlos manualmente:

```bash
python tests/test_files/sample.py
```

## Cobertura de código

Para generar un informe de cobertura de código, puedes utilizar pytest-cov:

```bash
# Usando make (recomendado)
make test-coverage

# O directamente con pytest
pytest --cov=src tests/
```

El informe HTML se generará en el directorio `htmlcov/`.

## Solución de problemas

### Error "No module named PIL"

Si encuentras este error, significa que Pillow no está instalado. Puedes solucionarlo de varias formas:

1. Ejecutar `make check-dependencies` para instalar automáticamente las dependencias faltantes
2. Instalar Pillow manualmente: `pip install pillow>=9.0.0`
3. Instalar todas las dependencias: `pip install -r requirements-dev.txt`

### Pruebas que fallan por falta de metainfo en el sistema

Las pruebas de integración incluyen una prueba que requiere que metainfo esté instalado en `/usr/local/bin/metainfo`. Esta prueba se omite automáticamente si metainfo no está instalado. Para instalar metainfo:

```bash
make install
```

## Notas adicionales

- Las pruebas de integración incluyen un caso que requiere que Metainfo esté instalado en el sistema. Si no está instalado, esta prueba se omitirá.
- Algunas pruebas utilizan mocks para simular comportamientos externos como exiftool.
- Se recomienda usar Python 3.6 o superior para evitar problemas de compatibilidad. 