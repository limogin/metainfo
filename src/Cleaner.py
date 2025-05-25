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
        
    def _get_real_file_type(self, file_path):
        """
        Detecta el tipo real del archivo, incluso si tiene extensiones combinadas.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            str: Tipo de archivo ('pdf', 'xlsx', 'docx' o None)
        """
        try:
            # Obtener la extensión base (la primera extensión)
            base_ext = os.path.splitext(file_path)[1].lower()
            
            # Si es un archivo .txt, verificar si es realmente otro tipo
            if base_ext == '.txt':
                # Leer los primeros bytes del archivo para detectar el tipo real
                with open(file_path, 'rb') as f:
                    header = f.read(8)  # Leer los primeros 8 bytes
                    
                    # Detectar PDF por su firma mágica
                    if header.startswith(b'%PDF-'):
                        return 'pdf'
                    
                    # Detectar XLSX por su firma mágica (PK\x03\x04)
                    if header.startswith(b'PK\x03\x04'):
                        return 'xlsx'
                    
                    # Detectar DOCX por su firma mágica (PK\x03\x04)
                    if header.startswith(b'PK\x03\x04'):
                        return 'docx'
            
            # Si no es .txt, verificar la extensión directamente
            if base_ext in ['.pdf', '.xlsx', '.docx']:
                return base_ext[1:]  # Quitar el punto de la extensión
                
            return None
            
        except Exception as e:
            Messages.print_error(f"Error al detectar tipo de archivo {file_path}: {str(e)}")
            return None

    def _verify_pdf_integrity(self, file_path):
        """
        Verifica la integridad de un archivo PDF antes de procesarlo.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            bool: True si el archivo es válido, False si está corrupto
        """
        try:
            Messages.print_debug(f"DEBUG-Cleaner - Verificando integridad de {file_path}", verbose=self.verbose)
            
            # Verificar que el archivo existe y tiene tamaño
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                Messages.print_error(f"El archivo {file_path} no existe o está vacío")
                return False
                
            # Verificar firma PDF
            with open(file_path, 'rb') as f:
                if not f.read(8).startswith(b'%PDF-'):
                    Messages.print_error(f"El archivo {file_path} no es un PDF válido")
                    return False
                    
            # Intentar reparar con qpdf
            try:
                qpdf_path = subprocess.run(["which", "qpdf"], capture_output=True, text=True).stdout.strip()
                if not qpdf_path:
                    Messages.print_warning("qpdf no está instalado")
                    return False
                    
                temp_file = f"{file_path}.qpdf_temp"
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
                # Comando de reparación
                repair_command = [qpdf_path, "--decrypt", "--linearize", "--object-streams=generate", file_path, temp_file]
                Messages.print_debug(f"DEBUG-Cleaner - Ejecutando qpdf: {' '.join(repair_command)}", verbose=self.verbose)
                
                result = subprocess.run(repair_command, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    os.replace(temp_file, file_path)
                    Messages.print_info(f"PDF reparado exitosamente: {file_path}")
                    return True
                else:
                    Messages.print_warning(f"No se pudo reparar el PDF: {result.stderr}")
                    return False
                    
            except Exception as e:
                Messages.print_warning(f"Error al usar qpdf: {str(e)}")
                return False
                
        except Exception as e:
            Messages.print_error(f"Error al verificar PDF {file_path}: {str(e)}")
            return False
        finally:
            # Limpiar archivo temporal si existe
            temp_file = f"{file_path}.qpdf_temp"
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def _clean_all_metadata(self, file_path):
        """
        Limpia todos los metadatos de un archivo, manteniendo el resto.
        
        Args:
            file_path: Ruta al archivo a procesar
        """
        Messages.print_debug(f"DEBUG-Cleaner - Iniciando limpieza completa de {file_path}", verbose=self.verbose)
        
        try:
            # Verificar si es un PDF y su integridad inicial
            real_type = self._get_real_file_type(file_path)
            if real_type == 'pdf':
                if not self._verify_pdf_integrity(file_path):
                    Messages.print_error(f"No se puede procesar el PDF corrupto: {file_path}")
                    return
            
            # 1. Primero usar mat2 para PDFs y XLSX
            if real_type in ['pdf', 'xlsx', 'docx']:
                Messages.print_info(f"Realizando limpieza inicial con mat2 para {real_type.upper()} {file_path}...")
                
                # Comando mat2 para limpiar metadatos
                mat_command = ["mat2", "--inplace", file_path]
                Messages.print_debug(f"DEBUG-Cleaner - Ejecutando comando mat2: {' '.join(mat_command)}", verbose=self.verbose)
                
                result_mat = subprocess.run(mat_command, capture_output=True, text=True)
                if result_mat.returncode != 0:
                    Messages.print_error(f"Error al ejecutar mat2: {result_mat.stderr}")
                else:
                    Messages.print_info(f"Limpieza con mat2 completada para {file_path}")
                    
                    # Si es PDF, verificar integridad después de mat2
                    if real_type == 'pdf':
                        if not self._verify_pdf_integrity(file_path):
                            Messages.print_warning(f"El PDF quedó corrupto después de mat2, intentando reparar...")
                            if not self._verify_pdf_integrity(file_path):
                                Messages.print_error(f"No se pudo reparar el PDF después de mat2: {file_path}")
                                return
            
            # 2. Limpieza general con exiftool
            Messages.print_info(f"Realizando limpieza general con exiftool para {file_path}...")
            
            # Comando para limpiar todo y sobrescribir el original
            exiftool_command = ["exiftool", "-all=", "-overwrite_original", file_path]
            Messages.print_debug(f"DEBUG-Cleaner - Ejecutando comando de limpieza general: {' '.join(exiftool_command)}", verbose=self.verbose)
            
            result = subprocess.run(exiftool_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                if "Invalid xref table" in result.stderr and real_type == 'pdf':
                    Messages.print_warning(f"El PDF tiene una tabla de referencias inválida después de la limpieza. Intentando reparar...")
                    if self._verify_pdf_integrity(file_path):
                        # Intentar la limpieza nuevamente después de la reparación
                        result = subprocess.run(exiftool_command, capture_output=True, text=True)
                        if result.returncode != 0:
                            Messages.print_error(f"Error al ejecutar limpieza general con exiftool después de reparación: {result.stderr}")
                            return
                    else:
                        Messages.print_error(f"No se pudo reparar el PDF después de la limpieza: {file_path}")
                        return
                else:
                    Messages.print_error(f"Error al ejecutar limpieza general con exiftool: {result.stderr}")
                    return
            
            # 3. Limpieza específica de claves sensibles
            Messages.print_info(f"Realizando limpieza específica de claves sensibles para {file_path}...")
            
            keys_to_delete = SensitivePatterns.get_keys_to_delete()
            if keys_to_delete:
                specific_command = ["exiftool"]
                for key in keys_to_delete:
                    specific_command.append(f"-{key}=")
                specific_command.extend(["-overwrite_original", file_path])
                
                Messages.print_debug(f"DEBUG-Cleaner - Ejecutando comando de limpieza específica: {' '.join(specific_command)}", verbose=self.verbose)
                
                result_specific = subprocess.run(specific_command, capture_output=True, text=True)
                if result_specific.returncode != 0:
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
                    Messages.print_warning(f"Después de la limpieza, aún quedan {non_system_count} campos de metadatos en {file_path}")
                    if self.verbose:
                        Messages.print_debug("Campos restantes:", verbose=True)
                        for key, val in remaining_metadata[0].items():
                            if key not in ['SourceFile', 'ExifTool:ExifToolVersion', 'File:FileName', 'File:Directory', 
                                         'File:FileSize', 'File:FileModifyDate', 'File:FileAccessDate',
                                         'File:FileInodeChangeDate', 'File:FilePermissions', 'File:FileType', 
                                         'File:FileTypeExtension', 'File:MIMEType']:
                                Messages.print_debug(f"  {key}: {val}", verbose=True)
                else:
                    Messages.print_info(f"Limpieza finalizada con éxito para {file_path}")
        
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