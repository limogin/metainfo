"""
Clase para centralizar la validación de parámetros de entrada.
Facilita el manejo consistente de argumentos y valores por defecto.
"""

class ParameterValidator:
    """
    Proporciona métodos para validar parámetros y obtener valores seguros
    """
    
    @staticmethod
    def safe_get(obj, attr_name, default_value=None):
        """
        Obtiene de forma segura el valor de un atributo, devolviendo un valor por defecto si no existe.
        
        Args:
            obj: Objeto del que obtener el atributo
            attr_name: Nombre del atributo a obtener
            default_value: Valor por defecto a devolver si el atributo no existe
            
        Returns:
            El valor del atributo o el valor por defecto
        """
        if obj is None:
            return default_value
            
        if hasattr(obj, attr_name):
            attr_value = getattr(obj, attr_name)
            if attr_value is not None:
                return attr_value
                
        return default_value
    
    @staticmethod
    def ensure_attr(obj, attr_name, default_value):
        """
        Asegura que un objeto tenga un atributo, asignándole un valor por defecto si no existe.
        
        Args:
            obj: Objeto en el que asegurar el atributo
            attr_name: Nombre del atributo a asegurar
            default_value: Valor por defecto a asignar si el atributo no existe
            
        Returns:
            El valor final del atributo (existente o recién asignado)
        """
        if obj is None:
            return None
            
        if not hasattr(obj, attr_name) or getattr(obj, attr_name) is None:
            setattr(obj, attr_name, default_value)
            
        return getattr(obj, attr_name)
    
    @staticmethod
    def validate_path(path, create_if_missing=False):
        """
        Valida que una ruta exista, opcionalmente creándola si no existe.
        
        Args:
            path: Ruta a validar
            create_if_missing: Si es True, se crea la ruta si no existe
            
        Returns:
            bool: True si la ruta existe o se creó correctamente, False en caso contrario
        """
        import os
        
        if path is None:
            return False
            
        if os.path.exists(path):
            return True
            
        if create_if_missing:
            try:
                os.makedirs(path)
                return True
            except Exception:
                return False
                
        return False
    
    @staticmethod
    def check_dependency(dependency_name, import_name=None):
        """
        Verifica si una dependencia está instalada.
        
        Args:
            dependency_name: Nombre de la dependencia a verificar
            import_name: Nombre de importación si es diferente al nombre de la dependencia
            
        Returns:
            bool: True si la dependencia está disponible, False en caso contrario
        """
        import importlib
        
        try:
            if import_name is None:
                import_name = dependency_name
                
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def create_default_args():
        """
        Crea un objeto con valores por defecto para los argumentos.
        
        Returns:
            object: Objeto con atributos predeterminados
        """
        class DefaultArgs:
            def __init__(self):
                self.pdf = False
                self.html = True
                self.only_sensitive = False
                self.verbose = False
                self.md = True
                self.wipe_all = False
                self.wipe_sensitive = False
                self.report_all = True
                self.report_sensitive = False
                
        return DefaultArgs() 