#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar que todas las dependencias necesarias para las pruebas
estén instaladas. Este script se puede ejecutar antes de las pruebas.
"""

import sys
import importlib.util
import subprocess

# Verificar que estamos usando Python 3
if sys.version_info[0] < 3:
    print("Error: Este script requiere Python 3.")
    print("Versión actual: Python {}.{}.{}".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    print("Por favor, ejecuta este script con Python 3:")
    print("  python3 tests/check_dependencies.py")
    sys.exit(1)

# Lista de dependencias críticas que se necesitan para las pruebas
DEPENDENCIES = [
    ("PIL", "pillow>=9.0.0", "Para el procesamiento de imágenes"),
    ("yaml", "pyyaml>=6.0", "Para el procesamiento de archivos YAML"),
    ("exiftool", "PyExifTool>=0.5.6", "Para el manejo de metadatos de archivos"),
    ("unittest", None, "Para ejecutar las pruebas (módulo estándar de Python)"),
    ("pytest", "pytest", "Para pruebas con cobertura (opcional)"),
]

def check_dependency(module_name, package_name, description):
    """
    Verifica si una dependencia está instalada.
    
    Args:
        module_name: Nombre del módulo a importar
        package_name: Nombre del paquete a instalar (puede ser None para módulos estándar)
        description: Descripción de la dependencia
        
    Returns:
        bool: True si está instalada, False en caso contrario
    """
    try:
        # Intentar importar el módulo
        if importlib.util.find_spec(module_name) is not None:
            print("✓ {} está instalado: {}".format(module_name, description))
            return True
        else:
            print("✗ {} no está instalado: {}".format(module_name, description))
            return False
    except ImportError:
        print("✗ Error al verificar {}: {}".format(module_name, description))
        return False

def install_dependency(package_name):
    """
    Instala una dependencia.
    
    Args:
        package_name: Nombre del paquete a instalar
        
    Returns:
        bool: True si la instalación fue exitosa, False en caso contrario
    """
    if package_name is None:
        return False
        
    try:
        print("Instalando {}...".format(package_name))
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print("Error al instalar {}".format(package_name))
        return False

def check_dependencies():
    """
    Función que verifica todas las dependencias necesarias.
    
    Returns:
        bool: True si todas las dependencias están instaladas, False en caso contrario
    """
    print("Verificando dependencias para las pruebas...")
    
    # Verificar la versión de Python primero
    python_version = "{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
    if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
        print("✓ Python {} - OK".format(python_version))
    else:
        print("⚠ Python {} - Se recomienda Python 3.6 o superior".format(python_version))
    
    all_installed = True
    
    for module_name, package_name, description in DEPENDENCIES:
        if not check_dependency(module_name, package_name, description):
            all_installed = False
            if package_name is not None:
                print("Intentando instalar {}...".format(package_name))
                if install_dependency(package_name):
                    all_installed = check_dependency(module_name, package_name, description)
    
    if all_installed:
        print("\n✓ Todas las dependencias están instaladas.")
        return True
    else:
        print("\n✗ Algunas dependencias no están instaladas.")
        return False

def main():
    """
    Función principal que verifica todas las dependencias.
    """
    result = check_dependencies()
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main()) 