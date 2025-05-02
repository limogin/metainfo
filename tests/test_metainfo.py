#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open

# Añadir la ruta raíz del proyecto al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Main import Main
from src.SensitivePatterns import SensitivePatterns
from src.SupportedExtensions import SupportedExtensions
from src.Cleaner import Cleaner
from src.Reporter import Reporter

class TestMetaInfo(unittest.TestCase):
    
    def setUp(self):
        """Configuración previa a cada prueba"""
        # Crear un directorio temporal para las pruebas
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        
        # Crear algunos archivos de prueba con diferentes extensiones
        self.sample_files = {
            'document.pdf': b'%PDF-1.5\nTest Document',
            'image.jpg': b'\xff\xd8\xff\xe0\x00\x10JFIFTest Image',
            'text.txt': b'Este es un archivo de texto plano'
        }
        
        for filename, content in self.sample_files.items():
            with open(os.path.join(self.test_dir, filename), 'wb') as f:
                f.write(content)
                
        # Crear una instancia de Main para las pruebas
        args = {
            'input_path': self.test_dir,
            'output_path': self.output_dir,
            'verbose': True
        }
        self.main = Main(args)
        
    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Eliminar los directorios temporales
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)
        
    @patch('exiftool.ExifToolHelper')
    def test_inspect_file(self, mock_exiftool):
        """Probar la función de inspección de archivos"""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_exiftool.return_value.__enter__.return_value = mock_instance
        mock_instance.get_metadata.return_value = [{'SourceFile': 'test.jpg', 'EXIF:Make': 'Canon'}]
        
        # Ejecutar la función
        result = self.main.inspect(os.path.join(self.test_dir, 'image.jpg'))
        
        # Verificar resultado
        self.assertEqual(result, [{'SourceFile': 'test.jpg', 'EXIF:Make': 'Canon'}])
        
    def test_supported_extensions(self):
        """Probar la obtención de extensiones soportadas"""
        # Verificar que las extensiones comunes están incluidas
        extensions = SupportedExtensions.get_all_extensions()
        common_extensions = ['jpg', 'pdf', 'doc', 'png']
        
        for ext in common_extensions:
            self.assertIn(ext, extensions)
    
    def test_sensitive_patterns(self):
        """Probar la obtención de patrones sensibles"""
        # Verificar que los patrones comunes están incluidos
        patterns = SensitivePatterns.get_all_patterns()
        common_patterns = ['GPS', 'email', 'password', 'telefono']
        
        for pattern in common_patterns:
            self.assertTrue(any(pattern.lower() in p.lower() for p in patterns),
                           f"No se encontró el patrón '{pattern}' en los patrones sensibles")
    
    @patch('src.Reporter.Reporter._process_directory_for_report')
    @patch('src.Reporter.Reporter.generate_report')
    def test_report_generation(self, mock_generate_report, mock_process_directory):
        """Probar la generación de informes de manera simple"""
        # Configurar mocks
        mock_process_directory.return_value = None
        # El nombre real del archivo incluirá un timestamp, por lo que usamos patrones que coincidan
        mock_generate_report.return_value = (
            os.path.join(self.output_dir, "reports", "metadata_report_20230101_120000.md"),
            os.path.join(self.output_dir, "reports", "metadata_report_20230101_120000.pdf"),
            None
        )
        
        # Establecer argumentos
        self.main.args.update({
            'report_all': True,
            'md': True,
            'pdf': True
        })
        
        # Ejecutar la función
        result = self.main.report()
        
        # Verificar resultado
        self.assertTrue(result)
        mock_process_directory.assert_called_once()
        mock_generate_report.assert_called_once()

    @patch('src.Cleaner.Cleaner._process_directory')
    def test_metadata_cleaning(self, mock_process_directory):
        """Probar la limpieza de metadatos de manera simple"""
        # Configurar mock
        mock_process_directory.return_value = True
        
        # Establecer argumentos
        self.main.args.update({
            'wipe_all': True
        })
        
        # Ejecutar la función
        result = self.main.wipe()
        
        # Verificar resultado
        self.assertTrue(result)
        mock_process_directory.assert_called_once()

    @patch('subprocess.run')
    def test_clean_all_metadata_simple(self, mock_subprocess_run):
        """Prueba simple de limpieza de todos los metadatos"""
        # Configurar mock
        mock_subprocess_run.return_value.returncode = 0
        
        # Crear archivo para prueba
        test_file = os.path.join(self.test_dir, 'test.jpg')
        with open(test_file, 'wb') as f:
            f.write(b'Test file content')
        
        # Ejecutar función
        self.main.cleaner._clean_all_metadata(test_file)
        
        # Verificar que se llamó a subprocess.run
        mock_subprocess_run.assert_called()

if __name__ == '__main__':
    unittest.main() 