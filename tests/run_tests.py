#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import subprocess

# Verificar que estamos usando Python 3
if sys.version_info[0] < 3:
    print("Error: Este script requiere Python 3.")
    print("Versión actual: Python {}.{}.{}".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    print("Por favor, ejecuta este script con Python 3:")
    print("  python3 tests/run_tests.py")
    sys.exit(1)

# Añadir la ruta raíz del proyecto al path para poder importar los módulos
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def check_dependencies():
    """
    Verifica que todas las dependencias necesarias estén instaladas.
    """
    check_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'check_dependencies.py')
    if os.path.exists(check_script):
        try:
            subprocess.check_call([sys.executable, check_script])
            return True
        except subprocess.CalledProcessError:
            print("Error al verificar dependencias. Algunas pruebas podrían fallar.")
            return False
    return True

def run_tests():
    """
    Ejecuta todas las pruebas en el directorio tests/
    """
    # Descubrir y cargar todas las pruebas
    loader = unittest.TestLoader()
    tests_dir = os.path.abspath(os.path.dirname(__file__))
    suite = loader.discover(tests_dir, pattern="test_*.py")
    
    # Ejecutar las pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Devolver un código de salida basado en el resultado
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    # Verificar dependencias primero
    if not check_dependencies():
        print("ADVERTENCIA: Algunas dependencias no están disponibles.")
        if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
            print("ADVERTENCIA: Se está ejecutando Python {}.{}, se recomienda Python 3.6+".format(
                sys.version_info[0], sys.version_info[1]))
    
    # Preparar archivos de prueba si es necesario
    test_files_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files', 'sample.py')
    if os.path.exists(test_files_script):
        print("Generando archivos de prueba...")
        try:
            exec(open(test_files_script).read())
        except Exception as e:
            print("Error al generar archivos de prueba: {}".format(str(e)))
            print("Algunas pruebas podrían fallar debido a la falta de archivos de prueba.")
    
    # Ejecutar pruebas
    print("\n===== Ejecutando pruebas =====\n")
    exit_code = run_tests()
    
    # Salir con el código apropiado
    sys.exit(exit_code) 