#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys

# Añadir la ruta raíz del proyecto al path para poder importar los módulos
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

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
    # Preparar archivos de prueba si es necesario
    test_files_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files', 'sample.py')
    if os.path.exists(test_files_script):
        print("Generando archivos de prueba...")
        try:
            exec(open(test_files_script).read())
        except Exception as e:
            print("Error al generar archivos de prueba: {}".format(str(e)))
    
    # Ejecutar pruebas
    print("\n===== Ejecutando pruebas =====\n")
    exit_code = run_tests()
    
    # Salir con el código apropiado
    sys.exit(exit_code) 