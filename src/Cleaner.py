import os

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
        
        try:
            # Mensaje sobre el modo de limpieza
            if self.args and self.args.only_sensitive:
                print("Modo de limpieza: SOLO DATOS SENSIBLES")
            else:
                print("Modo de limpieza: TODOS LOS METADATOS")
                
            files_found = self._process_directory(src_path, lower_extensions, upper_extensions)
            
            if not files_found:
                print("No se encontraron archivos con las extensiones soportadas.")
            else:
                print("Proceso de limpieza de metadatos completado.")
                
            return True
        except Exception as e:
            print(f"Error al eliminar metadatos: {str(e)}")
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
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path) and (item.lower().endswith(lower_extensions) or item.upper().endswith(upper_extensions)):
                print(f"Limpiando metadatos de {item_path} ...")
                files_found = True
                if self.main.EXIFTOOL_AVAILABLE:
                    try:
                        if self.args and self.args.only_sensitive:
                            # Limpiar solo metadatos sensibles
                            self._clean_sensitive_metadata(item_path)
                        else:
                            # Limpiar todos los metadatos
                            with self.main.exiftool.ExifToolHelper() as et:
                                et.execute("-all=", "-overwrite_original", item_path)
                    except Exception as e:
                        print(f"Error al limpiar {item_path}: {str(e)}")
            
            elif os.path.isdir(item_path):
                # Procesar subdirectorio
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
            print(f"No se puede limpiar {file_path}: exiftool no está disponible")
            return
            
        try:
            # Obtener todos los metadatos del archivo
            metadata = self.main.inspect(file_path)
            
            with self.main.exiftool.ExifToolHelper() as et:
                # Para cada elemento en los metadatos
                for d in metadata:
                    if hasattr(d, 'items') and callable(d.items):
                        for key, val in d.items():
                            # Verificar si contiene datos sensibles
                            is_sensitive, matching_patterns = self.main._check_sensitive_data(key, val)
                            
                            # Si es sensible, eliminarlo
                            if is_sensitive:
                                print(f"  - Eliminando campo sensible: {key} ({', '.join(matching_patterns)})")
                                # Construir el comando para eliminar esta etiqueta específica
                                # El formato es -TAG= para eliminar una etiqueta específica
                                et.execute(f"-{key}=", "-overwrite_original", file_path)
            
            print(f"Limpieza selectiva de {file_path} completada")
            
        except Exception as e:
            print(f"Error al limpiar selectivamente {file_path}: {str(e)}") 