import os
import datetime
import subprocess

class Reporter:
    """
    Clase responsable de generar informes de metadatos.
    """
    
    def __init__(self, main_instance):
        """
        Inicializa el Reporter con una referencia a la instancia principal.
        
        Args:
            main_instance: Instancia de la clase Main
        """
        self.main = main_instance
        self.args = main_instance.args if hasattr(main_instance, 'args') else None
        
    def generate_report(self, src_path, out_path):
        """
        Genera un informe de metadatos para los archivos en el directorio especificado.
        
        Args:
            src_path: Ruta al directorio a analizar
            out_path: Ruta donde se guardará el informe
            
        Returns:
            bool: True si el informe se generó correctamente, False en caso contrario
        """
        dst_fn_md = os.path.join(out_path, 'report.md')
        dst_fn_pdf = os.path.join(out_path, 'report.pdf')
        
        lower_extensions = tuple(self.main.extensions)
        upper_extensions = tuple(ext.upper() for ext in self.main.extensions)
        
        try:
            with open(dst_fn_md, "w") as f:
                f.write("# METAINFO REPORT\n")
                f.write(f"- Path: {src_path}\n\n")
                f.write(f"- Fecha: {datetime.datetime.now()}\n")
                
                # Añadir una nota si solo se reportan datos sensibles
                if self.args and self.args.only_sensitive:
                    f.write("\n> **Nota:** Este informe muestra SOLO los metadatos potencialmente sensibles.\n\n")
                    
                files_found, sensitive_found = self._process_directory(src_path, f, lower_extensions, upper_extensions)
                
                if not files_found:
                    f.write("\nNo se encontraron archivos con las extensiones soportadas.\n")
                    print("No se encontraron archivos con las extensiones soportadas.")
                elif self.args and self.args.only_sensitive and not sensitive_found:
                    f.write("\nNo se encontraron datos sensibles en los archivos analizados.\n")
                    print("No se encontraron datos sensibles en los archivos analizados.")
            
            print(f"Informe MD generado en: {dst_fn_md}")
            if self.args and self.args.pdf:
                if self._generate_pdf_report(dst_fn_md, dst_fn_pdf):
                  print(f"Informe PDF generado en: {dst_fn_pdf}") 
            return True
        
        except Exception as e:
            print(f"Error durante el procesamiento: {str(e)}")
            return False
    
    def _process_directory(self, directory, file_handle, lower_extensions, upper_extensions):
        """
        Procesa recursivamente un directorio y todos sus subdirectorios.
        
        Args:
            directory: Ruta al directorio a procesar
            file_handle: Manejador del archivo donde se escribe el informe
            lower_extensions: Tupla de extensiones en minúsculas
            upper_extensions: Tupla de extensiones en mayúsculas
            
        Returns:
            bool: True si se encontraron archivos, False en caso contrario
        """
        files_found = False
        sensible_data_found = False
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path) and (item.lower().endswith(lower_extensions) or item.upper().endswith(upper_extensions)):
                print(f"Leyendo {item_path} ...")
                files_found = True
                metadata = self.main.inspect(item_path)
                
                # Verificar si hay datos sensibles antes de escribir la cabecera del archivo
                has_sensitive_data = False
                if self.args and self.args.only_sensitive:
                    for d in metadata:
                        if hasattr(d, 'items') and callable(d.items):
                            for key, val in d.items():
                                is_sensitive, _ = self.main._check_sensitive_data(key, val)
                                if is_sensitive:
                                    has_sensitive_data = True
                                    break
                            if has_sensitive_data:
                                break
                else:
                    has_sensitive_data = True  # Si no estamos filtrando, siempre mostramos el archivo
                
                # Solo escribir la cabecera y procesar si hay datos sensibles o no estamos filtrando
                if has_sensitive_data:
                    sensible_data_found = sensible_data_found or has_sensitive_data
                    file_handle.write(f"\n## {item_path}\n")
                    
                    for d in metadata:
                        if hasattr(d, 'items') and callable(d.items):
                            for key, val in d.items():
                                # Comprobar si contiene datos sensibles
                                is_sensitive, matching_patterns = self.main._check_sensitive_data(key, val)
                                
                                # Marcar el campo como sensible si se encontró una coincidencia
                                if is_sensitive:
                                    file_handle.write(f"- {key}: {val} ⚠️ **[DATO POTENCIALMENTE SENSIBLE: {', '.join(matching_patterns)}]**\n")
                                elif not self.args or not self.args.only_sensitive:
                                    # Solo escribir datos no sensibles si no estamos en modo "solo sensibles"
                                    file_handle.write(f"- {key}: {val}\n")
                        else:
                            if not self.args or not self.args.only_sensitive:
                                file_handle.write(f"- Formato no reconocido: {d}\n")
            
            elif os.path.isdir(item_path):
                # Procesar subdirectorio
                subdir_files_found, subdir_sensitive_found = self._process_directory(item_path, file_handle, lower_extensions, upper_extensions)
                if subdir_files_found and (subdir_sensitive_found or not self.args or not self.args.only_sensitive):
                    file_handle.write(f"\n### Subdirectory: {item_path}\n")
                files_found = files_found or subdir_files_found
                sensible_data_found = sensible_data_found or subdir_sensitive_found
                
        return files_found, sensible_data_found
        
    def _generate_pdf_report(self, md_file, pdf_file):
        """
        Genera un informe PDF a partir de un archivo MD.
        
        Args:
            md_file: Ruta al archivo Markdown
            pdf_file: Ruta donde se guardará el archivo PDF
            
        Returns:
            bool: True si el PDF se generó correctamente, False en caso contrario
        """
        try:
            # Convertir el archivo MD a pdf con márgenes de 2cm
            subprocess.run([
                'pandoc', 
                '-s', 
                md_file, 
                '-o', 
                pdf_file,
                '-V', 'geometry:margin=2cm',  # Márgenes de 2cm en todos los lados
                '--pdf-engine=xelatex'  # Usar xelatex para mejor soporte de múltiples idiomas
            ], check=True)
            
            return True
        except Exception as e:
            print(f"Error al generar el informe PDF: {str(e)}")
            return False 