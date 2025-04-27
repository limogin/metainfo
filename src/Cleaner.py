import os
from src.Messages import Messages
from src.ParameterValidator import ParameterValidator

class Cleaner:
    """
    Clase responsable de limpiar metadatos de archivos.
    """
    
    def __init__(self, main_instance):
        """
        Inicializa el Cleaner con una referencia a la instancia principal.
        
        Args:
            main_instance: Instancia de la clase Main
        """
        self.main = main_instance
        self.args = main_instance.args if hasattr(main_instance, 'args') else None
        # Verificar si el atributo EXIFTOOL_AVAILABLE está en main_instance
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        Messages.print_debug("DEBUG-Cleaner-init - Verificando disponibilidad de exiftool", verbose=verbose)
        
    def clean_metadata(self, src_path):
        """
        Limpia los metadatos de los archivos en el directorio especificado.
        
        Args:
            src_path: Ruta al directorio a procesar
            
        Returns:
            bool: True si se completó la limpieza correctamente, False en caso contrario
        """
        lower_extensions = tuple(self.main.extensions)
        upper_extensions = tuple(ext.upper() for ext in self.main.extensions)
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        
        # Verificar la disponibilidad de exiftool antes de proceder
        if not hasattr(self.main, 'EXIFTOOL_AVAILABLE') or not self.main.EXIFTOOL_AVAILABLE:
            Messages.print_error("Error: No se puede limpiar metadatos, exiftool no está disponible")
            Messages.print_info("Instale exiftool y el paquete PyExifTool: pip install PyExifTool")
            return False
        
        try:
            # Mensaje sobre el modo de limpieza
            if self.args and self.args.only_sensitive:
                Messages.print_info("Modo de limpieza: SOLO DATOS SENSIBLES")
            else:
                Messages.print_info("Modo de limpieza: TODOS LOS METADATOS")
            
            Messages.print_debug("DEBUG-Cleaner - Iniciando procesamiento de directorio", verbose=verbose)
            files_found = self._process_directory(src_path, lower_extensions, upper_extensions)
            
            if not files_found:
                Messages.print_info("No se encontraron archivos con las extensiones soportadas.")
            else:
                Messages.print_info("Proceso de limpieza de metadatos completado.")
                
            return True
        except Exception as e:
            Messages.print_error(f"Error al eliminar metadatos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def _process_directory(self, directory, lower_extensions, upper_extensions):
        """
        Procesa recursivamente un directorio y todos sus subdirectorios para limpiar metadatos.
        
        Args:
            directory: Ruta al directorio a procesar
            lower_extensions: Tupla de extensiones en minúsculas
            upper_extensions: Tupla de extensiones en mayúsculas
            
        Returns:
            bool: True si se encontraron archivos, False en caso contrario
        """
        files_found = False
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path) and (item.lower().endswith(lower_extensions) or item.upper().endswith(upper_extensions)):
                Messages.print_info(f"Limpiando metadatos de {item_path} ...")
                files_found = True
                if self.main.EXIFTOOL_AVAILABLE:
                    try:
                        # Importación local para asegurar que exiftool está disponible
                        import exiftool
                        
                        if self.args and getattr(self.args, 'only_sensitive', False):
                            # Limpiar solo metadatos sensibles
                            Messages.print_debug(f"DEBUG-Cleaner - Limpieza selectiva de {item_path}", verbose=verbose)
                            self._clean_sensitive_metadata(item_path)
                        else:
                            # Limpiar todos los metadatos
                            Messages.print_debug(f"DEBUG-Cleaner - Limpieza completa de {item_path}", verbose=verbose)
                            with exiftool.ExifToolHelper() as et:
                                et.execute("-all=", "-overwrite_original", item_path)
                                Messages.print_debug(f"DEBUG-Cleaner - Metadatos eliminados de {item_path}", verbose=verbose)
                    except Exception as e:
                        Messages.print_error(f"Error al limpiar {item_path}: {str(e)}")
                else:
                    Messages.print_error(f"No se puede limpiar {item_path}: exiftool no está disponible")
            
            elif os.path.isdir(item_path):
                # Procesar subdirectorio
                Messages.print_debug(f"DEBUG-Cleaner - Procesando subdirectorio {item_path}", verbose=verbose)
                subdir_files_found = self._process_directory(item_path, lower_extensions, upper_extensions)
                files_found = files_found or subdir_files_found
                
        return files_found
        
    def _clean_sensitive_metadata(self, file_path):
        """
        Limpia solo los metadatos sensibles de un archivo, manteniendo el resto.
        
        Args:
            file_path: Ruta al archivo a procesar
        """
        if not self.main.EXIFTOOL_AVAILABLE:
            Messages.print_error(f"No se puede limpiar {file_path}: exiftool no está disponible")
            return
        
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
            
        try:
            # Importación local para asegurar que exiftool está disponible
            import exiftool
            
            # Obtener todos los metadatos del archivo
            metadata = self.main.inspect(file_path)
            sensitive_found = False
            
            with exiftool.ExifToolHelper() as et:
                # Para cada elemento en los metadatos
                if isinstance(metadata, list) and len(metadata) > 0:
                    # Si metadata es una lista (formato típico de ExifTool)
                    for d in metadata:
                        if hasattr(d, 'items') and callable(d.items):
                            for key, val in d.items():
                                # Verificar si contiene datos sensibles
                                is_sensitive, matching_patterns = self.main._check_sensitive_data(key, val)
                                
                                # Si es sensible, eliminarlo
                                if is_sensitive:
                                    sensitive_found = True
                                    Messages.print_info(f"  - Eliminando campo sensible: {key} ({', '.join(matching_patterns)})")
                                    # Construir el comando para eliminar esta etiqueta específica
                                    # El formato es -TAG= para eliminar una etiqueta específica
                                    et.execute(f"-{key}=", "-overwrite_original", file_path)
                                    Messages.print_debug(f"DEBUG-Cleaner - Campo sensible '{key}' eliminado", verbose=verbose)
                elif isinstance(metadata, dict):
                    # Si metadata es un diccionario
                    for key, val in metadata.items():
                        # Ignorar el campo 'SourceFile' que es añadido por ExifTool
                        if key != 'SourceFile':
                            # Verificar si contiene datos sensibles
                            is_sensitive, matching_patterns = self.main._check_sensitive_data(key, val)
                            
                            # Si es sensible, eliminarlo
                            if is_sensitive:
                                sensitive_found = True
                                Messages.print_info(f"  - Eliminando campo sensible: {key} ({', '.join(matching_patterns)})")
                                # Construir el comando para eliminar esta etiqueta específica
                                et.execute(f"-{key}=", "-overwrite_original", file_path)
                                Messages.print_debug(f"DEBUG-Cleaner - Campo sensible '{key}' eliminado", verbose=verbose)
            
            if sensitive_found:
                Messages.print_info(f"Limpieza selectiva de {file_path} completada")
            else:
                Messages.print_info(f"No se encontraron datos sensibles en {file_path}")
            
        except Exception as e:
            Messages.print_error(f"Error al limpiar selectivamente {file_path}: {str(e)}")
            # No propagar la excepción para continuar con otros archivos 