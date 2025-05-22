import os
from src.Messages import Messages
from src.ParameterValidator import ParameterValidator
import exiftool
import subprocess
import shutil
import traceback
from src.SensitivePatterns import SensitivePatterns

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
        self.verbose = self.args.get('verbose', False)
        self.sensitive = self.args.get('wipe_sensitive', False)
        # Verificar si el atributo EXIFTOOL_AVAILABLE está en main_instance
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        
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
        verbose = self.args.get('verbose', False)
                
        try:
            # Mensaje sobre el modo de limpieza
            if self.sensitive:
                Messages.print_info("Modo de limpieza: SOLO DATOS SENSIBLES")
            else:
                Messages.print_info("Modo de limpieza: TODOS LOS METADATOS")
            
            files_found = self._process_directory(src_path, lower_extensions, upper_extensions)
            
            if not files_found:
                Messages.print_info("No se encontraron archivos con las extensiones soportadas.")
            else:
                Messages.print_info("Proceso de limpieza de metadatos completado.")
                
            return True
        except Exception as e:
            Messages.print_error(f"Error al eliminar metadatos: {str(e)}")
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
        verbose = self.args.get('verbose', False)
        
        try:
            # Verificar si el directorio existe
            if not os.path.exists(directory):
                Messages.print_error(f"Error: El directorio {directory} no existe")
                return False
                
            Messages.print_debug(f"DEBUG-Cleaner-process - Procesando directorio: {directory}", verbose=self.verbose)
            
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                # Omitir archivos .txt
                # if item.lower().endswith('.txt'):
                #    Messages.print_debug(f"DEBUG-Cleaner - Omitiendo archivo .txt: {item_path}", verbose=self.verbose)
                #    continue
                
                if os.path.isfile(item_path) and (item.lower().endswith(lower_extensions) or item.upper().endswith(upper_extensions)):
                    try:
                        Messages.print_info(f"Limpiando metadatos de {item_path} ...")
                        files_found = True
                        
                        if self.sensitive is False:                            
                            self._clean_all_metadata(item_path)
                        else:
                            self._clean_sensitive_metadata(item_path)
                        
                    except Exception as e:
                        Messages.print_error(f"Error al procesar archivo {item_path}: {str(e)}")                        
                        continue
                    
                elif os.path.isdir(item_path):
                    # Procesar subdirectorio
                    Messages.print_debug(f"DEBUG-Cleaner - Procesando subdirectorio {item_path}", verbose=verbose)
                    subdir_files_found = self._process_directory(item_path, lower_extensions, upper_extensions)
                    files_found = files_found or subdir_files_found
                    
            return files_found
        except Exception as e:
            Messages.print_error(f"Error al procesar directorio {directory}: {str(e)}")
            traceback.print_exc()
            return files_found
        
    def _clean_all_metadata(self, file_path):
        """
        Limpia todos los metadatos de un archivo, manteniendo el resto.
        
        Args:
            file_path: Ruta al archivo a procesar
        """
        Messages.print_debug(f"DEBUG-Cleaner - Iniciando limpieza completa de {file_path}", verbose=self.verbose)
        
        try:
            # Primero, intentar usando el método directo de la línea de comandos
            
            # Crear un archivo temporal para guardar la salida
            temp_dir = os.path.dirname(file_path)
            temp_file = os.path.join(temp_dir, f"temp_{os.path.basename(file_path)}")
            
            # Borrar el archivo temporal si ya existe
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    Messages.print_error(f"No se pudo eliminar el archivo temporal existente: {str(e)}")
            
            # Comando base para ejecutar exiftool directamente - limpieza general
            exiftool_command = ["exiftool", "-all=", "-o", temp_file, file_path]
            Messages.print_debug(f"DEBUG-Cleaner - Ejecutando comando de limpieza general: {' '.join(exiftool_command)}", verbose=self.verbose)
            
            # Ejecutar el comando de limpieza general
            result = subprocess.run(exiftool_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                # El comando fue exitoso, reemplazar el archivo original con el temporal
                Messages.print_debug(f"DEBUG-Cleaner - Comando exitoso, reemplazando archivo original", verbose=self.verbose)
                try:
                    # Respaldar permisos originales
                    original_perms = os.stat(file_path).st_mode
                    
                    # Eliminar el archivo original
                    os.remove(file_path)
                    
                    # Mover el archivo temporal al lugar del original
                    shutil.move(temp_file, file_path)
                    
                    # Restablecer permisos
                    os.chmod(file_path, original_perms)
                    
                    Messages.print_info(f"Limpieza general completada para {file_path}")
                except Exception as e:
                    Messages.print_error(f"Error al reemplazar el archivo original: {str(e)}")
            else:
                Messages.print_error(f"Error al ejecutar exiftool: {result.stderr}")
                
            # Ahora realizar limpieza específica de claves sensibles
            Messages.print_info(f"Realizando limpieza específica de claves sensibles para {file_path}...")
            
            # Obtener las claves específicas a borrar usando la clase SensitivePatterns directamente
            keys_to_delete = SensitivePatterns.get_keys_to_delete()
            
            if keys_to_delete:
                # Crear nuevo archivo temporal para la limpieza específica
                temp_file_specific = os.path.join(temp_dir, f"temp_specific_{os.path.basename(file_path)}")
                
                # Construir comando para eliminar claves específicas
                specific_command = ["exiftool"]
                for key in keys_to_delete:
                    specific_command.append(f"-{key}=")
                specific_command.extend(["-o", temp_file_specific, file_path])
                
                Messages.print_debug(f"DEBUG-Cleaner - Ejecutando comando de limpieza específica: {' '.join(specific_command)}", verbose=self.verbose)
                
                # Ejecutar limpieza específica
                result_specific = subprocess.run(specific_command, capture_output=True, text=True)
                
                if result_specific.returncode == 0:
                    try:
                        # Respaldar permisos originales
                        original_perms = os.stat(file_path).st_mode
                        
                        # Eliminar el archivo original
                        os.remove(file_path)
                        
                        # Mover el archivo temporal al lugar del original
                        shutil.move(temp_file_specific, file_path)
                        
                        # Restablecer permisos
                        os.chmod(file_path, original_perms)
                        
                        Messages.print_info(f"Limpieza específica de claves sensibles completada para {file_path}")
                    except Exception as e:
                        Messages.print_error(f"Error al reemplazar el archivo original en limpieza específica: {str(e)}")
                else:
                    Messages.print_error(f"Error al ejecutar limpieza específica: {result_specific.stderr}")
            
            # Verificación final
            with exiftool.ExifToolHelper() as et:
                remaining_metadata = et.get_metadata(file_path)
                metadata_count = len(remaining_metadata[0]) if remaining_metadata and len(remaining_metadata) > 0 else 0
                non_system_count = sum(1 for key, val in remaining_metadata[0].items() 
                                  if key not in ['SourceFile', 'ExifTool:ExifToolVersion', 'File:FileName', 'File:Directory', 
                                               'File:FileSize', 'File:FileModifyDate', 'File:FileAccessDate',
                                               'File:FileInodeChangeDate', 'File:FilePermissions', 'File:FileType', 
                                               'File:FileTypeExtension', 'File:MIMEType'])
                
                if non_system_count > 0:
                    Messages.print_warning(f"Después de la limpieza completa y específica, aún quedan {non_system_count} campos de metadatos en {file_path}")
                else:
                    Messages.print_info(f"Limpieza completa y específica finalizada con éxito para {file_path}")
        
        except Exception as e:
            Messages.print_error(f"Error general al limpiar {file_path}: {str(e)}")
            traceback.print_exc()


    def _clean_sensitive_metadata(self, file_path):
        """
        Limpia solo los metadatos sensibles de un archivo, manteniendo el resto.
        
        Args:
            file_path: Ruta al archivo a procesar
        """
        verbose = self.args.get('verbose', False)
        Messages.print_debug(f"DEBUG-Cleaner - Iniciando limpieza selectiva de {file_path}", verbose=self.verbose)
        
        try:
            # Obtener metadatos actuales
            metadata = self.main.inspect(file_path)
            sensitive_found = False
            sensitive_tags = []
            
            # Identificar qué etiquetas son sensibles
            if isinstance(metadata, list) and len(metadata) > 0:
                for d in metadata:
                    if hasattr(d, 'items') and callable(d.items):
                        for key, val in d.items():
                            # Verificar si contiene datos sensibles
                            is_sensitive, matching_patterns = self.main.reporter._check_sensitive_data(key, val)
                            if is_sensitive:
                                sensitive_found = True
                                sensitive_tags.append(key)
                                Messages.print_info(f"  - Etiqueta sensible encontrada: {key} ({', '.join(matching_patterns)})")
            elif isinstance(metadata, dict):
                # Si metadata es un diccionario
                for key, val in metadata.items():
                    # Ignorar el campo 'SourceFile' que es añadido por ExifTool
                    if key != 'SourceFile':
                        # Verificar si contiene datos sensibles
                        is_sensitive, matching_patterns = self.main.reporter._check_sensitive_data(key, val)
                        if is_sensitive:
                            sensitive_found = True
                            sensitive_tags.append(key)
                            Messages.print_info(f"  - Etiqueta sensible encontrada: {key} ({', '.join(matching_patterns)})")
            
            if not sensitive_found:
                Messages.print_info(f"No se encontraron datos sensibles en {file_path}")
                return
            
            # Proceder con la limpieza usando subprocess
            temp_dir = os.path.dirname(file_path)
            temp_file = os.path.join(temp_dir, f"temp_{os.path.basename(file_path)}")
            
            # Borrar el archivo temporal si ya existe
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    Messages.print_error(f"No se pudo eliminar el archivo temporal existente: {str(e)}")
            
            # Construir el comando para eliminar solo las etiquetas sensibles
            exiftool_command = ["exiftool"]
            for tag in sensitive_tags:
                exiftool_command.append(f"-{tag}=")
            exiftool_command.extend(["-o", temp_file, file_path])
            
            Messages.print_debug(f"DEBUG-Cleaner - Ejecutando comando: {' '.join(exiftool_command)}", verbose=self.verbose)
            
            # Ejecutar el comando
            result = subprocess.run(exiftool_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                # El comando fue exitoso, reemplazar el archivo original con el temporal
                Messages.print_debug(f"DEBUG-Cleaner - Comando exitoso, reemplazando archivo original", verbose=self.verbose)
                try:
                    # Respaldar permisos originales
                    original_perms = os.stat(file_path).st_mode
                    
                    # Eliminar el archivo original
                    os.remove(file_path)
                    
                    # Mover el archivo temporal al lugar del original
                    shutil.move(temp_file, file_path)
                    
                    # Restablecer permisos
                    os.chmod(file_path, original_perms)
                    
                    Messages.print_info(f"Metadatos sensibles eliminados correctamente de {file_path}")
                    return
                except Exception as e:
                    Messages.print_error(f"Error al reemplazar el archivo original: {str(e)}")
            else:
                Messages.print_error(f"Error al ejecutar exiftool: {result.stderr}")
            
            # Si llegamos aquí, el método directo falló; intentar con la biblioteca
            Messages.print_info(f"Intentando método alternativo para {file_path}...")
            
            with exiftool.ExifToolHelper() as et:
                for tag in sensitive_tags:
                    try:
                        et.execute(f"-{tag}=", "-overwrite_original", file_path)
                        Messages.print_debug(f"DEBUG-Cleaner - Campo sensible '{tag}' eliminado", verbose=self.verbose)
                    except Exception as e:
                        Messages.print_error(f"Error al eliminar etiqueta {tag}: {str(e)}")
                
                # Verificar si se eliminaron correctamente
                remaining_metadata = et.get_metadata(file_path)
                still_sensitive = False
                
                if isinstance(remaining_metadata, list) and len(remaining_metadata) > 0:
                    for d in remaining_metadata[0]:
                        if d in sensitive_tags:
                            still_sensitive = True
                            Messages.print_warning(f"No se pudo eliminar completamente la etiqueta: {d}")
                
                if not still_sensitive:
                    Messages.print_info(f"Limpieza selectiva de {file_path} completada")
                else:
                    Messages.print_warning(f"Algunas etiquetas sensibles no pudieron eliminarse de {file_path}")
            
        except Exception as e:
            Messages.print_error(f"Error general al limpiar selectivamente {file_path}: {str(e)}")
            traceback.print_exc() 