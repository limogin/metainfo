import os
import datetime
import sys
import subprocess
try:
    import exiftool
    EXIFTOOL_AVAILABLE = True
except ImportError:
    EXIFTOOL_AVAILABLE = False
    from src.Messages import Messages
    Messages.print_error(Messages.ERROR_EXIFTOOL)

from src.Reporter import Reporter
from src.Cleaner import Cleaner
from src.SupportedExtensions import SupportedExtensions
from src.SensitivePatterns import SensitivePatterns
from src.Messages import Messages
from src.ParameterValidator import ParameterValidator

class Main: 

    def __init__(self, src_path, out_path):
        if src_path is None:
            Messages.print_error(Messages.ERROR_NO_INPUT_FOLDER)
            sys.exit(1)
            
        if not os.path.exists(src_path):
            Messages.print_error(Messages.ERROR_FOLDER_NOT_EXISTS, src_path)
            sys.exit(1)
            
        self.src_path = src_path
        self.out_path = out_path if out_path is not None else "./"
        
        # Crear el directorio de salida si no existe
        ParameterValidator.validate_path(self.out_path, create_if_missing=True)
            
        # Establecer las extensiones y patrones sensibles utilizando las clases de constantes
        self.extensions = SupportedExtensions.get_all_extensions()
        self.sensitive_patterns = SensitivePatterns.get_all_patterns()
        
        # Asignar la variable global EXIFTOOL_AVAILABLE como atributo de instancia
        self.EXIFTOOL_AVAILABLE = EXIFTOOL_AVAILABLE
        
        # Inicializar atributo args con valores por defecto
        self.args = ParameterValidator.create_default_args()
        Messages.print_debug(Messages.DEBUG_MAIN_INIT)
            
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
        # Depuración: Verificar si los argumentos están configurados correctamente
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        
        # Obtener valores de forma segura
        pdf_value = ParameterValidator.safe_get(self.args, 'pdf', False)
        html_value = ParameterValidator.safe_get(self.args, 'html', True)
        only_sensitive = ParameterValidator.safe_get(self.args, 'only_sensitive', False)
                
        Messages.print_debug(Messages.DEBUG_PDF_ENABLED, pdf_value, verbose=verbose)
        Messages.print_debug(Messages.DEBUG_HTML_ENABLED, html_value, verbose=verbose)
        
        if only_sensitive:
            Messages.print_info("Generando informe solo con datos sensibles")
            
        # Asegurar que Reporter tenga acceso a estos argumentos
        if ParameterValidator.safe_get(self, 'reporter', None) is not None:
            # Para asegurar que los args se pasan correctamente, hacer una asignación explícita
            self.reporter.args = self.args
            
            # Verificar que el valor de pdf se mantiene en reporter.args
            reporter_pdf = ParameterValidator.safe_get(self.reporter.args, 'pdf', None)
            Messages.print_debug(f"DEBUG-Main-report - Valor PDF transmitido a Reporter: {reporter_pdf}", verbose=verbose)
            
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
        
        # Verificar una última vez que reporter.args contiene el valor correcto de pdf
        if hasattr(self.reporter, 'args') and hasattr(self.reporter.args, 'pdf'):
            reporter_pdf_final = self.reporter.args.pdf
            Messages.print_debug(f"DEBUG-Main-report - Valor final PDF en Reporter antes de generar reporte: {reporter_pdf_final}", verbose=verbose)
            
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
        only_sensitive = ParameterValidator.safe_get(self.args, 'only_sensitive', False)
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        
        if only_sensitive and verbose:
            Messages.print_debug("Procesando directorio con filtro de solo datos sensibles", verbose=True)
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path):
                # Verificar si el archivo tiene una extensión soportada
                ext = os.path.splitext(item_path)[1].lower()
                if ext and (item.lower().endswith(lower_extensions) or item.upper().endswith(upper_extensions)):
                    metadata_info['total_files'] += 1
                    Messages.print_debug(Messages.DEBUG_READING_FILE, item_path, verbose=verbose)
                    
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
                    has_sensitive_data = False
                    sensitive_metadata_count = 0
                    
                    for data in metadata:
                        if hasattr(data, 'items') and callable(data.items):
                            for key, val in data.items():
                                has_metadata = True
                                file_info['total_metadata'] += 1
                                
                                # Verificar si es sensible
                                is_sensitive, matching_patterns = self._check_sensitive_data(key, val)
                                
                                if is_sensitive:
                                    has_sensitive_data = True
                                    file_info['has_sensitive'] = True
                                    sensitive_metadata_count += 1
                                
                                # Si solo queremos datos sensibles, solo añadir los que son sensibles
                                if not only_sensitive or is_sensitive:
                                    metadata_entry = {
                                        'key': key,
                                        'value': val,
                                        'is_sensitive': is_sensitive,
                                        'matching_patterns': matching_patterns
                                    }
                                    file_info['metadata'].append(metadata_entry)
                    
                    # Solo incluir archivos con metadatos
                    if has_metadata:
                        metadata_info['files_with_metadata'] += 1
                        metadata_info['extensions_stats'][ext]['with_metadata'] += 1
                        
                        if has_sensitive_data:
                            metadata_info['files_with_sensitive'] += 1
                            metadata_info['extensions_stats'][ext]['with_sensitive'] += 1
                            
                            if only_sensitive and verbose:
                                Messages.print_debug(f"Archivo {item_path} contiene {sensitive_metadata_count} metadatos sensibles", verbose=True)
                        
                        # Si solo queremos datos sensibles, solo incluir archivos que tengan datos sensibles
                        if not only_sensitive or has_sensitive_data:
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