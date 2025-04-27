import os
import datetime
import markdown
import tempfile
import subprocess
import sys

# Variable global para rastrear si pypandoc está disponible
PYPANDOC_AVAILABLE = False

try:
    import pypandoc
    PYPANDOC_AVAILABLE = True
    print("pypandoc está disponible, versión:", pypandoc.__version__)
except ImportError:
    from src.Messages import Messages
    Messages.print_error(Messages.WARNING_MISSING_PYPANDOC)

from src.Messages import Messages
from src.ParameterValidator import ParameterValidator

class Reporter:
    """
    Clase para generar reportes de metadatos.
    """
    
    def __init__(self, main_instance):
        """
        Inicializa el Reporter con una referencia a la instancia principal.
        
        Args:
            main_instance: Instancia de la clase Main
        """
        self.main = main_instance
        
        # Asignar argumentos, asegurándose de que estén disponibles
        if hasattr(main_instance, 'args') and main_instance.args is not None:
            self.args = main_instance.args
            
            # Asegurar que pdf esté definido, incluso si es False
            pdf_value = ParameterValidator.ensure_attr(self.args, 'pdf', False)
            html_value = ParameterValidator.ensure_attr(self.args, 'html', True)
                
            # Depuración: verificar valores
            verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
            Messages.print_debug(f"DEBUG-Reporter-init - Args desde Main: PDF={pdf_value}, HTML={html_value}", verbose=verbose)
        else:
            Messages.print_debug("DEBUG-Reporter-init - No hay args en Main o args es None, creando valores por defecto")
            # Crear un objeto simulado para args si no está disponible
            self.args = ParameterValidator.create_default_args()
        
    def generate_report(self, src_path, metadata_info):
        """
        Genera un informe de metadatos basado en la información recopilada.
        
        Args:
            src_path: Ruta al directorio procesado
            metadata_info: Diccionario con la información de metadatos recopilada
            
        Returns:
            tuple: (ruta al archivo markdown, ruta al archivo pdf) o (None, None) en caso de error
        """
        try:
            # Obtener el valor de verbose desde args de forma segura
            verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
            
            # Obtener valores de configuración de forma segura
            pdf_enabled = ParameterValidator.safe_get(self.args, 'pdf', False)
            html_enabled = ParameterValidator.safe_get(self.args, 'html', True)
            
            # Mostrar mensajes de depuración solo cuando verbose=True
            Messages.print_debug(Messages.DEBUG_PDF_ENABLED, pdf_enabled, verbose=verbose)
            Messages.print_debug(Messages.DEBUG_HTML_ENABLED, html_enabled, verbose=verbose)
                
            # Generar informe en formato Markdown
            md_path = self._generate_markdown_report(src_path, metadata_info)
            
            # Generar HTML solo si está explícitamente habilitado o si PDF está activado
            html_path = None
            if md_path and html_enabled:
                html_path = self._generate_html_from_markdown(md_path)
                if html_path:
                    Messages.print_info(Messages.INFO_HTML_GENERATED, html_path)
            
            # Generar PDF si está habilitado - verificando nuevamente el flag pdf_enabled
            pdf_path = None
            if pdf_enabled and md_path:
                Messages.print_debug(Messages.DEBUG_CONVERSION_STARTED, verbose=verbose)
                Messages.print_debug(f"Archivo Markdown de origen: {md_path}", verbose=verbose)
                pdf_path = self._generate_pdf_from_markdown(md_path)
                Messages.print_debug(f"DEBUG - Resultado generación PDF: {'Éxito' if pdf_path else 'Fallo'}", verbose=verbose)
                if pdf_path is None and html_path:
                    Messages.print_info(Messages.INFO_HTML_ALTERNATIVE, html_path)
                    
            return md_path, pdf_path
            
        except Exception as e:
            Messages.print_error(f"Error al generar informe: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def _generate_markdown_report(self, src_path, metadata_info):
        """
        Genera un informe en formato Markdown.
        
        Args:
            src_path: Ruta al directorio procesado
            metadata_info: Diccionario con la información de metadatos recopilada
            
        Returns:
            str: Ruta al archivo Markdown generado o None en caso de error
        """
        try:
            # Crear directorio de informes si no existe
            report_dir = os.path.join(os.getcwd(), "reports")
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
                
            # Generar nombre de archivo basado en la fecha y hora actual
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"metadata_report_{timestamp}"
            md_path = os.path.join(report_dir, f"{base_name}.md")
            
            # Generar contenido del informe
            md_content = self._generate_markdown_content(src_path, metadata_info)
            
            # Escribir archivo Markdown
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
                
            Messages.print_info(Messages.INFO_MARKDOWN_GENERATED, md_path)
            return md_path
            
        except Exception as e:
            Messages.print_error(f"Error al generar informe Markdown: {str(e)}")
            return None
    
    def _generate_html_from_markdown(self, md_path):
        """
        Genera un informe en formato HTML a partir de un archivo Markdown.
        
        Args:
            md_path: Ruta al archivo Markdown
            
        Returns:
            str: Ruta al archivo HTML generado o None en caso de error
        """
        if not md_path or not os.path.exists(md_path):
            Messages.print_error("Error: No se puede generar HTML, el archivo Markdown no existe.")
            return None
            
        # Generar nombre de archivo HTML basado en el nombre del archivo Markdown
        report_dir = os.path.dirname(md_path)
        base_name = os.path.splitext(os.path.basename(md_path))[0]
        html_path = os.path.join(report_dir, f"{base_name}.html")
        
        try:
            # Leer el contenido del archivo Markdown
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convertir Markdown a HTML
            html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])
            
            # Añadir estilos CSS para mejorar la apariencia
            styled_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Metadatos</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 20px;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ 
            border-bottom: 2px solid #3498db; 
            padding-bottom: 10px; 
            margin-top: 30px;
        }}
        h2 {{ 
            border-bottom: 1px solid #bdc3c7; 
            padding-bottom: 5px; 
            margin-top: 25px; 
        }}
        h3 {{
            margin-top: 20px;
            background-color: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th, td {{ 
            text-align: left; 
            padding: 12px; 
            border: 1px solid #ddd; 
        }}
        th {{ 
            background-color: #f2f2f2; 
            color: #333;
            position: sticky;
            top: 0;
        }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f1f1f1; }}
        code, .file-path {{ 
            font-family: Consolas, monospace; 
            background-color: #f8f8f8; 
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .sensitive {{ 
            color: #e74c3c; 
            font-weight: bold; 
        }}
        .metadata-key {{ 
            font-weight: bold; 
            color: #2980b9; 
        }}
        pre {{ 
            background-color: #f8f8f8; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto;
            border: 1px solid #ddd;
        }}
        footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            font-size: 0.9em;
            color: #777;
        }}
    </style>
</head>
<body>
    {html_content}
    <footer>
        <p>Informe generado por MetaInfo Tool - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </footer>
</body>
</html>"""
            
            # Escribir el archivo HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(styled_html)
                
            Messages.print_info(Messages.INFO_HTML_GENERATED, html_path)
            return html_path
            
        except Exception as e:
            Messages.print_error(f"Error al generar HTML: {str(e)}")
            return None
    
    def _generate_pdf_from_markdown(self, md_path):
        """
        Genera un informe en formato PDF a partir de un archivo Markdown.
        
        Args:
            md_path: Ruta al archivo Markdown
            
        Returns:
            str: Ruta al archivo PDF generado o None en caso de error
        """
        Messages.print_info("Generando PDF...")
        
        # Verificar que pypandoc esté disponible
        if not PYPANDOC_AVAILABLE:
            Messages.print_error(Messages.ERROR_PYPANDOC_MISSING)
            Messages.print_info("Por favor, instale pypandoc: pip install pypandoc")
            return None
        
        if not md_path or not os.path.exists(md_path):
            Messages.print_error("Error: No se puede generar PDF, el archivo Markdown no existe.")
            return None
            
        # Obtener el valor de verbose desde args
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
            
        # Generar nombre de archivo PDF basado en el nombre del archivo Markdown
        report_dir = os.path.dirname(md_path)
        base_name = os.path.splitext(os.path.basename(md_path))[0]
        pdf_path = os.path.join(report_dir, f"{base_name}.pdf")
        
        try:
            # Opciones para la conversión con soporte para portada y formato mejorado
            extra_args = [
                '--pdf-engine=xelatex',
                '--variable=geometry:margin=2cm',
                '--variable=colorlinks=true',
                '--variable=fontsize=11pt',
                '--variable=mainfont=DejaVu Sans',
                '--variable=monofont=DejaVu Sans Mono',
                '--toc',
                '--toc-depth=3',
                '-V', 'lang=es',
                '--template=eisvogel',  # Intentar usar la plantilla Eisvogel si está disponible
                '--wrap=preserve'
            ]
            
            # Crear un archivo temporal de recursos para la portada
            with tempfile.NamedTemporaryFile(suffix='.tex', delete=False, mode='w', encoding='utf-8') as temp_header:
                # Personalización para la plantilla de portada si no está Eisvogel
                header_content = r"""
\usepackage{titling}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{colortbl}
\usepackage{hyperref}

% Personalización de cabecera y pie de página
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{MetaInfo Tool}
\fancyhead[R]{\thepage}
\fancyfoot[C]{Informe de Metadatos}

% Formato de tabla mejorado
\renewcommand{\arraystretch}{1.3}
\definecolor{table-row-color}{RGB}{242, 242, 242}
\definecolor{table-header-color}{RGB}{44, 62, 80}

% Comando para portada personalizada si no se usa Eisvogel
\AtBeginDocument{
  \ifdefined\eisvogeltitlepage
  \else
    \begin{titlepage}
      \centering
      \vspace*{3cm}
      \includegraphics[width=0.3\textwidth]{example-image}
      \vspace{1cm}
      
      \textcolor{teal}{\rule{\linewidth}{0.5mm}}
      \vspace{0.5cm}
      
      {\Huge\bfseries\thetitle\par}
      \vspace{0.5cm}
      
      {\Large\theauthor\par}
      \vspace{0.5cm}
      
      {\large\thedate\par}
      \vspace{0.5cm}
      
      \textcolor{teal}{\rule{\linewidth}{0.5mm}}
      \vfill
      
      {\large Generado automáticamente\par}
      \vspace{1cm}
    \end{titlepage}
    \newpage
    \tableofcontents
    \newpage
  \fi
}

% Personalización del formato de tablas
\let\oldlongtable\longtable
\let\endoldlongtable\endlongtable
\renewenvironment{longtable}{\rowcolors{2}{white}{table-row-color}\oldlongtable}{\endoldlongtable}

\let\oldtoprule\toprule
\renewcommand{\toprule}{
  \arrayrulecolor{table-header-color}
  \oldtoprule
  \arrayrulecolor{black}
}

"""
                temp_header.write(header_content)
                header_file = temp_header.name
                
            # Añadir el archivo de recursos a los argumentos
            extra_args.extend(['--include-in-header', header_file])
            
            # Crear un archivo temporal con estilos para tablas mejorados
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
                
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w', encoding='utf-8') as temp_md:
                # Añadir CSS personalizado para HTML
                table_style = """
<style>
table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}
th, td {
    text-align: left;
    padding: 8px;
    border: 1px solid #ddd;
}
th {
    background-color: #2c3e50;
    color: white;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #f2f2f2;
}
</style>

