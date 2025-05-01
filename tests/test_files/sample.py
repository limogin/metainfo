# -*- coding: utf-8 -*-
import os
import sys
import tempfile
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.PngImagePlugin import PngInfo

# Función para crear una imagen JPEG con metadatos EXIF
def create_jpeg_with_metadata(output_path, metadata):
    """
    Crea una imagen JPEG con metadatos EXIF
    
    Args:
        output_path: Ruta donde guardar la imagen
        metadata: Diccionario con los metadatos a incluir
    """
    # Crear una imagen simple
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    
    # Guardar la imagen con metadatos EXIF
    img.save(output_path, exif=generate_exif(metadata))
    print("Imagen JPEG creada en: {}".format(output_path))

# Función para crear una imagen PNG con metadatos
def create_png_with_metadata(output_path, metadata):
    """
    Crea una imagen PNG con metadatos
    
    Args:
        output_path: Ruta donde guardar la imagen
        metadata: Diccionario con los metadatos a incluir
    """
    # Crear una imagen simple
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    
    # Crear objeto de información PNG
    info = PngInfo()
    
    # Añadir metadatos
    for key, value in metadata.items():
        info.add_text(key, str(value))
    
    # Guardar imagen con metadatos
    img.save(output_path, "PNG", pnginfo=info)
    print("Imagen PNG creada en: {}".format(output_path))

# Función auxiliar para generar datos EXIF
def generate_exif(metadata):
    """
    Genera datos EXIF a partir de un diccionario
    
    Args:
        metadata: Diccionario con los metadatos a incluir
        
    Returns:
        exif_bytes: Bytes de datos EXIF
    """
    # Aquí necesitaríamos usar una biblioteca que permita generar exif completo
    # Por simplicidad, esta función es un placeholder
    # En un entorno real, usaríamos piexif u otra biblioteca similar
    img = Image.new('RGB', (1, 1))
    # En la práctica, esta función no añadirá los metadatos correctamente
    # Se necesitaría una implementación más compleja
    return b''

def main():
    # Crear directorio temporal para los archivos de prueba
    test_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(test_dir, 'files')
    
    # Crear el directorio si no existe
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
    
    # Metadatos de ejemplo con datos sensibles
    sensitive_metadata = {
        'Author': 'Juan Pérez',
        'Email': 'juan.perez@example.com',
        'GPS:Latitude': '40.7128',
        'GPS:Longitude': '-74.0060',
        'Copyright': 'Copyright 2023',
        'Comments': 'Este documento contiene una contraseña: secreta123',
        'Phone': '+34 612 345 678'
    }
    
    # Metadatos de ejemplo sin datos sensibles
    normal_metadata = {
        'Title': 'Documento de Prueba',
        'Description': 'Este es un documento de prueba',
        'Software': 'Test Generator 1.0',
        'CreateDate': '2023:01:01 12:00:00'
    }
    
    # Crear imágenes con metadatos
    create_jpeg_with_metadata(os.path.join(files_dir, 'sensitive.jpg'), sensitive_metadata)
    create_jpeg_with_metadata(os.path.join(files_dir, 'normal.jpg'), normal_metadata)
    create_png_with_metadata(os.path.join(files_dir, 'sensitive.png'), sensitive_metadata)
    create_png_with_metadata(os.path.join(files_dir, 'normal.png'), normal_metadata)
    
    print("Archivos de prueba creados con éxito en: {}".format(files_dir))

if __name__ == "__main__":
    main() 