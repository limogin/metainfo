# Pruebas para Metainfo

Este directorio contiene pruebas unitarias y de integración para verificar la funcionalidad de Metainfo.

## Estructura

```
tests/
  ├── README.md              # Este archivo
  ├── run_tests.py           # Script para ejecutar todas las pruebas
  ├── test_metainfo.py       # Pruebas unitarias para Metainfo
  ├── test_integration.py    # Pruebas de integración
  └── test_files/            # Archivos de prueba
      ├── sample.py          # Script para generar archivos con metadatos simulados
      └── files/             # Archivos generados para pruebas
```

## Requisitos

Antes de ejecutar las pruebas, asegúrate de tener instaladas las dependencias necesarias:

```bash
pip install pillow exiftool pytest pytest-cov
```

## Ejecución de las pruebas

### Ejecutar todas las pruebas

```bash
python tests/run_tests.py
```

Este comando ejecutará todas las pruebas y mostrará un informe detallado.

### Ejecutar pruebas específicas

```bash
# Ejecutar solo pruebas unitarias
python -m unittest tests/test_metainfo.py

# Ejecutar solo pruebas de integración
python -m unittest tests/test_integration.py
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
pytest --cov=src tests/
```

## Notas adicionales

- Las pruebas de integración incluyen un caso que requiere que Metainfo esté instalado en el sistema. Si no está instalado, esta prueba se omitirá.
- Algunas pruebas utilizan mocks para simular comportamientos externos como exiftool. 