"""
                # Escribir el contenido con los estilos añadidos
                temp_md.write(table_style + md_content)
                temp_md_path = temp_md.name
            
            Messages.print_debug(Messages.DEBUG_CONVERSION_STARTED, verbose=verbose)
            Messages.print_debug(Messages.DEBUG_USING_SIMPLIFIED_OPTIONS, verbose=verbose)
            Messages.print_debug(f"Archivo Markdown temporal con estilos: {temp_md_path}", verbose=verbose)
            Messages.print_debug(f"Archivo PDF de destino: {pdf_path}", verbose=verbose)
            
            # Verificar si la plantilla Eisvogel está disponible
            eisvogel_available = False
            try:
                pandoc_data_dir = subprocess.run(
                    ["pandoc", "--version"], 
                    capture_output=True, 
                    text=True, 
                    check=True
                ).stdout
                
                if "eisvogel" in pandoc_data_dir.lower():
                    eisvogel_available = True
                    Messages.print_debug("Plantilla Eisvogel encontrada y será utilizada", verbose=verbose)
                else:
                    Messages.print_debug("Plantilla Eisvogel no encontrada, se usará formato personalizado", verbose=verbose)
                    # Remover la opción de plantilla Eisvogel si no está disponible
                    if '--template=eisvogel' in extra_args:
                        extra_args.remove('--template=eisvogel')
            except Exception:
                # Si no podemos verificar, asumimos que no está disponible
                if '--template=eisvogel' in extra_args:
                    extra_args.remove('--template=eisvogel')
            
            # Verificar si pandoc está disponible
            Messages.print_info("Versiones instaladas:")
            try:
                Messages.print_info(f"pypandoc: {pypandoc.__version__}")
                Messages.print_info(f"Pandoc: {pypandoc.get_pandoc_version()}")
            except Exception as ver_err:
                Messages.print_error(f"Error al verificar versiones: {str(ver_err)}")

            # Método 1: Conversión directa de archivo a PDF usando el archivo temporal
            success = False
            try:
                output = pypandoc.convert_file(temp_md_path, 'pdf', outputfile=pdf_path, extra_args=extra_args)
                Messages.print_info("Conversión directa completada.")
                success = True
            except Exception as simple_err:
                error_msg = str(simple_err)
                Messages.print_error(f"Error en conversión directa: {error_msg}")
                
                # Verificar si es un error relacionado con fuentes o la plantilla
                if "fontspec" in error_msg or "font" in error_msg.lower() or "cannot be found" in error_msg:
                    Messages.print_error(Messages.ERROR_FONT_NOT_FOUND)
                elif "template" in error_msg.lower() or "eisvogel" in error_msg.lower():
                    Messages.print_error("Error con la plantilla Eisvogel. Intentando con opciones más simples...")
                    # Remover la opción de plantilla si causa problemas
                    if '--template=eisvogel' in extra_args:
                        extra_args.remove('--template=eisvogel')
                
                # Método 2: Conversión con opciones simplificadas
                if not success:
                    Messages.print_info(Messages.INFO_TRYING_ALTERNATIVE)
                    try:
                        # Opciones básicas pero efectivas
                        simple_args = [
                            '--pdf-engine=xelatex',
                            '--variable=geometry:margin=2cm',
                            '--toc',
                            '--include-in-header', header_file
                        ]
                        output = pypandoc.convert_file(temp_md_path, 'pdf', outputfile=pdf_path, extra_args=simple_args)
                        Messages.print_info(Messages.INFO_SUCCESSFUL_CONVERSION)
                        success = True
                    except Exception as alt_err:
                        error_msg = str(alt_err)
                        Messages.print_error(f"Error en conversión alternativa: {error_msg}")
                
                # Método 3: Conversión en dos pasos (markdown → latex → pdf) con argumentos muy básicos
                if not success:
                    Messages.print_info(Messages.INFO_TRYING_ALTERNATIVE)
                    try:
                        latex_path = os.path.join(report_dir, f"{base_name}.tex")
                        
                        # Opciones mínimas para LaTeX
                        minimal_args = [
                            '--standalone',
                            '--variable=geometry:margin=2cm'
                        ]
                        
                        # Paso 1: Markdown a LaTeX con opciones mínimas
                        latex_content = pypandoc.convert_file(temp_md_path, 'latex', extra_args=minimal_args)
                        
                        # Añadir ajustes para tablas en LaTeX
                        table_latex_style = r"""
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}
\usepackage{colortbl}
\usepackage{xcolor}
\definecolor{table-header-color}{RGB}{44, 62, 80}
\definecolor{table-row-color}{RGB}{242, 242, 242}

