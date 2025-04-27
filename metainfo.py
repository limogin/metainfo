# -*- coding: utf-8 -*-
import subprocess 
import os 
import sys

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
    
  def __init__ (self):
    parser = argparse.ArgumentParser(description="MetaInfo")
    parser.add_argument ("--i", nargs='?', help="path to folder to inspect")
    parser.add_argument ("--o", nargs='?', default="./", help="path to output folder (opcional, por defecto: carpeta actual)")
    parser.add_argument ("--wipe_all", action="store_true", default=False, help="wipe all metadata (default: False)")
    parser.add_argument ("--wipe_sensitive", action="store_true", default=False, help="wipe only sensitive metadata (default: False)")
    parser.add_argument ("--report_all", action="store_true", default=True, help="report all metadata (default: True)")
    parser.add_argument ("--report_sensitive", action="store_true", default=False, help="report only sensitive metadata (default: False)")
    parser.add_argument ("--verbose", action="store_true", dest="verbose", help="mostrar información detallada (default: False)")
    parser.add_argument ("--md", action="store_true", dest="md", default=True, help="generar informe en formato markdown (default: True)")
    parser.add_argument ("--html", action="store_true", dest="html", default=False, help="generar informe en formato HTML (default: False)")
    parser.add_argument ("--pdf", action="store_true", dest="pdf", default=False, help="generar informe en formato pdf (default: False)")
    parser.add_argument ("--show_mimes", action="store_true", default=False, help="mostrar mimes soportados y sale del programa (default: False)")
    parser.add_argument ("--show_patterns", action="store_true", default=False, help="mostrar solo los patrones de búsqueda considerados sensibles y sale del programa (default: False)")
    parser.add_argument("--version", 
                        action="version",
                        version=f"%(prog)s {VERSION}",
                        help="Mostrar versión del programa")
    
    # Nota sobre formatos de salida
    parser.epilog = Messages.INFO_REPORT_FORMATS
    
    args = parser.parse_args()
    self.parser = parser
    self.args = args 
    self.verbose = args.verbose

    # Asegurarse de que se han establecido valores por defecto para todos los parámetros importantes
    # Hacerlo una vez al inicio para no repetir verificaciones
    ParameterValidator.ensure_attr(self.args, 'pdf', False)
    ParameterValidator.ensure_attr(self.args, 'html', False) 
    ParameterValidator.ensure_attr(self.args, 'verbose', False)
    ParameterValidator.ensure_attr(self.args, 'only_sensitive', False)
    
    # Determinar si se está generando un informe solo con datos sensibles
    if ParameterValidator.safe_get(self.args, 'report_sensitive', False):
        self.args.only_sensitive = True
        self.args.report_all = False

    # Configuración de depuración inicial
    pdf_value = ParameterValidator.safe_get(self.args, 'pdf', False)
    html_value = ParameterValidator.safe_get(self.args, 'html', False)
    Messages.print_debug(Messages.DEBUG_ARGS_SETUP, pdf_value, html_value, verbose=self.verbose)

    # Verificar la solicitud de PDF y su viabilidad
    if pdf_value:
        try:
            pandoc_version = subprocess.run(
                ["pandoc", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.debug("Pandoc encontrado: " + pandoc_version.stdout.splitlines()[0])
        except (subprocess.SubprocessError, FileNotFoundError):
            Messages.print_error(Messages.ERROR_MISSING_PANDOC)
            self.args.pdf = False
        
        # Si se activó PDF, también activar HTML como respaldo
        if self.args.pdf:
            self.args.html = True

    # Crear la instancia principal y pasar todos los argumentos una sola vez
    self.main = Main(self.args.i, self.args.o)
    self.main.args = self.args
    
    # Iniciar procesamiento
    self.process()   
    
  def help (self):      
      self.parser.print_help()

  def debug (self, s, e=False):
      if self.verbose:
        if e:
            Messages.print_error(s)
            self.help()
            sys.exit(1) 
        else:
            Messages.print_info(s)

  def process (self):
      # Verificar que self.args existe
      if not ParameterValidator.safe_get(self, 'args', None):
          Messages.print_error(Messages.ERROR_NO_ARGS)
          return
          
      # Procesar comandos utilitarios que finalizan la ejecución
      if self.args.show_patterns:
         self.main.show_sensitive_patterns()
         sys.exit(0)
      elif self.args.show_mimes:
         self.main.show_supported_extensions()
         sys.exit(0)
      
      # Procesar comandos de limpieza
      if self.args.wipe_all:
          self.main.wipe()
      elif self.args.wipe_sensitive:
          self.main.wipe()
      # Por defecto, generar informe
      else:
          # Depuración final antes de generar el informe
          Messages.print_debug(f"DEBUG-metainfo - PDF activado: {self.args.pdf}", verbose=self.verbose)
          Messages.print_debug(f"DEBUG-metainfo - HTML activado: {self.args.html}", verbose=self.verbose)
          Messages.print_debug(f"DEBUG-metainfo - Solo datos sensibles: {self.args.only_sensitive}", verbose=self.verbose)
          
          # Generar informe
          md_path, pdf_path = self.main.report()
          
          # Informar sobre el resultado
          if md_path is None:
              Messages.print_error(Messages.ERROR_REPORT_GENERATION)
          elif self.args.pdf and pdf_path is None:
              html_path = f"{os.path.splitext(md_path)[0]}.html"
              if os.path.exists(html_path):
                  Messages.print_error(Messages.ERROR_PDF_GENERATION, md_path, html_path)
              else:
                  Messages.print_error(Messages.ERROR_PDF_GENERATION, md_path, "No disponible")
  
           
def main(): 
    mn = MetaInfo()
    
if __name__ == "__main__":
    main() 

