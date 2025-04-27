import os
import datetime
import sys
import subprocess
try:
    import exiftool
    EXIFTOOL_AVAILABLE = True
except ImportError:
    EXIFTOOL_AVAILABLE = False
    print("exiftool no está disponible. La funcionalidad será limitada.")

from src.Reporter import Reporter
from src.Cleaner import Cleaner
from src.SupportedExtensions import SupportedExtensions
from src.SensitivePatterns import SensitivePatterns

class Main: 

    def __init__(self, src_path, out_path):
        if src_path is None:
            print("Error: No se ha especificado la carpeta de entrada. Use --i ruta_carpeta")
            sys.exit(1)
            
        if not os.path.exists(src_path):
            print(f"Error: La carpeta {src_path} no existe")
            sys.exit(1)
            
        self.src_path = src_path
        self.out_path = out_path if out_path is not None else "./"
        
        # Crear el directorio de salida si no existe
        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)
            
        # Establecer las extensiones y patrones sensibles utilizando las clases de constantes
        self.extensions = SupportedExtensions.get_all_extensions()
        self.sensitive_patterns = SensitivePatterns.get_all_patterns()
            
        # Inicializar los manejadores especializados
        self.reporter = Reporter(self)
        self.cleaner = Cleaner(self)

    def inspect(self, fn): 
        """
        Inspecciona un archivo y devuelve sus metadatos.
        
        Args:
            fn: Ruta al archivo a inspeccionar
            
        Returns:
            dict: Metadatos del archivo
        """
        if not EXIFTOOL_AVAILABLE:
            return {"error": "exiftool no está disponible"}
            
        try:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(fn)
                return metadata
        except Exception as e:
            return {"error": str(e)}
        
    def _check_sensitive_data(self, key, val):
        """
        Verifica si una clave o valor contiene datos sensibles.
        
        Args:
            key: Clave del metadato
            val: Valor del metadato
            
        Returns:
            tuple: (es_sensible, patrones_coincidentes)
                - es_sensible: True si se encontró un patrón sensible
                - patrones_coincidentes: Lista de patrones que coincidieron
        """
        # Convertir clave y valor a string para poder buscar coincidencias
        key_str = str(key).lower()
        val_str = str(val).lower()
        
        # Verificar si algún patrón sensible coincide con la clave o el valor
        is_sensitive = False
        matching_patterns = []
        
        for pattern in self.sensitive_patterns:
            pattern_lower = pattern.lower()
            if pattern_lower in key_str or pattern_lower in val_str:
                is_sensitive = True
                matching_patterns.append(pattern)
        
        return is_sensitive, matching_patterns
        
    def report(self):
        """
        Genera un informe de metadatos para los archivos en el directorio especificado.
        
        Returns:
            bool: True si el informe se generó correctamente, False en caso contrario
        """
        return self.reporter.generate_report(self.src_path, self.out_path)
        
    def wipe(self):
        """
        Limpia los metadatos de los archivos en el directorio especificado.
        
        Returns:
            bool: True si se completó la limpieza correctamente, False en caso contrario
        """
        return self.cleaner.clean_metadata(self.src_path)
        
    def show_supported_extensions(self):
        """
        Muestra las extensiones soportadas agrupadas por tipo.
        """
        print(SupportedExtensions.print_extensions_by_type())
        
    def show_sensitive_patterns(self):
        """
        Muestra los patrones sensibles agrupados por idioma.
        """
        print(SensitivePatterns.print_patterns_by_language())