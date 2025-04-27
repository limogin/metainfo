import unittest
import os
import sys
import tempfile
import shutil
import subprocess
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
        
        # Copiar archivos de prueba si existen
        self.test_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files', 'files')
        if os.path.exists(self.test_files_dir):
            for file in os.listdir(self.test_files_dir):
                shutil.copy(
                    os.path.join(self.test_files_dir, file),
                    os.path.join(self.test_dir, file)
                )
        else:
            # Si no hay archivos de prueba, crear algunos
            with open(os.path.join(self.test_dir, 'test.txt'), 'w') as f:
                f.write('Archivo de prueba')
        
    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Eliminar los directorios temporales
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)
    
    @patch('sys.argv', ['metainfo.py', '--i', None, '--o', None, '--report_all'])
    def test_full_report_workflow(self):
        """Probar el flujo completo de generación de informe"""
        # Actualizar los argumentos con las rutas temporales
        sys.argv[2] = self.test_dir
        sys.argv[4] = self.output_dir
        
        # Instanciar Main directamente
        main = Main(self.test_dir, self.output_dir)
        main.args = type('Args', (), {
            'report_all': True,
            'report_sensitive': False,
            'only_sensitive': False,
            'md': True,
            'pdf': False,
            'verbose': True
        })
        
        # Ejecutar el reporte
        result = main.report()
        
        # Verificar que se generó el informe
        self.assertTrue(result, "La generación del informe falló")
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'report.md')), 
                      "No se generó el archivo report.md")
                      
        # Verificar que el informe contiene datos (podría estar vacío si no hay archivos)
        with open(os.path.join(self.output_dir, 'report.md'), 'r') as f:
            content = f.read()
            self.assertIn("METAINFO REPORT", content, "El informe no contiene el encabezado esperado")
    
    @patch('sys.argv', ['metainfo.py', '--i', None, '--o', None, '--report_sensitive'])
    def test_sensitive_report_workflow(self):
        """Probar el flujo de generación de informe solo con datos sensibles"""
        # Actualizar los argumentos con las rutas temporales
        sys.argv[2] = self.test_dir
        sys.argv[4] = self.output_dir
        
        # Instanciar Main directamente
        main = Main(self.test_dir, self.output_dir)
        main.args = type('Args', (), {
            'report_all': False,
            'report_sensitive': True,
            'only_sensitive': True,
            'md': True,
            'pdf': False,
            'verbose': True
        })
        
        # Parchar el método _check_sensitive_data para detectar algo como sensible
        original_check = main._check_sensitive_data
        
        def mock_check_sensitive(key, val):
            # Considerar cualquier clave que contenga "test" como sensible
            if "test" in str(key).lower() or "test" in str(val).lower():
                return True, ["test"]
            return original_check(key, val)
            
        main._check_sensitive_data = mock_check_sensitive
        
        # Añadir un archivo con contenido "sensible" para la prueba
        with open(os.path.join(self.test_dir, 'sensitive_test.txt'), 'w') as f:
            f.write('Este archivo contiene la palabra test')
        
        # Ejecutar el reporte
        result = main.report()
        
        # Verificar que se generó el informe
        self.assertTrue(result, "La generación del informe falló")
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'report.md')), 
                      "No se generó el archivo report.md")
                      
        # Verificar que el informe contiene la nota sobre datos sensibles
        with open(os.path.join(self.output_dir, 'report.md'), 'r') as f:
            content = f.read()
            self.assertIn("**Nota:** Este informe muestra SOLO los metadatos potencialmente sensibles", 
                         content, 
                         "El informe no contiene la nota sobre datos sensibles")
    
    @patch('sys.argv', ['metainfo.py', '--i', None, '--o', None, '--wipe_sensitive'])
    def test_wipe_sensitive_workflow(self):
        """Probar el flujo completo de limpieza de metadatos sensibles"""
        # Actualizar los argumentos con las rutas temporales
        sys.argv[2] = self.test_dir
        sys.argv[4] = self.output_dir
        
        # Instanciar Main directamente
        main = Main(self.test_dir, self.output_dir)
        main.args = type('Args', (), {
            'wipe_sensitive': True,
            'wipe_all': False,
            'only_sensitive': True,
            'verbose': True
        })
        
        # Ejecutar la limpieza
        result = main.wipe()
        
        # Verificar que la limpieza se completó
        self.assertTrue(result, "La limpieza de metadatos sensibles falló")
    
    @unittest.skipIf(not os.path.exists('/usr/local/bin/metainfo'), "Metainfo no está instalado")
    def test_command_line_execution(self):
        """Probar la ejecución desde línea de comandos (requiere instalación)"""
        # Construir y ejecutar el comando
        cmd = [
            'python', 
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metainfo.py')),
            '--i', self.test_dir,
            '--o', self.output_dir,
            '--report_all',
            '--verbose'
        ]
        
        try:
            # Ejecutar el comando y capturar la salida
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Verificar que la ejecución fue exitosa
            self.assertEqual(result.returncode, 0, 
                           "La ejecución falló con código {}, error: {}".format(result.returncode, result.stderr))
            
            # Verificar que se generó el informe
            self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'report.md')), 
                          "No se generó el archivo report.md")
        
        except subprocess.CalledProcessError as e:
            self.fail("La ejecución del comando falló: {}, salida: {}".format(str(e), e.stderr))
        except Exception as e:
            self.fail("Error inesperado: {}".format(str(e)))

if __name__ == '__main__':
    unittest.main() 