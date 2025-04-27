# -*- coding: utf-8 -*-
import subprocess 
import os 
import sys
import traceback

# Versión del programa
VERSION = "1.0.0"

# Verificar dependencias críticas
try:
    import yaml # pip install pyyaml 
except ImportError:
    from src.Messages import Messages
    Messages.print_error(Messages.ERROR_MISSING_YAML)
    sys.exit(1)

import argparse 
import shutil
import gzip
from src.Main import Main
from src.Messages import Messages
from src.ParameterValidator import ParameterValidator

class MetaInfo:
    
    def __init__(self, args=None):
        """
        Constructor de la clase MetaInfo.
        
        Args:
            args: Argumentos de línea de comandos
        """
        self.args = args or {}
        self.verbose = self.args.get('verbose', False)
        
        # Configuración de reportes
        self.markdown_enabled = self.args.get('markdown', True) 
        self.html_enabled = self.args.get('html', False)
        self.pdf_enabled = self.args.get('pdf', False)
        self.only_sensitive = self.args.get('report_sensitive', False)
        
        # Verificar si podemos generar PDFs
        if self.pdf_enabled:
            try:
                import pypandoc
                # Verificar si pandoc está instalado
                if self.verbose:
                    Messages.print_debug("Verificando si pandoc está instalado para generar PDF", verbose=True)
                result = subprocess.run(['pandoc', '--version'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
                if result.returncode != 0:
                    Messages.print_warning(Messages.WARNING_PANDOC_NOT_FOUND)
                    self.pdf_enabled = False
            except ImportError:
                Messages.print_warning(Messages.WARNING_PYPANDOC_NOT_FOUND)
                self.pdf_enabled = False
        
        if self.verbose:
            Messages.print_debug(f"Configuración de reportes - markdown: {self.markdown_enabled}, html: {self.html_enabled}, pdf: {self.pdf_enabled}, only_sensitive: {self.only_sensitive}", verbose=True)

    def process(self):
        """
        Procesa los argumentos de la línea de comandos.
        """
        if self.args is None:
            return
        
        args = self.args
        
        # Inicializar la clase Main con los argumentos
        main = Main(self.args)
        
        # Path de entrada
        input_path = args.get('input_path')
        
        # Mostrar versión
        if args.get('version'):
            main.print_version()
            return
        
        # Mostrar extensiones soportadas
        if args.get('show_supported'):
            main.display_supported_extensions()
            return
        
        # Mostrar patrones sensibles
        if args.get('show_sensitive'):
            main.display_sensitive_patterns()
            return
        
        # Verificar existencia de la ruta de entrada
        if not input_path:
            Messages.print_error(Messages.ERROR_NO_INPUT_PATH)
            return
        
        if not os.path.exists(input_path):
            Messages.print_error(Messages.ERROR_INPUT_NOT_EXISTS, input_path)
            return
        
        # Comando para generar reporte
        if args.get('report'):
            if self.verbose:
                Messages.print_debug(f"Generando reporte con configuración: markdown={self.markdown_enabled}, html={self.html_enabled}, pdf={self.pdf_enabled}, only_sensitive={self.only_sensitive}", verbose=True)
            
            main.report(
                markdown=self.markdown_enabled,
                html=self.html_enabled,
                pdf=self.pdf_enabled,
                only_sensitive=self.only_sensitive
            )
            return
        
        # Comando para limpiar metadatos
        if args.get('wipe'):
            main.wipe()
            return
        
        # Comando para limpiar solo metadatos sensibles
        if args.get('wipe_sensitive'):
            main.wipe_sensitive()
            return
        
        # Si no se especificó ningún comando, imprimir ayuda
        Messages.print_warning(Messages.WARNING_NO_ACTION)

def main(): 
    try:
        # Configurar el analizador de argumentos
        parser = argparse.ArgumentParser(description="MetaInfo - Herramienta para gestión de metadatos")
        parser.add_argument("--input_path", "--i", nargs='?', help="Ruta de la carpeta a inspeccionar")
        parser.add_argument("--output_path", "--o", nargs='?', default="./", help="Ruta de la carpeta de salida (opcional, por defecto: carpeta actual)")
        parser.add_argument("--wipe", "--wipe_all", action="store_true", default=False, help="Eliminar todos los metadatos (predeterminado: False)")
        parser.add_argument("--wipe_sensitive", action="store_true", default=False, help="Eliminar solo metadatos sensibles (predeterminado: False)")
        parser.add_argument("--report", "--report_all", action="store_true", default=True, help="Generar informe de todos los metadatos (predeterminado: True)")
        parser.add_argument("--report_sensitive", action="store_true", default=False, help="Generar informe solo de metadatos sensibles (predeterminado: False)")
        parser.add_argument("--verbose", action="store_true", default=False, help="Mostrar información detallada (predeterminado: False)")
        parser.add_argument("--markdown", "--md", action="store_true", default=True, help="Generar informe en formato Markdown (predeterminado: True)")
        parser.add_argument("--html", action="store_true", default=False, help="Generar informe en formato HTML (predeterminado: False)")
        parser.add_argument("--pdf", action="store_true", default=False, help="Generar informe en formato PDF (predeterminado: False)")
        parser.add_argument("--show_supported", "--show_mimes", action="store_true", default=False, help="Mostrar extensiones soportadas y salir (predeterminado: False)")
        parser.add_argument("--show_sensitive", "--show_patterns", action="store_true", default=False, help="Mostrar patrones considerados sensibles y salir (predeterminado: False)")
        parser.add_argument("--version", action="version", version="%(prog)s "+VERSION, help="Mostrar versión del programa")
        
        # Nota sobre formatos de salida
        parser.epilog = Messages.INFO_REPORT_FORMATS
        
        args = parser.parse_args()
        
        # Convertir los argumentos a un diccionario
        args_dict = vars(args)
        
        # Inicializar y procesar
        metainfo = MetaInfo(args_dict)
        metainfo.process()
        
    except Exception as e:
        Messages.print_error(f"Error inesperado: {str(e)}")
        if os.environ.get('DEBUG') == '1':
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 

