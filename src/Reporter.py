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
from src.resources.templates import Templates

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
    {Templates.get_html_style()}
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
            # Obtener argumentos básicos de pandoc desde Templates
            extra_args = Templates.get_basic_pandoc_args()
            
            # Añadir opciones adicionales para una mejor apariencia
            extra_args.extend([
                '--variable=colorlinks=true',
                '--variable=fontsize=11pt',
                '--variable=mainfont=DejaVu Sans',
                '--variable=monofont=DejaVu Sans Mono',
                '--template=eisvogel',  # Intentar usar la plantilla Eisvogel si está disponible
                '--wrap=preserve'
            ])
            
            # Crear un archivo temporal con el encabezado LaTeX
            with tempfile.NamedTemporaryFile(suffix='.tex', delete=False, mode='w', encoding='utf-8') as temp_header:
                temp_header.write(Templates.get_latex_header())
                header_file = temp_header.name
                
            # Añadir el archivo de encabezado a los argumentos
            extra_args.extend(['--include-in-header', header_file])
            
            # Crear un archivo temporal con el contenido Markdown y estilos adicionales
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
                
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w', encoding='utf-8') as temp_md:
                # Añadir CSS para HTML (pandoc lo ignorará para PDF)
                table_style = Templates.get_html_style()
                
                # Escribir el contenido con los estilos añadidos
                temp_md.write(table_style + md_content)
                temp_md_path = temp_md.name
            
            # Mensajes de depuración
            Messages.print_debug(Messages.DEBUG_CONVERSION_STARTED, verbose=verbose)
            Messages.print_debug(f"Archivo Markdown temporal: {temp_md_path}", verbose=verbose)
            Messages.print_debug(f"Archivo PDF destino: {pdf_path}", verbose=verbose)
            
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
            
            # Mostrar versiones instaladas para depuración
            Messages.print_info("Versiones instaladas:")
            try:
                Messages.print_info(f"pypandoc: {pypandoc.__version__}")
                Messages.print_info(f"Pandoc: {pypandoc.get_pandoc_version()}")
            except Exception as ver_err:
                Messages.print_error(f"Error al verificar versiones: {str(ver_err)}")

            # ---- ESTRATEGIA 1: Conversión directa ----
            success = False
            try:
                Messages.print_info("Intentando conversión directa a PDF...")
                output = pypandoc.convert_file(temp_md_path, 'pdf', outputfile=pdf_path, extra_args=extra_args)
                Messages.print_info("Conversión directa completada con éxito.")
                success = True
            except Exception as simple_err:
                error_msg = str(simple_err)
                Messages.print_error(f"Error en conversión directa: {error_msg}")
                
                # Analizar errores comunes y ajustar la estrategia
                if "fontspec" in error_msg or "font" in error_msg.lower() or "cannot be found" in error_msg:
                    Messages.print_error(Messages.ERROR_FONT_NOT_FOUND)
                elif "template" in error_msg.lower() or "eisvogel" in error_msg.lower():
                    Messages.print_error("Error con la plantilla Eisvogel. Intentando con opciones más simples...")
                    # Remover la opción de plantilla si causa problemas
                    if '--template=eisvogel' in extra_args:
                        extra_args.remove('--template=eisvogel')
                elif "Undefined control sequence" in error_msg and "rowcolors" in error_msg:
                    Messages.print_error("Error con el comando rowcolors. Usando opciones más básicas...")
                    # Si hay error con rowcolors, usar sólo opciones básicas
                    extra_args = Templates.get_basic_pandoc_args()
                
                # ---- ESTRATEGIA 2: Conversión simplificada ----
                if not success:
                    Messages.print_info(Messages.INFO_TRYING_ALTERNATIVE)
                    try:
                        simple_args = Templates.get_basic_pandoc_args()
                        output = pypandoc.convert_file(temp_md_path, 'pdf', outputfile=pdf_path, extra_args=simple_args)
                        Messages.print_info(Messages.INFO_SUCCESSFUL_CONVERSION)
                        success = True
                    except Exception as alt_err:
                        error_msg = str(alt_err)
                        Messages.print_error(f"Error en conversión alternativa: {error_msg}")
                
                # ---- ESTRATEGIA 3: Conversión en dos pasos (Markdown → LaTeX → PDF) ----
                if not success:
                    Messages.print_info("Intentando conversión en dos pasos (Markdown → LaTeX → PDF)...")
                    try:
                        latex_path = os.path.join(report_dir, f"{base_name}.tex")
                        
                        # Convertir de Markdown a LaTeX con opciones mínimas
                        minimal_args = ['--standalone', '--variable=geometry:margin=2cm']
                        latex_content = pypandoc.convert_file(temp_md_path, 'latex', extra_args=minimal_args)
                        
                        # Añadir los estilos de LaTeX para tablas
                        if "\\begin{document}" in latex_content:
                            latex_content = latex_content.replace(
                                "\\begin{document}", 
                                Templates.get_latex_table_style() + "\\begin{document}"
                            )
                        
                        # Guardar el contenido LaTeX a un archivo
                        with open(latex_path, 'w', encoding='utf-8') as f:
                            f.write(latex_content)
                        Messages.print_debug(f"Archivo LaTeX generado: {latex_path}", verbose=verbose)
                        
                        # ---- PASO 2A: Compilar LaTeX a PDF con pdflatex ----
                        try:
                            Messages.print_info("Compilando LaTeX con pdflatex...")
                            result = subprocess.run(
                                ['pdflatex', '-output-directory', report_dir, latex_path],
                                capture_output=True, text=True, check=False
                            )
                            
                            # Segunda pasada para índice y referencias si es exitoso
                            if result.returncode == 0:
                                subprocess.run(
                                    ['pdflatex', '-output-directory', report_dir, latex_path],
                                    capture_output=True, text=True, check=False
                                )
                                success = True
                                Messages.print_info(Messages.INFO_SUCCESSFUL_CONVERSION)
                            else:
                                # Si pdflatex falla, mostrar el error
                                error_output = result.stderr if result.stderr else result.stdout
                                Messages.print_error(f"Error al compilar con pdflatex: {error_output}")
                                
                                # ---- PASO 2B: Intentar con xelatex como último recurso ----
                                Messages.print_info("Intentando compilar con xelatex...")
                                result = subprocess.run(
                                    ['xelatex', '-output-directory', report_dir, latex_path],
                                    capture_output=True, text=True, check=False
                                )
                                
                                if result.returncode == 0:
                                    # Segunda pasada para índice y referencias
                                    subprocess.run(
                                        ['xelatex', '-output-directory', report_dir, latex_path],
                                        capture_output=True, text=True, check=False
                                    )
                                    success = True
                                    Messages.print_info(Messages.INFO_SUCCESSFUL_CONVERSION)
                                else:
                                    error_output = result.stderr if result.stderr else result.stdout
                                    Messages.print_error(f"Error también con xelatex: {error_output}")
                                    Messages.print_error(Messages.ERROR_PDF_CONVERSION_FAILED)
                                    Messages.print_info(Messages.LATEX_RECOMMENDATIONS)
                        except Exception as latex_err:
                            Messages.print_error(f"Error en compilación LaTeX: {str(latex_err)}")
                    except Exception as twostep_err:
                        Messages.print_error(f"Error en proceso de dos pasos: {str(twostep_err)}")
                        Messages.print_error(Messages.ERROR_PDF_CONVERSION_FAILED)
            
            # Limpiar archivos temporales
            try:
                for temp_file in [temp_md_path, header_file]:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                # No eliminar el archivo .tex que puede ser útil para depuración
            except Exception as e:
                Messages.print_debug(f"Error al limpiar archivos temporales: {str(e)}", verbose=verbose)
                    
            # Verificar resultado final
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                Messages.print_info(Messages.INFO_PDF_GENERATED, pdf_path)
                Messages.print_debug(f"Tamaño del archivo: {os.path.getsize(pdf_path)} bytes", verbose=verbose)
                return pdf_path
            else:
                Messages.print_error("Error: No se pudo generar el archivo PDF o el archivo está vacío.")
                return None
                
        except Exception as e:
            Messages.print_error(f"Error general al generar PDF: {str(e)}")
            
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