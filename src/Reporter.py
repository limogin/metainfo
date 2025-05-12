import os
import datetime
import markdown
import tempfile
import subprocess
import sys
import pypandoc
import re

from src.Messages import Messages
from src.ParameterValidator import ParameterValidator
from src.resources.templates import Templates
from src.SensitivePatterns import SensitivePatterns

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
        self.args = main_instance.args
        self.output_path = self.args.get('output_path', "./")
        self.verbose = self.args.get('verbose', False)
        
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
            pdf_enabled = self.args.get('pdf', False)
            html_enabled = self.args.get('html', False)
            md_path = self._generate_markdown_report(src_path, metadata_info)
            
            html_path = None
            if md_path and html_enabled:
                html_path = self._generate_html_from_markdown(md_path, src_path)
                if html_path:
                    Messages.print_info(Messages.INFO_HTML_GENERATED, html_path)
            
            pdf_path = None
            if pdf_enabled and md_path:
                pdf_path = self._generate_pdf_from_markdown(md_path)
                if pdf_path is None and html_path:
                    Messages.print_info(Messages.INFO_HTML_ALTERNATIVE, html_path)
                    
            return md_path, pdf_path, html_path
            
        except Exception as e:
            Messages.print_error(f"Error al generar informe: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None, None
    
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
            # Crear directorio de informes en la ruta de salida especificada
            report_dir = os.path.join(self.output_path, "reports")
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
    
    def _generate_html_from_markdown(self, md_path, src_path):
        """
        Genera un informe en formato HTML a partir de un archivo Markdown.
        
        Args:
            md_path: Ruta al archivo Markdown
            src_path: Ruta al directorio analizado
            
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
            
            # Filtrar los metadatos YAML del contenido Markdown
            lines = md_content.split('\n')
            filtered_lines = []
            in_yaml = False
            
            for line in lines:
                if line.strip() == '---':
                    in_yaml = not in_yaml
                    continue
                if not in_yaml:
                    filtered_lines.append(line)
            
            filtered_content = '\n'.join(filtered_lines)
            
            # Convertir Markdown a HTML
            html_content = markdown.markdown(filtered_content, extensions=['tables', 'toc', 'fenced_code', 'codehilite', 'attr_list'])
            
            # Extraer el título del informe del contenido Markdown
            report_title = "Informe de Análisis de Metadatos"
            if self.args.get('only_sensitive', False):
                report_title += " (Datos Sensibles)"
                
            # Obtener la fecha y hora actual
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Añadir estilos CSS para mejorar la apariencia
            styled_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        
        .header {{
            background-color: #2C3E50;
            color: white;
            padding: 2em;
            margin: -20px -20px 2em -20px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            color: white;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            margin-top: 0.5em;
            color: #ecf0f1;
        }}
        
        .header .meta {{
            margin-top: 1em;
            font-size: 0.9em;
            color: #bdc3c7;
        }}
        
        .header .meta span {{
            margin: 0 1em;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: #2C3E50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        h1 {{ font-size: 2em; }}
        h2 {{ font-size: 1.5em; }}
        h3 {{ font-size: 1.2em; }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #2C3E50;
            color: white;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        code {{
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: #f5f5f5;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        details {{
            margin: 1em 0;
            padding: 0.5em;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        
        summary {{
            cursor: pointer;
            font-weight: bold;
            padding: 0.5em;
            background-color: #f5f5f5;
            border-radius: 3px;
        }}
        
        summary:hover {{
            background-color: #e9e9e9;
        }}
        
        footer {{
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        a {{
            color: #2980b9;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        blockquote {{
            border-left: 4px solid #2C3E50;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_title}</h1>
        <div class="subtitle">Directorio analizado: {self._sanitize_text(os.path.relpath(src_path, self.output_path))}</div>
        <div class="meta">
            <span>Fecha: {current_time}</span>
            <span>Autor: MetaInfo Tool</span>
        </div>
    </div>
    {html_content}
    <footer>
        <p>Informe generado por MetaInfo Tool - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </footer>
</body>
</html>"""            
            # Escribir el archivo HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(styled_html)
                
            return html_path
            
        except Exception as e:
            Messages.print_error(f"Error al generar HTML: {str(e)}")
            return None
    
    def _generate_pdf_from_markdown(self, md_path):
        """
        Genera un informe en formato PDF a partir de un archivo Markdown usando pandoc.
        
        Args:
            md_path: Ruta al archivo Markdown
            
        Returns:
            str: Ruta al archivo PDF generado o None en caso de error
        """
        Messages.print_info("Generando PDF...")
        
        if not md_path or not os.path.exists(md_path):
            Messages.print_error("Error: No se puede generar PDF, el archivo Markdown no existe.")
            return None
            
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        report_dir = os.path.dirname(md_path)
        base_name = os.path.splitext(os.path.basename(md_path))[0]
        pdf_path = os.path.join(report_dir, f"{base_name}.pdf")
        
        try:
            # Configurar argumentos básicos de pandoc con opciones más seguras
            extra_args = [
                '--pdf-engine=xelatex',
                '--variable=geometry:margin=2cm',
                '--variable=documentclass:article',
                '--variable=colorlinks=true',
                '--variable=linkcolor=blue',
                '--variable=urlcolor=blue',
                '--strip-comments',  # Eliminar comentarios LaTeX para evitar conflictos
                '--no-highlight',  # Desactivar resaltado de sintaxis para evitar errores
                '--toc'  # Tabla de contenidos
            ]
            
            # Crear archivo temporal con encabezado LaTeX básico y mínimo
            with tempfile.NamedTemporaryFile(suffix='.tex', delete=False, mode='w', encoding='utf-8') as temp_header:
                temp_header.write("""\\usepackage{booktabs}
\\usepackage{longtable}
\\usepackage{array}
\\usepackage{fontspec}

% Configuración básica para tablas
\\renewcommand{\\arraystretch}{1.2}
\\setlength{\\tabcolsep}{8pt}
""")
                header_file = temp_header.name
                extra_args.extend(['--include-in-header', header_file])
            
            # Leer y preparar contenido Markdown
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Limpiar caracteres problemáticos - sanitizar todo el contenido
            sanitized_md_content = ""
            lines = md_content.split('\n')
            for line in lines:
                # Mantener las líneas de YAML y Markdown intactas
                if line.startswith('---') or line.startswith('#') or line.startswith('```') or line == '':
                    sanitized_md_content += line + '\n'
                else:
                    # Sanitizar el contenido de texto
                    sanitized_line = self._sanitize_text(line)
                    sanitized_md_content += sanitized_line + '\n'
            
            # Guardar en un archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w', encoding='utf-8') as temp_md:
                temp_md.write(sanitized_md_content)
                temp_md_path = temp_md.name
            
            # Agregar un tempfile para los mensajes de error
            with tempfile.NamedTemporaryFile(suffix='.log', delete=False, mode='w', encoding='utf-8') as temp_log:
                log_file = temp_log.name
            
            # Primero intentar la conversión directa a PDF
            try:
                Messages.print_info("Intentando conversión directa a PDF...")
                output = pypandoc.convert_file(
                    temp_md_path, 
                    'pdf', 
                    outputfile=pdf_path, 
                    extra_args=extra_args
                )
                Messages.print_info("Conversión directa a PDF completada con éxito.")
                success = True
            except Exception as e:
                Messages.print_error(f"Error en conversión directa a PDF: {str(e)}")
                Messages.print_error(Messages.ERROR_PDF_CONVERSION_FAILED)
                Messages.print_info(Messages.LATEX_RECOMMENDATIONS)
                success = False
            
            # Limpiar archivos temporales
            for temp_file in [temp_md_path, header_file, log_file]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    Messages.print_debug(f"Error al limpiar archivo temporal: {str(e)}", verbose=verbose)
            
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                Messages.print_info(Messages.INFO_PDF_GENERATED, pdf_path)
                return pdf_path
            else:
                Messages.print_error("Error: No se pudo generar el archivo PDF o el archivo está vacío.")
                return None
                
        except Exception as e:
            Messages.print_error(f"Error general al generar PDF: {str(e)}")
            Messages.print_info(Messages.LATEX_RECOMMENDATIONS)
            return None
        
    def _sanitize_text(self, text):
        """
        Limpia el texto de caracteres especiales y de control que podrían causar problemas
        en la generación de PDF o HTML.
        
        Args:
            text: Texto a sanitizar
            
        Returns:
            str: Texto sanitizado
        """
        if not isinstance(text, str):
            text = str(text)
            
        # Eliminar caracteres de control invisibles (excepto espacios en blanco comunes)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Para uso en Markdown que luego se convertirá a PDF, es mejor simplificar
        # y eliminar caracteres problemáticos en lugar de escaparlos con comandos LaTeX
        text = re.sub(r'[\\{}$&#^_~%]', ' ', text)
        
        # Reemplazar barras invertidas múltiples que podrían causar problemas
        text = re.sub(r'\\+', ' ', text)
        
        # Reemplazar caracteres Unicode problemáticos
        text = text.replace('–', '-')  # En-dash
        text = text.replace('—', '-')  # Em-dash
        text = text.replace("'", "'")  # Comilla simple
        text = text.replace('"', '"')  # Comilla doble izquierda
        text = text.replace('"', '"')  # Comilla doble derecha
        text = text.replace('…', '...') # Elipsis
        
        # Reemplazar caracteres acentuados con sus equivalentes ASCII
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N',
            'ü': 'u', 'Ü': 'U',
            'ç': 'c', 'Ç': 'C',
            'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
            'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
            'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
            'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O', 'Ü': 'U',
            'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
            'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U',
            '©': '(c)', '®': '(R)', '™': '(TM)',
            '€': 'EUR', '£': 'GBP', '¥': 'JPY',
            '°': ' grados ', '²': '2', '³': '3',
            '±': '+/-', '×': 'x', '÷': '/',
            '≤': '<=', '≥': '>=', '≠': '!=',
            '≈': '~=', '≡': '==='
        }
        
        for original, replacement in replacements.items():
            text = text.replace(original, replacement)
        
        # Eliminar cualquier otro carácter no ASCII
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        return text
        
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
subtitle: "Directorio analizado: {self._sanitize_text(os.path.relpath(src_path, self.output_path))}"
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
- **Directorio analizado**: `{self._sanitize_text(os.path.relpath(src_path, self.output_path))}`
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
            content += f"| {self._sanitize_text(ext)} | {stats['count']} | {stats['with_metadata']} | {stats['with_sensitive']} |\n"
            
        # Añadir detalles de cada archivo con metadatos
        content += "\n## Detalles por Archivo\n\n"
        
        for file_info in metadata_info.get('files_info', []):
            file_path = file_info.get('file_path', '')
            # La ruta ya es relativa desde _process_directory_for_report
            rel_path = file_path
            total_metadata = file_info.get('total_metadata', 0)
            has_sensitive = file_info.get('has_sensitive', False)
            
            content += f"### {self._sanitize_text(os.path.basename(file_path))}\n\n"
            content += f"**Ruta relativa**: `{self._sanitize_text(rel_path)}`\n\n"
            content += f"**Total de campos de metadatos**: {total_metadata}\n\n"
            if (has_sensitive):
              content += f"**Estado de datos sensibles**: {'Se han encontrado coincidencias de datos sensibles'}\n\n"
            
            # Tabla de metadatos para este archivo
            content += "| Campo | Valor | Sensible | Patrón Coincidente |\n"
            content += "|-------|-------|----------|--------------------|\n"
            
            # Añadir cada campo de metadatos
            for metadata_entry in file_info.get('metadata', []):
                key = self._sanitize_text(metadata_entry.get('key', ''))
                raw_value = str(metadata_entry.get('value', '')).replace('|', '\\|').replace('\n', ' ')
                
                # Convertir rutas absolutas a relativas si es necesario
                if os.path.isabs(raw_value) and os.path.exists(raw_value):
                    raw_value = os.path.relpath(raw_value, self.main.src_path)
                
                # Sanitizar el valor
                value = self._sanitize_text(raw_value)
                
                is_sensitive = metadata_entry.get('is_sensitive', False)
                patterns = metadata_entry.get('matching_patterns', [])
                
                # Acortar valores demasiado largos
                if len(value) > 100:
                    value = value[:97] + "..."
                    
                sensitive_status = "Sí" if is_sensitive else "No"
                patterns_str = ", ".join(self._sanitize_text(pattern) for pattern in patterns) if patterns else "-"
                
                # Añadir fila a la tabla
                content += f"| {key} | {value} | {sensitive_status} | {patterns_str} |\n"
                
            content += "\n---\n\n"
            
        # Añadir recomendaciones
        content += """## Recomendaciones de Seguridad

1. **Limpieza de Metadatos**: Considere limpiar los metadatos de archivos antes de compartirlos, especialmente aquellos marcados como sensibles.
2. **Revisión Manual**: Verifique manualmente los archivos con datos sensibles para confirmar que la información identificada es realmente sensible.
3. **Políticas de Seguridad**: Implemente políticas para la verificación rutinaria de metadatos antes de publicar o compartir archivos.
4. **Herramientas de Limpieza**: Utilice la funcionalidad de limpieza de esta herramienta ejecutando el comando con la opción `--clean`.

"""

        # Añadir sección con los patrones utilizados para detectar información sensible
        content += """## Patrones de Detección de Información Sensible

A continuación se muestran los patrones utilizados por MetaInfo para identificar potencialmente información sensible en los metadatos.

"""
        # Añadir patrones en español
        content += "### Español\n"
        spanish_patterns = ", ".join(f"`{p}`" for p in self.main.sensitive_patterns if p in SensitivePatterns.SPANISH)
        content += f"{spanish_patterns}\n\n"
        
        # Añadir patrones en inglés
        content += "### Inglés\n"
        english_patterns = ", ".join(f"`{p}`" for p in self.main.sensitive_patterns if p in SensitivePatterns.ENGLISH)
        content += f"{english_patterns}\n\n"
        
        # Añadir patrones de dispositivos
        content += "### Metadatos de Dispositivos\n"
        device_patterns = ", ".join(f"`{p}`" for p in self.main.sensitive_patterns if p in SensitivePatterns.DEVICE_METADATA)
        content += f"{device_patterns}\n\n"
        
        # Añadir otros idiomas en sección contraída
        content += "<details>\n<summary>Patrones en otros idiomas (Francés, Alemán, Italiano, Portugués)</summary>\n\n"
        
        # Francés
        content += "#### Francés\n"
        french_patterns = ", ".join(f"`{p}`" for p in self.main.sensitive_patterns if p in SensitivePatterns.FRENCH)
        content += f"{french_patterns}\n\n"
        
        # Alemán
        content += "#### Alemán\n"
        german_patterns = ", ".join(f"`{p}`" for p in self.main.sensitive_patterns if p in SensitivePatterns.GERMAN)
        content += f"{german_patterns}\n\n"
        
        # Italiano
        content += "#### Italiano\n"
        italian_patterns = ", ".join(f"`{p}`" for p in self.main.sensitive_patterns if p in SensitivePatterns.ITALIAN)
        content += f"{italian_patterns}\n\n"
        
        # Portugués
        content += "#### Portugués\n"
        portuguese_patterns = ", ".join(f"`{p}`" for p in self.main.sensitive_patterns if p in SensitivePatterns.PORTUGUESE)
        content += f"{portuguese_patterns}\n\n"
        
        content += "</details>\n\n"
        
        content += "---\n\n*Informe generado por MetaInfo Tool*\n"
        
        return content

    def _check_sensitive_data(self, key, val):
        """
        Verifica si una clave o valor contiene datos sensibles.
        
        Args:
            key: Clave del metadato
            val: Valor del metadato
            
        Returns:
            tuple: (es_sensible, patrones_coincidentes)
                - es_sensible: True si se encontró un patrón sensible
                - patrones_coincidentes: Lista de patrones que coincidieron
        """
        # Convertir clave y valor a string para poder buscar coincidencias
        key_str = str(key).lower()
        val_str = str(val).lower()
        
        # Hacer una excepción para ciertas claves
        if key_str == 'author' and not any(pattern.lower() in val_str for pattern in self.main.sensitive_patterns):
            return False, []
            
        # Verificar si algún patrón sensible coincide con la clave o el valor
        is_sensitive = False
        matching_patterns = []

        is_negative = False
        for negative_pattern in self.main.negative_patterns:
            negative_lower = negative_pattern.lower()
                
            if negative_lower in key_str:
                is_negative = True
                break
            
        if is_negative:
            return False, []
        
        for pattern in self.main.sensitive_patterns:
            pattern_lower = pattern.lower()
            
            # Si el patrón tiene 3 o menos caracteres, usar coincidencia exacta
            if len(pattern_lower) <= 3:
                if key_str == pattern_lower or val_str == pattern_lower:
                    is_sensitive = True
                    matching_patterns.append(pattern)
            else:
                if pattern_lower in key_str or pattern_lower in val_str:
                    is_sensitive = True
                    matching_patterns.append(pattern)
        
        return is_sensitive, matching_patterns

    def _process_directory_for_report(self, directory, metadata_info):
        """
        Procesa recursivamente un directorio recopilando información de metadatos.
        
        Args:
            directory: Ruta al directorio a procesar
            metadata_info: Diccionario donde se almacena la información recopilada
        """
        lower_extensions = tuple(ext.lower() for ext in self.main.extensions)
        upper_extensions = tuple(ext.upper() for ext in self.main.extensions)
        only_sensitive = ParameterValidator.safe_get(self.args, 'only_sensitive', False)
        verbose = ParameterValidator.safe_get(self.args, 'verbose', False)
        
        if only_sensitive and verbose:
            Messages.print_debug("Procesando directorio con filtro de solo datos sensibles", verbose=True)
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path):
                # Verificar si el archivo tiene una extensión soportada
                ext = os.path.splitext(item_path)[1].lower()
                if ext and (item.lower().endswith(lower_extensions) or item.upper().endswith(upper_extensions)):
                    metadata_info['total_files'] += 1
                    Messages.print_debug(Messages.DEBUG_READING_FILE, item_path, verbose=verbose)
                    
                    # Actualizar estadísticas de extensiones
                    if ext not in metadata_info['extensions_stats']:
                        metadata_info['extensions_stats'][ext] = {
                            'count': 0,
                            'with_metadata': 0,
                            'with_sensitive': 0
                        }
                    metadata_info['extensions_stats'][ext]['count'] += 1
                    
                    # Recopilar metadatos
                    metadata = self.main.inspect(item_path)
                    file_info = {
                        'file_path': os.path.relpath(item_path, self.main.src_path),
                        'total_metadata': 0,
                        'has_sensitive': False,
                        'metadata': []
                    }
                    
                    has_metadata = False
                    has_sensitive_data = False
                    sensitive_metadata_count = 0
                    
                    for data in metadata:
                        if hasattr(data, 'items') and callable(data.items):
                            for key, val in data.items():
                                has_metadata = True
                                file_info['total_metadata'] += 1
                                
                                # Sanitizar clave y valor para la verificación de datos sensibles
                                clean_key = key
                                clean_val = val
                                
                                # Verificar si es sensible
                                is_sensitive, matching_patterns = self._check_sensitive_data(clean_key, clean_val)
                                
                                if is_sensitive:
                                    has_sensitive_data = True
                                    file_info['has_sensitive'] = True
                                    sensitive_metadata_count += 1
                                
                                # Si solo queremos datos sensibles, solo añadir los que son sensibles
                                if not only_sensitive or is_sensitive:
                                    metadata_entry = {
                                        'key': key,
                                        'value': val,
                                        'is_sensitive': is_sensitive,
                                        'matching_patterns': matching_patterns
                                    }
                                    file_info['metadata'].append(metadata_entry)
                    
                    # Solo incluir archivos con metadatos
                    if has_metadata:
                        metadata_info['files_with_metadata'] += 1
                        metadata_info['extensions_stats'][ext]['with_metadata'] += 1
                        
                        if has_sensitive_data:
                            metadata_info['files_with_sensitive'] += 1
                            metadata_info['extensions_stats'][ext]['with_sensitive'] += 1
                            
                            if only_sensitive and verbose:
                                Messages.print_debug(f"Archivo {item_path} contiene {sensitive_metadata_count} metadatos sensibles", verbose=True)
                        
                        # Si solo queremos datos sensibles, solo incluir archivos que tengan datos sensibles
                        if not only_sensitive or has_sensitive_data:
                            metadata_info['files_info'].append(file_info)
            
            elif os.path.isdir(item_path):
                # Procesar subdirectorios recursivamente
                self._process_directory_for_report(item_path, metadata_info) 