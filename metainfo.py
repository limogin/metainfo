# -*- coding: utf-8 -*-
import subprocess 
import os 
import sys
import argparse 
import shutil
import gzip
from src.Main import Main
from src.Messages import Messages
from src.ParameterValidator import ParameterValidator

# Versión del programa
VERSION = "1.0.0"


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
        self.check_dependencies()
        
        if self.verbose:
            os.environ['DEBUG'] = '1'
            Messages.print_debug(f"Configuración de reportes - markdown: {self.markdown_enabled}, html: {self.html_enabled}, pdf: {self.pdf_enabled}, only_sensitive: {self.only_sensitive}", verbose=True)

    def check_dependencies(self): 
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
                sys.exit()

        try:
           import exiftool           
        except ImportError:           
           Messages.print_error(Messages.ERROR_EXIFTOOL, True)        
           sys.exit()
        
    def main(self): 
       try:
        # Configurar el analizador de argumentos
        parser = argparse.ArgumentParser(description="MetaInfo - Herramienta para gestión de metadatos")
        parser.add_argument("--input_path", "--i", nargs='?', help="Ruta de la carpeta a inspeccionar")
        parser.add_argument("--output_path", "--o", nargs='?', default="./", help="Ruta de la carpeta de salida (opcional, por defecto: carpeta actual)")
        parser.add_argument("--wipe", "--wipe_all", action="store_true", default=False, help="Eliminar todos los metadatos (predeterminado: False)")
        parser.add_argument("--wipe_sensitive", action="store_true", default=False, help="Eliminar solo metadatos sensibles (predeterminado: False)")
        parser.add_argument("--report", "--report_all", action="store_true", default=False, help="Generar informe de todos los metadatos (predeterminado: True)")
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
        self.parser = parser    
        
        # Parsear argumentos y asignarlos a self.args
        self.args = parser.parse_args()
        if self.args is None:
            Messages.print_error(Messages.ERROR_NO_ARGS)
            return
        # Convertir argumentos de Namespace a diccionario
        self.args = vars(self.args)
        if self.args is None:
            Messages.print_error(Messages.ERROR_NO_ARGS)
            return
        
        # Inicializar y procesar
        self.process()
        
       except Exception as e:
         Messages.print_error(f"Error inesperado: {str(e)}")
         if os.environ.get('DEBUG') == '1':
            import traceback
            traceback.print_exc()
         return 1
    
       return 0
    
    def help(self):
        self.parser.print_help()
        sys.exit()
        
    def process(self):
        """
        Procesa los argumentos de la línea de comandos.
        """
        
        input_path = self.args.get('input_path')
        out_path = self.args.get('output_path')
        verbose = self.args.get('verbose')
        if out_path is None: 
            out_path = "./"
            self.args.set('output_path', out_path)
        args = self.args    
        Messages.print_debug(f"Ruta de entrada: {input_path}", verbose=verbose)
        Messages.print_debug(f"Ruta de salida: {out_path}", verbose=verbose)
        # Verificar existencia de la ruta de entrada
        if not input_path:
            Messages.print_error(Messages.ERROR_NO_INPUT_PATH)
            return
        
        if not os.path.exists(input_path):
            Messages.print_error(Messages.ERROR_INPUT_NOT_EXISTS, input_path)
            return
       
        main = Main(args)
                        
        # Mostrar versión
        if args.get('version'):
            main.print_version()
            return
        # Mostrar extensiones soportadas
        if args.get('show_supported'):
            main.show_supported_extensions()
            return
        
        # Mostrar patrones sensibles
        if args.get('show_sensitive'):
            main.show_sensitive_patterns()
            return        
        
        # Comando para generar reporte
        if args.get('report') or args.get('report_all') or args.get('report_sensitive'):
            if self.verbose:
                Messages.print_debug(f"Generando informe con configuración: markdown={self.markdown_enabled}, html={self.html_enabled}, pdf={self.pdf_enabled}, only_sensitive={self.only_sensitive}", verbose=True)            
            main.report()
            return
        
        # Comando para limpiar metadatos
        if args.get('wipe') or args.get('wipe_all') or args.get('wipe_sensitive'):
            if (self.verbose):
                Messages.print_debug(f"Limpieza de metadatos con configuración: wipe={args.get('wipe')}, wipe_all={args.get('wipe_all')}, wipe_sensitive={args.get('wipe_sensitive')}", verbose=True)            
            main.wipe()
            return
        
               
        # Si no se especificó ningún comando, imprimir ayuda
        Messages.print_warning(Messages.WARNING_NO_ACTION, verbose=verbose)
        self.help()


if __name__ == "__main__":
    mn = MetaInfo()
    mn.main()

