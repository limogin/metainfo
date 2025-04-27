"""
Clase para centralizar todos los mensajes al usuario.
Facilita el mantenimiento y la consistencia de la interfaz.
"""

class Messages:
    # Mensajes de error generales
    ERROR_NO_INPUT_FOLDER = "Error: No se ha especificado la carpeta de entrada. Use --i ruta_carpeta"
    ERROR_FOLDER_NOT_EXISTS = "Error: La carpeta {0} no existe"
    ERROR_NO_ARGS = "ERROR: No hay argumentos disponibles para procesar"
    ERROR_REPORT_GENERATION = "ERROR: No se pudo generar el informe."
    
    # Mensajes relacionados con dependencias
    ERROR_MISSING_YAML = """ERROR: La biblioteca 'pyyaml' es requerida pero no está instalada.
Por favor, instálela ejecutando: pip install pypandoc"""
    
    ERROR_MISSING_PANDOC = """ERROR: Pandoc no está instalado o no se encuentra en el PATH.
Por favor, instale Pandoc desde https://pandoc.org/installing.html
La generación de PDF ha sido desactivada."""
    
    WARNING_MISSING_PYPANDOC = """ADVERTENCIA: pypandoc no está instalado. No se podrán generar PDFs.
Instale con: pip install pypandoc"""
    
    ERROR_PYPANDOC_NOT_AVAILABLE = """Error: pypandoc no está disponible.
Por favor, instale pypandoc: pip install pypandoc"""
    
    ERROR_MARKDOWN_NOT_EXISTS = "Error: No se puede generar PDF/HTML, el archivo Markdown no existe."
    
    # Mensajes relacionados con la generación de informes
    ERROR_PDF_GENERATION = """ADVERTENCIA: Se generó el informe en Markdown pero falló la conversión a PDF.
Puede encontrar el informe en Markdown en: {0}
Puede visualizar el informe en HTML en: {1}
El formato HTML siempre está disponible como alternativa al PDF."""
    
    ERROR_FONT_NOT_FOUND = """ERROR: No se pudo generar el PDF debido a un problema con las fuentes.
Se ha modificado la configuración para usar fuentes estándar.
Intente ejecutar nuevamente el comando."""
    
    ERROR_PDF_CONVERSION_FAILED = """ERROR: Todos los métodos de conversión a PDF han fallado.
Razones comunes:
1. Problemas con las fuentes instaladas
2. LaTeX no está correctamente configurado
3. Contenido no compatible en el informe
Revise el mensaje de error detallado para más información."""
    
    ERROR_EXIFTOOL = "exiftool no está disponible. La funcionalidad será limitada."
    
    # Mensajes relacionados con LaTeX
    LATEX_RECOMMENDATIONS = """
Recomendaciones para solucionar el problema:
 1. Instale Pandoc desde https://pandoc.org/installing.html
 2. Instale una distribución completa de LaTeX con soporte Unicode:
    - En Ubuntu/Debian: sudo apt install texlive-xetex texlive-fonts-recommended texlive-lang-spanish
    - Para una instalación completa: sudo apt install texlive-full
    - En Fedora/RHEL: sudo dnf install texlive-xetex texlive-collection-fontsrecommended texlive-collection-langspanish
    - En Windows/Mac: Instale TeX Live o MiKTeX desde https://www.latex-project.org/get/
 3. Asegúrese de que ambos estén en su PATH del sistema
 4. Para conversiones simples, puede usar el HTML generado con --html como alternativa"""
    
    # Mensajes informativos
    INFO_REPORT_FORMATS = """
NOTA SOBRE FORMATOS DE SALIDA:
- Siempre se genera un archivo Markdown (.md) como formato base.
- Si se especifica --html, se genera un archivo HTML para visualización en navegadores.
- Si se especifica --pdf, se intentará generar un PDF (requiere Pandoc y XeLaTeX/LaTeX instalados).
  - XeLaTeX es preferido para mejor soporte de caracteres Unicode.
  - Instale los paquetes necesarios con: sudo apt install texlive-xetex texlive-fonts-recommended
- Si la generación de PDF falla, siempre puede usar el formato HTML como alternativa."""
    
    INFO_MD_GENERATED = "Reporte Markdown generado: {0}"
    INFO_HTML_GENERATED = "Reporte HTML generado: {0}"
    INFO_PDF_GENERATED = "Reporte PDF generado: {0}"
    
    INFO_HTML_ALTERNATIVE = "Se ha generado un HTML como alternativa al PDF: {0}"
    INFO_TRYING_ALTERNATIVE = "Intentando método alternativo para generar PDF..."
    INFO_SUCCESSFUL_CONVERSION = "Conversión a PDF exitosa utilizando método alternativo."
    
    # Mensajes de depuración
    DEBUG_PDF_ENABLED = "DEBUG - PDF habilitado: {0}"
    DEBUG_HTML_ENABLED = "DEBUG - HTML habilitado: {0}"
    DEBUG_ARGS_SETUP = "DEBUG: Valores iniciales: PDF={0}, HTML={1}"
    DEBUG_MAIN_INIT = "DEBUG-Main-init - Inicializado args con valores por defecto"
    DEBUG_READING_FILE = "Leyendo {0} ..."
    DEBUG_CONVERSION_STARTED = "Iniciando conversión a PDF con pypandoc..."
    DEBUG_USING_SIMPLIFIED_OPTIONS = "Utilizando opciones simplificadas para evitar problemas con fuentes"
    
    # Mensajes relacionados con PDF
    ERROR_PYPANDOC_MISSING = "Error: pypandoc no está disponible."
    INFO_MARKDOWN_GENERATED = "Reporte Markdown generado: {0}"
    INFO_HTML_GENERATED = "Reporte HTML generado: {0}"
    INFO_PDF_GENERATED = "Reporte PDF generado: {0}" 
    
    @staticmethod
    def print_error(message, *args):
        """
        Imprime un mensaje de error formateado.
        
        Args:
            message: El mensaje a imprimir
            *args: Argumentos para formatear el mensaje
        """
        if args:
            print(message.format(*args))
        else:
            print(message)
    
    @staticmethod
    def print_info(message, *args):
        """
        Imprime un mensaje informativo formateado.
        
        Args:
            message: El mensaje a imprimir
            *args: Argumentos para formatear el mensaje
        """
        if args:
            print(message.format(*args))
        else:
            print(message)
    
    @staticmethod
    def print_debug(message, *args, verbose=False):
        """
        Imprime un mensaje de depuración formateado, solo si verbose es True.
        
        Args:
            message: El mensaje a imprimir
            *args: Argumentos para formatear el mensaje
            verbose: Si es True, se imprime el mensaje
        """
        # Solo imprime mensajes de depuración si verbose es True
        if not verbose:
            return
            
        if args:
            print(message.format(*args))
        else:
            print(message)