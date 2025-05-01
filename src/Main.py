import os
import datetime
import sys
import subprocess
import exiftool

from src.Reporter import Reporter
from src.Cleaner import Cleaner
from src.SupportedExtensions import SupportedExtensions
from src.SensitivePatterns import SensitivePatterns
from src.Messages import Messages
from src.ParameterValidator import ParameterValidator

class Main: 
    """
    Clase principal que coordina las operaciones de análisis y manipulación de metadatos.
    
    Esta clase actúa como punto de entrada principal y coordina las diferentes
    funcionalidades del sistema, delegando tareas específicas a clases especializadas.
    """
    
    def __init__(self, args):
        """
        Inicializa la instancia principal con los argumentos proporcionados.
        
        Args:
            args (dict): Diccionario con los argumentos de configuración
        """
        self._initialize_paths(args)
        self._initialize_components()
        self._setup_extensions_and_patterns()        
        
        
    def _initialize_paths(self, args):
        """Inicializa las rutas de entrada y salida."""
        src_path = args.get('input_path')
        out_path = args.get('output_path')
        verbose  = args.get('verbose', False)
        
        self.src_path = src_path
        self.out_path = out_path if out_path is not None else "./"
        self.verbose = verbose
        self.args = args 
        
        # Crear el directorio de salida si no existe
        ParameterValidator.validate_path(self.out_path, create_if_missing=True)
        
    def _initialize_components(self):
        """Inicializa los componentes especializados del sistema."""
        self.reporter = Reporter(self)
        self.cleaner = Cleaner(self)
        
    def _setup_extensions_and_patterns(self):
        """Configura las extensiones soportadas y patrones sensibles."""
        self.extensions = SupportedExtensions.get_all_extensions()
        self.sensitive_patterns = SensitivePatterns.get_all_patterns()
        self.negative_patterns = SensitivePatterns.get_negative_patterns()

    # ===== Métodos de Inspección y Análisis =====
    
    def inspect(self, fn): 
        """
        Inspecciona un archivo y devuelve sus metadatos.
        
        Args:
            fn: Ruta al archivo a inspeccionar
            
        Returns:
            dict: Metadatos del archivo
        """
        try:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(fn)
                return metadata
        except Exception as e:
            return {"error": str(e)}
            
    def report(self):
        """
        Genera un informe de metadatos para los archivos en el directorio especificado.
        
        Returns:
            tuple: (ruta al archivo markdown, ruta al archivo pdf) o (None, None) en caso de error
        """

        pdf_value = self.args.get ('pdf', False)
        html_value = self.args.get ('html', False)
        only_sensitive = self.args.get ('only_sensitive', False)
        
        self.args['pdf'] = pdf_value
        self.args['html'] = html_value
        self.args['only_sensitive'] = only_sensitive

        Messages.print_debug(Messages.DEBUG_PDF_ENABLED, pdf_value, verbose=self.verbose)
        Messages.print_debug(Messages.DEBUG_HTML_ENABLED, html_value, verbose=self.verbose)
        
        if only_sensitive:
            Messages.print_info("Generando informe solo con datos sensibles")
            
        # Inicializar estructura para el informe
        metadata_info = self._initialize_metadata_info()
        
        # Procesar el directorio y generar el informe
        self.reporter._process_directory_for_report(self.src_path, metadata_info)
        return self.reporter.generate_report(self.src_path, metadata_info)
        
    
    def _initialize_metadata_info(self):
        """Inicializa la estructura para almacenar la información de metadatos."""
        return {
            'total_files': 0,
            'files_with_metadata': 0,
            'files_with_sensitive': 0,
            'extensions_stats': {},
            'files_info': []
        }

    # ===== Métodos de Limpieza =====    
    def wipe(self):
        """
        Limpia los metadatos de los archivos en el directorio especificado.
        
        Returns:
            bool: True si se completó la limpieza correctamente, False en caso contrario
        """
        return self.cleaner.clean_metadata(self.src_path)

    # ===== Métodos de Información =====
        
    def show_supported_extensions(self):
        """Muestra las extensiones soportadas agrupadas por tipo."""
        print(SupportedExtensions.print_extensions_by_type())
        
    def show_sensitive_patterns(self):
        """Muestra los patrones sensibles agrupados por idioma."""
        print(SensitivePatterns.print_patterns_by_language())
        
    def print_version(self):
        """Muestra la versión de la aplicación."""
        print("MetaInfo versión 1.0.0")