\renewcommand{\arraystretch}{1.3}

% Aplicar color a las filas alternas
\let\oldlongtable\longtable
\let\endoldlongtable\endlongtable
\renewenvironment{longtable}{\rowcolors{2}{white}{table-row-color}\oldlongtable}{\endoldlongtable}

% Aplicar estilo a las cabeceras
\let\oldhead\head
\renewcommand{\head}[1]{\rowcolor{table-header-color}\color{white}\bfseries #1}
"""
                        # Insertar después del preámbulo
                        if "\\begin{document}" in latex_content:
                            latex_content = latex_content.replace("\\begin{document}", 
                                                               table_latex_style + "\\begin{document}")
                        
                        with open(latex_path, 'w', encoding='utf-8') as f:
                            f.write(latex_content)
                        Messages.print_debug(f"Archivo LaTeX intermedio generado: {latex_path}", verbose=verbose)
                        
                        # Paso 2: LaTeX a PDF usando subprocess
                        try:
                            Messages.print_info("Ejecutando pdflatex con configuración básica...")
                            result = subprocess.run(
                                ['pdflatex', '-output-directory', report_dir, latex_path],
                                capture_output=True,
                                text=True,
                                check=False
                            )
                            # Segunda ejecución para índice
                            if result.returncode == 0:
                                subprocess.run(
                                    ['pdflatex', '-output-directory', report_dir, latex_path],
                                    capture_output=True,
                                    text=True,
                                    check=False
                                )
                                success = True
                                Messages.print_info(Messages.INFO_SUCCESSFUL_CONVERSION)
                            else:
                                error_output = result.stderr if result.stderr else result.stdout
                                Messages.print_error(f"Error al ejecutar pdflatex: {error_output}")
                                
                                # Si falla pdflatex, intentar con xelatex como último recurso
                                Messages.print_info("Intentando con xelatex como alternativa final...")
                                result = subprocess.run(
                                    ['xelatex', '-output-directory', report_dir, latex_path],
                                    capture_output=True,
                                    text=True,
                                    check=False
                                )
                                if result.returncode == 0:
                                    # Segunda ejecución para índice
                                    subprocess.run(
                                        ['xelatex', '-output-directory', report_dir, latex_path],
                                        capture_output=True,
                                        text=True,
                                        check=False
                                    )
                                    success = True
                                    Messages.print_info(Messages.INFO_SUCCESSFUL_CONVERSION)
                                else:
                                    error_output = result.stderr if result.stderr else result.stdout
                                    Messages.print_error(f"Error también con xelatex: {error_output}")
                                    Messages.print_error(Messages.ERROR_PDF_CONVERSION_FAILED)
                        except Exception as latex_err:
                            Messages.print_error(f"Error en conversión LaTeX a PDF: {str(latex_err)}")
                    except Exception as twostep_err:
                        Messages.print_error(f"Error en conversión de dos pasos: {str(twostep_err)}")
                        Messages.print_error(Messages.ERROR_PDF_CONVERSION_FAILED)
            
            # Limpiar archivos temporales
            try:
                for temp_file in [temp_md_path, header_file]:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
            except Exception:
                pass
                    
            # Verificar resultado
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                Messages.print_info(Messages.INFO_PDF_GENERATED, pdf_path)
                Messages.print_debug(f"Tamaño del archivo: {os.path.getsize(pdf_path)} bytes", verbose=verbose)
                return pdf_path
            else:
                Messages.print_error(f"Error: No se pudo generar el archivo PDF o el archivo está vacío.")
                Messages.print_debug(f"Comprobando directorio de destino: {os.path.exists(os.path.dirname(pdf_path))}", verbose=verbose)
                return None
                
        except Exception as e:
            Messages.print_error(f"Error al generar PDF: {str(e)}")
            Messages.print_debug(f"Tipo de error: {type(e).__name__}", verbose=verbose)
            
            if hasattr(e, 'output'):
                Messages.print_error(f"Salida del error: {e.output}")
                
            Messages.print_info(Messages.LATEX_RECOMMENDATIONS)
            
            return None
            
    def _generate_markdown_content(self, src_path, metadata_info):
        """
        Genera el contenido del informe en formato Markdown.
        
        Args:
            src_path: Ruta al directorio procesado
            metadata_info: Diccionario con la información de metadatos recopilada
            
        Returns:
            str: Contenido del informe en formato Markdown
        """
        # Información del sistema y fecha del análisis
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Comprobar si es un informe solo de datos sensibles
        only_sensitive = ParameterValidator.safe_get(self.args, 'only_sensitive', False)
        report_title = "Informe de Análisis de Metadatos"
        if only_sensitive:
            report_title += " (Datos Sensibles)"
        
        # Añadir metadatos YAML para la generación de PDF con portada
        yaml_header = f"""---
title: "{report_title}"
author: "MetaInfo Tool"
date: "{current_time}"
subtitle: "Directorio analizado: {src_path}"
titlepage: true
titlepage-color: "2C3E50"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "FFFFFF"
titlepage-rule-height: 2
toc: true
toc-own-page: true
numbersections: true
documentclass: report
classoption: oneside
---

"""
        
        content = yaml_header + f"""# {report_title}

## Información General
- **Directorio analizado**: `{src_path}`
- **Fecha del análisis**: {current_time}
- **Total de archivos analizados**: {metadata_info.get('total_files', 0)}
- **Archivos con metadatos**: {metadata_info.get('files_with_metadata', 0)}
- **Archivos con información sensible**: {metadata_info.get('files_with_sensitive', 0)}

## Resumen por Tipo de Archivo
| Extensión | Cantidad | Con Metadatos | Con Datos Sensibles |
|-----------|----------|---------------|---------------------|
"""
        
        # Añadir estadísticas por tipo de archivo
        for ext, stats in metadata_info.get('extensions_stats', {}).items():
            content += f"| {ext} | {stats['count']} | {stats['with_metadata']} | {stats['with_sensitive']} |\n"
            
        # Añadir detalles de cada archivo con metadatos
        content += "\n## Detalles por Archivo\n\n"
        
        for file_info in metadata_info.get('files_info', []):
            file_path = file_info.get('file_path', '')
            total_metadata = file_info.get('total_metadata', 0)
            has_sensitive = file_info.get('has_sensitive', False)
            
            # Usar texto plano en lugar de emoji para compatibilidad con LaTeX
            sensitive_mark = " [ADVERTENCIA] **CONTIENE DATOS SENSIBLES**" if has_sensitive else ""
            content += f"### {os.path.basename(file_path)}{sensitive_mark}\n\n"
            content += f"**Ruta completa**: `{file_path}`\n\n"
            content += f"**Total de campos de metadatos**: {total_metadata}\n\n"
            
            # Tabla de metadatos para este archivo
            content += "| Campo | Valor | Sensible | Patrón Coincidente |\n"
            content += "|-------|-------|----------|--------------------|\n"
            
            # Añadir cada campo de metadatos
            for metadata_entry in file_info.get('metadata', []):
                key = metadata_entry.get('key', '')
                value = str(metadata_entry.get('value', '')).replace('|', '\\|').replace('\n', ' ')
                is_sensitive = metadata_entry.get('is_sensitive', False)
                patterns = metadata_entry.get('matching_patterns', [])
                
                # Acortar valores demasiado largos
                if len(value) > 100:
                    value = value[:97] + "..."
                    
                sensitive_status = "Sí" if is_sensitive else "No"
                patterns_str = ", ".join(patterns) if patterns else "-"
                
                # Añadir fila a la tabla
                content += f"| {key} | {value} | {sensitive_status} | {patterns_str} |\n"
                
            content += "\n---\n\n"
            
        # Añadir recomendaciones
        content += """## Recomendaciones de Seguridad

1. **Limpieza de Metadatos**: Considere limpiar los metadatos de archivos antes de compartirlos, especialmente aquellos marcados como sensibles.
2. **Revisión Manual**: Verifique manualmente los archivos con datos sensibles para confirmar que la información identificada es realmente sensible.
3. **Políticas de Seguridad**: Implemente políticas para la verificación rutinaria de metadatos antes de publicar o compartir archivos.
4. **Herramientas de Limpieza**: Utilice la funcionalidad de limpieza de esta herramienta ejecutando el comando con la opción `--clean`.

---

*Informe generado por MetaInfo Tool*
"""
        
        return content 