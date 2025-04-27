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
        
        # Hacer una excepción para ciertas claves
        if key_str == 'author' and not any(pattern.lower() in val_str for pattern in self.sensitive_patterns):
            return False, []
            
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
            tuple: (ruta al archivo markdown, ruta al archivo pdf) o (None, None) en caso de error
        """
        # Inicializar estadísticas y colectores
        metadata_info = {
            'total_files': 0,
            'files_with_metadata': 0,
            'files_with_sensitive': 0,
            'extensions_stats': {},
            'files_info': []
        }
        
        # Procesar el directorio recursivamente
        self._process_directory_for_report(self.src_path, metadata_info)
        
        # Generar el informe utilizando el Reporter
        return self.reporter.generate_report(self.src_path, metadata_info)
    
    def _process_directory_for_report(self, directory, metadata_info):
        """
        Procesa recursivamente un directorio recopilando información de metadatos.
        
        Args:
            directory: Ruta al directorio a procesar
            metadata_info: Diccionario donde se almacena la información recopilada
        """
        lower_extensions = tuple(ext.lower() for ext in self.extensions)
        upper_extensions = tuple(ext.upper() for ext in self.extensions)
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path):
                # Verificar si el archivo tiene una extensión soportada
                ext = os.path.splitext(item_path)[1].lower()
                if ext and (item.lower().endswith(lower_extensions) or item.upper().endswith(upper_extensions)):
                    metadata_info['total_files'] += 1
                    print(f"Leyendo {item_path} ...")
                    
                    # Actualizar estadísticas de extensiones
                    if ext not in metadata_info['extensions_stats']:
                        metadata_info['extensions_stats'][ext] = {
                            'count': 0,
                            'with_metadata': 0,
                            'with_sensitive': 0
                        }
                    metadata_info['extensions_stats'][ext]['count'] += 1
                    
                    # Recopilar metadatos
                    metadata = self.inspect(item_path)
                    file_info = {
                        'file_path': item_path,
                        'total_metadata': 0,
                        'has_sensitive': False,
                        'metadata': []
                    }
                    
                    has_metadata = False
                    for data in metadata:
                        if hasattr(data, 'items') and callable(data.items):
                            for key, val in data.items():
                                has_metadata = True
                                file_info['total_metadata'] += 1
                                
                                # Verificar si es sensible
                                is_sensitive, matching_patterns = self._check_sensitive_data(key, val)
                                
                                metadata_entry = {
                                    'key': key,
                                    'value': val,
                                    'is_sensitive': is_sensitive,
                                    'matching_patterns': matching_patterns
                                }
                                file_info['metadata'].append(metadata_entry)
                                
                                if is_sensitive:
                                    file_info['has_sensitive'] = True
                    
                    # Solo incluir archivos con metadatos
                    if has_metadata:
                        metadata_info['files_with_metadata'] += 1
                        metadata_info['extensions_stats'][ext]['with_metadata'] += 1
                        
                        if file_info['has_sensitive']:
                            metadata_info['files_with_sensitive'] += 1
                            metadata_info['extensions_stats'][ext]['with_sensitive'] += 1
                        
                        # Incluir todos los archivos con metadatos
                        metadata_info['files_info'].append(file_info)
            
            elif os.path.isdir(item_path):
                # Procesar subdirectorios recursivamente
                self._process_directory_for_report(item_path, metadata_info)
        
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