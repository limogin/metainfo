class SensitivePatterns:
    """
    Clase que define los patrones considerados sensibles para detectar en metadatos.
    """

    NEGATIVE_PATTERNS = [
        "sourcefile",
        "filename",    
        "exiftoolversion",
        "exiftool:exiftoolversion",        
        "file:filename",
    ]
    
    # Patrones sensibles en español
    SPANISH = [
        "nombre",
        "apellido",
        "nombre_completo",
        "nombre_del_equipo",
        "nombre_del_dispositivo",
        "email",
        "correo",
        "correo_electronico", 
        "telefono",
        "celular",
        "movil",
        "direccion",
        "domicilio",
        "ubicacion",
        "gps",
        "coordenadas",
        "latitud",
        "longitud",
        "dni",
        "rut",
        "pasaporte",
        "identificacion",
        "usuario",
        "password",
        "contraseña",
        "clave",
        "cuenta",
        "tarjeta",
        "credito",
        "debito",
        "banco",
        "empresa",
        "organizacion",
        "institucion",
        "departamento",
        "area",
        "cargo",
        "puesto",
        "rol",
        "ip",
        "mac",
        "serial",
        "licencia",
        "version",
        "sistema",
        "software"
    ]
    
    # Patrones sensibles en inglés
    ENGLISH = [
        "name",
        "first_name",
        "last_name",
        "full_name",
        "device_name",
        "computer_name",
        "hostname",
        "email_address",
        "phone",
        "phone_number",
        "cell",
        "mobile",
        "address",
        "location",
        "coordinates",
        "latitude",
        "longitude",
        "passport",
        "id",
        "ssn", # Número de seguridad social en EEUU
        "social_security",
        "username",
        "user",
        "pass",
        "password",
        "key",
        "account",
        "card",
        "credit_card",
        "debit_card",
        "bank",
        "company",
        "organization",
        "institution",
        "department",
        "position",
        "title",
        "role",
        "license",
        "version",
        "system",
        "os",
        "operating_system"
    ]
    
    # Patrones sensibles en francés
    FRENCH = [
        "nom",
        "prénom",
        "nom_complet",
        "adresse",
        "téléphone",
        "mot_de_passe"
    ]
    
    # Patrones sensibles en alemán
    GERMAN = [
        "name",
        "vorname",
        "nachname",
        "vollständiger_name",
        "adresse",
        "telefon",
        "passwort"
    ]
    
    # Patrones sensibles en italiano
    ITALIAN = [
        "nome",
        "cognome",
        "nome_completo",
        "indirizzo",
        "telefono",
        "password"
    ]
    
    # Patrones sensibles en portugués
    PORTUGUESE = [
        "nome",
        "sobrenome",
        "nome_completo",
        "endereço",
        "telefone",
        "senha"
    ]
    
    # Metadatos específicos de cámaras y dispositivos
    DEVICE_METADATA = [
        "make",
        "model",
        "creator",
        "author",
        "artist",
        "owner",
        "copyright",
        "camera_serial_number",
        "serial_number",
        "device_id",
        "unique_id",
        "original_filename",
        "creator_tool",
        "software_agent",
        "created_by",
        "modified_by",
        "owner_name",
        "by_line",
        "camera_owner",
        "camera_serial",
        "body_serial_number",
        "lens_serial_number",
        "device_serial_number",
        "exif_version"
    ]
    
    @classmethod
    def get_negative_patterns(cls):
        """
        Obtiene los patrones negativos.
        """
        return cls.NEGATIVE_PATTERNS
    
    @classmethod
    def get_all_patterns(cls):
        """
        Obtiene todos los patrones sensibles en una única lista.
        
        Returns:
            list: Lista con todos los patrones sensibles
        """
        return (cls.SPANISH + cls.ENGLISH + cls.FRENCH + 
                cls.GERMAN + cls.ITALIAN + cls.PORTUGUESE + 
                cls.DEVICE_METADATA)
    
    @classmethod
    def get_patterns_by_language(cls, language):
        """
        Obtiene los patrones sensibles para un idioma específico.
        
        Args:
            language: Código de idioma ('spanish', 'english', 'french', etc.)
            
        Returns:
            list: Lista con los patrones del idioma especificado
        """
        if language.lower() == 'spanish':
            return cls.SPANISH
        elif language.lower() == 'english':
            return cls.ENGLISH
        elif language.lower() == 'french':
            return cls.FRENCH
        elif language.lower() == 'german':
            return cls.GERMAN
        elif language.lower() == 'italian':
            return cls.ITALIAN
        elif language.lower() == 'portuguese':
            return cls.PORTUGUESE
        elif language.lower() == 'device':
            return cls.DEVICE_METADATA
        else:
            return []
            
    @classmethod
    def print_patterns_by_language(cls):
        """
        Imprime los patrones agrupados por idioma.
        
        Returns:
            str: String con los patrones agrupados por idioma
        """
        result = "PATRONES SENSIBLES POR IDIOMA:\n\n"
        
        result += "ESPAÑOL:\n"
        result += ", ".join(cls.SPANISH)
        result += "\n\n"
        
        result += "INGLÉS:\n"
        result += ", ".join(cls.ENGLISH)
        result += "\n\n"
        
        result += "FRANCÉS:\n"
        result += ", ".join(cls.FRENCH)
        result += "\n\n"
        
        result += "ALEMÁN:\n"
        result += ", ".join(cls.GERMAN)
        result += "\n\n"
        
        result += "ITALIANO:\n"
        result += ", ".join(cls.ITALIAN)
        result += "\n\n"
        
        result += "PORTUGUÉS:\n"
        result += ", ".join(cls.PORTUGUESE)
        result += "\n\n"
        
        result += "METADATOS DE DISPOSITIVOS:\n"
        result += ", ".join(cls.DEVICE_METADATA)
        
        return result 