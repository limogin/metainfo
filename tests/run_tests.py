#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas del proyecto.

Este script verifica primero las dependencias necesarias, luego corre las pruebas unitarias
y de integración, y finalmente genera un informe de cobertura de código.
"""

import os
import sys
import unittest
import subprocess

# Intentar importar termcolor, pero si no está disponible, crear una versión alternativa
try:
    from termcolor import colored
except ImportError:
    # Definir una función alternativa que simplemente devuelve el texto sin colorear
    def colored(text, color=None, on_color=None, attrs=None):
        return text

# Verificar que estamos usando Python 3
if sys.version_info[0] < 3:
    print("Error: Este script requiere Python 3.")
    print("Versión actual: Python {}.{}.{}".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    print("Por favor, ejecuta este script con Python 3:")
    print("  python3 tests/run_tests.py")
    sys.exit(1)

# Añadir la ruta raíz del proyecto al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar el verificador de dependencias
from tests.check_dependencies import check_dependencies

def run_unit_tests():
    """Ejecuta las pruebas unitarias y muestra los resultados."""
    print(colored("\n=== Ejecutando Pruebas Unitarias ===", "blue", attrs=["bold"]))
    
    # Descubrir y ejecutar todas las pruebas
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    
    # Mostrar resumen de resultados
    print("\nResumen de pruebas unitarias:")
    print(f"  Pruebas ejecutadas: {results.testsRun}")
    print(f"  Pruebas exitosas: {results.testsRun - len(results.failures) - len(results.errors)}")
    print(f"  Pruebas fallidas: {len(results.failures)}")
    print(f"  Pruebas con errores: {len(results.errors)}")
    
    return results.wasSuccessful()

def run_coverage():
    """Ejecuta el análisis de cobertura de código."""
    try:
        import coverage
        print(colored("\n=== Ejecutando Análisis de Cobertura ===", "blue", attrs=["bold"]))

        # Configurar y iniciar la medición de cobertura
        cov = coverage.Coverage(source=['src'], omit=['*/__pycache__/*', '*/tests/*'])
        cov.start()
        
        # Ejecutar las pruebas
        loader = unittest.TestLoader()
        suite = loader.discover(os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=0)
        runner.run(suite)
        
        # Detener la medición y generar informe
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory='coverage_report')
        
        print(f"\nInforme HTML de cobertura generado en: {os.path.abspath('coverage_report')}")
        return True
    except ImportError:
        print(colored("\nATENCIÓN: No se pudo ejecutar el análisis de cobertura porque el módulo 'coverage' no está instalado.", "yellow"))
        print("Para instalarlo, ejecute: 'pip install coverage'")
        return False
    except Exception as e:
        print(colored(f"\nError al ejecutar análisis de cobertura: {str(e)}", "red"))
        return False

def main():
    # Verificar dependencias necesarias
    dependencies_ok = check_dependencies()
    if not dependencies_ok:
        sys.exit(1)
    
    # Ejecutar las pruebas unitarias
    unittest_success = run_unit_tests()
    
    # Ejecutar análisis de cobertura
    coverage_success = run_coverage()
    
    # Determinar el estado de salida
    if not unittest_success:
        print(colored("\n⚠️  Algunas pruebas han fallado.", "red", attrs=["bold"]))
        sys.exit(1)
    else:
        print(colored("\n✅ Todas las pruebas han pasado correctamente.", "green", attrs=["bold"]))
        sys.exit(0)

if __name__ == "__main__":
    main() 