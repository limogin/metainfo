#!/usr/bin/env python3
import os
import sys
import unittest

# Añadir la ruta raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Cargar los tests
from tests.test_metainfo import TestMetaInfo

if __name__ == '__main__':
    # Ejecutar los tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False) 