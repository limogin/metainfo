import os
import datetime
import markdown
import pdfkit

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
        self.args = main_instance.args if hasattr(main_instance, 'args') else None
        
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
                
            print(f"Reporte Markdown generado: {md_path}")
            
            # Generar PDF si está habilitado
            pdf_path = None
            if self.args and self.args.pdf:
                pdf_path = os.path.join(report_dir, f"{base_name}.pdf")
                try:
                    # Convertir Markdown a HTML primero
                    html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])
                    
                    # Añadir estilos CSS básicos para mejorar la apariencia
                    styled_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                            h1, h2, h3 {{ color: #2c3e50; }}
                            h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                            h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; margin-top: 20px; }}
                            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                            th, td {{ text-align: left; padding: 8px; border: 1px solid #ddd; }}
                            th {{ background-color: #f2f2f2; color: #333; }}
                            tr:nth-child(even) {{ background-color: #f9f9f9; }}
                            .file-path {{ font-family: monospace; background-color: #f8f8f8; padding: 2px 5px; }}
                            .sensitive {{ color: #e74c3c; font-weight: bold; }}
                            .metadata-key {{ font-weight: bold; color: #2980b9; }}
                            pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        </style>
                    </head>
                    <body>
                        {html_content}
                    </body>
                    </html>
                    """
                    
                    # Opciones para pdfkit
                    options = {
                        'page-size': 'A4',
                        'margin-top': '20mm',
                        'margin-right': '20mm',
                        'margin-bottom': '20mm',
                        'margin-left': '20mm',
                        'encoding': 'UTF-8',
                        'enable-local-file-access': None
                    }
                    
                    # Generar PDF desde HTML
                    pdfkit.from_string(styled_html, pdf_path, options=options)
                    print(f"Reporte PDF generado: {pdf_path}")
                    
                except Exception as e:
                    print(f"Error al generar PDF: {str(e)}")
                    print("Asegúrese de tener wkhtmltopdf instalado: https://wkhtmltopdf.org/downloads.html")
                    pdf_path = None
                    
            return md_path, pdf_path
            
        except Exception as e:
            print(f"Error al generar informe: {str(e)}")
            return None, None
            
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
        
        content = f"""# Informe de Análisis de Metadatos

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
            
            # Añadir encabezado de archivo con icono de advertencia si tiene datos sensibles
            sensitive_mark = " ⚠️ **CONTIENE DATOS SENSIBLES**" if has_sensitive else ""
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