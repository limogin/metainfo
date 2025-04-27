class SupportedExtensions:
    """
    Clase que define todas las extensiones de archivo soportadas por la aplicación.
    """
    
    # Imágenes
    IMAGES = [
        "jpg",
        "jpeg",
        "png",
        "webp",
        "gif",
        "bmp",
        "tiff",
        "tif",
        "raw"
    ]
    
    # Documentos
    DOCUMENTS = [
        "pdf",
        "docx",
        "doc",
        "odt",
        "rtf",
        "txt",
        "md",
        "ppt",
        "pptx",
        "odp",
        "xls",
        "xlsx",
        "ods",
        "csv"
    ]
    
    # Archivos multimedia
    MEDIA = [
        "mp3",
        "mp4",
        "avi",
        "mov",
        "wmv",
        "flv",
        "mkv",
        "wav",
        "ogg",
        "m4a",
        "aac"
    ]
    
    @classmethod
    def get_all_extensions(cls):
        """
        Obtiene todas las extensiones soportadas en una única lista.
        
        Returns:
            list: Lista con todas las extensiones soportadas
        """
        return cls.IMAGES + cls.DOCUMENTS + cls.MEDIA
    
    @classmethod
    def get_extensions_by_type(cls, type_name):
        """
        Obtiene las extensiones soportadas por tipo.
        
        Args:
            type_name: Nombre del tipo ('images', 'documents', 'media')
            
        Returns:
            list: Lista con las extensiones del tipo especificado
        """
        if type_name.lower() == 'images':
            return cls.IMAGES
        elif type_name.lower() == 'documents':
            return cls.DOCUMENTS
        elif type_name.lower() == 'media':
            return cls.MEDIA
        else:
            return []
            
    @classmethod
    def print_extensions_by_type(cls):
        """
        Imprime las extensiones agrupadas por tipo.
        
        Returns:
            str: String con las extensiones agrupadas por tipo
        """
        result = "EXTENSIONES SOPORTADAS:\n\n"
        
        result += "IMÁGENES:\n"
        result += ", ".join(cls.IMAGES)
        result += "\n\n"
        
        result += "DOCUMENTOS:\n"
        result += ", ".join(cls.DOCUMENTS)
        result += "\n\n"
        
        result += "MULTIMEDIA:\n"
        result += ", ".join(cls.MEDIA)
        
        return result 