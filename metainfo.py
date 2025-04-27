# -*- coding: utf-8 -*-
import subprocess 
import os 
import yaml # pip install pyyaml 
import argparse 
import shutil
import gzip
import sys 
from src.Main import Main
class MetaInfo:
    
  def __init__ (self):
    parser = argparse.ArgumentParser(description="MetaInfo")
    parser.add_argument ("--i", nargs='?', help="path to folder to inspect")
    parser.add_argument ("--o", nargs='?', default="./", help="path to output folder (opcional, por defecto: carpeta actual)")
    parser.add_argument ("--wipe_all", action="store_true", default=False, help="wipe all metadata (default: False)")
    parser.add_argument ("--wipe_sensitive", action="store_true", default=False, help="wipe only sensitive metadata (default: False)")
    parser.add_argument ("--report_all", action="store_true", default=True, help="report all metadata (default: True)")
    parser.add_argument ("--report_sensitive", action="store_true", default=False, help="report only sensitive metadata (default: False)")
    parser.add_argument ("--verbose", action="store_true", default=False, help="mostrar información detallada (default: False)")
    parser.add_argument ("--md", action="store_true", default=True, help="generar informe en formato markdown (default: True)")
    parser.add_argument ("--pdf", action="store_true", default=False, help="generar informe en formato pdf (default: False)")
    parser.add_argument ("--show_mimes", action="store_true", default=False, help="mostrar mimes soportados y sale del programa (default: False)")
    parser.add_argument ("--show_patterns", action="store_true", default=False, help="mostrar solo los patrones de búsqueda considerados sensibles y sale del programa (default: False)")
    
    args = parser.parse_args()
    self.parser = parser
    self.args = args 
    self.verbose = args.verbose

    self.main = Main(self.args.i, self.args.o)
    self.main.args = args
    self.process()   
    

  def help (self):      
      self.parser.print_help()

   
  def debug (self, s, e=False):
      if self.verbose:
        if e:
            print(s)
            self.help()
            sys.exit(1) 
        else:
            print(s)

  def process (self):     
     if (self.args.show_patterns):
        self.main.show_sensitive_patterns()
        sys.exit(0)
     elif (self.args.show_mimes):
        self.main.show_supported_extensions()
        sys.exit(0)
     elif (self.args.wipe_all):
         # Limpiar todos los metadatos
         self.args.only_sensitive = False
         self.main.wipe()
     elif (self.args.wipe_sensitive):
         # Limpiar solo metadatos sensibles
         self.args.only_sensitive = True
         self.main.wipe()
     else:
         # Determinar el tipo de reporte
         self.args.only_sensitive = self.args.report_sensitive
         self.main.report()
     
           
def main(): 
    mn = MetaInfo()
    
if __name__ == "__main__":
    main() 

