#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import tempfile
import shutil
import subprocess
import glob
from unittest.mock import patch

# Añadir la ruta raíz del proyecto al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Main import Main

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        """Configuración previa a cada prueba"""
        # Crear directorios temporales para entrada y salida
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        
        # Crear algunos archivos de prueba simples
        with open(os.path.join(self.test_dir, 'test.txt'), 'w') as f:
            f.write('Archivo de prueba')
            
        with open(os.path.join(self.test_dir, 'test.jpg'), 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIFTest Image')
        
    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Eliminar los directorios temporales
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)
    
    def test_basic_report_workflow(self):
        """Prueba básica del flujo de generación de informe"""
        # Crear instancia de Main
        main = Main({
            'input_path': self.test_dir,
            'output_path': self.output_dir,
            'report_all': True,
            'md': True,
            'pdf': False,
            'verbose': True
        })
        
        # Ejecutar reporte con mock para evitar la dependencia real de exiftool
        with patch('exiftool.ExifToolHelper') as mock_exiftool:
            # Configurar mock
            mock_instance = mock_exiftool.return_value.__enter__.return_value
            mock_instance.get_metadata.return_value = [{'SourceFile': 'test.jpg', 'Author': 'Test'}]
            
            # Ejecutar reporte
            result = main.report()
            
            # Verificar resultado
            self.assertTrue(result, "La generación del informe falló")
            reports_dir = os.path.join(self.output_dir, 'reports')
            markdown_files = glob.glob(os.path.join(reports_dir, '*.md'))
            self.assertTrue(len(markdown_files) > 0, "No se generó ningún archivo de reporte en formato Markdown")

    def test_basic_clean_workflow(self):
        """Prueba básica del flujo de limpieza de metadatos"""
        # Crear instancia de Main
        main = Main({
            'input_path': self.test_dir,
            'output_path': self.output_dir,
            'wipe_all': True,
            'verbose': True
        })
        
        # Ejecutar limpieza con mocks
        with patch('subprocess.run') as mock_run, \
             patch('exiftool.ExifToolHelper') as mock_exiftool:
            
            # Configurar mocks
            mock_run.return_value.returncode = 0
            mock_instance = mock_exiftool.return_value.__enter__.return_value
            mock_instance.get_metadata.return_value = [{'SourceFile': 'test.jpg'}]
            
            # Ejecutar limpieza
            result = main.wipe()
            
            # Verificar resultado
            self.assertTrue(result, "La limpieza de metadatos falló")
            mock_run.assert_called()

if __name__ == '__main__':
    unittest.main() 