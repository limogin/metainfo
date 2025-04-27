"""
Clase para centralizar las plantillas y estilos utilizados en la generación de informes.
Este módulo permite mantener el código de las plantillas separado de la lógica de generación de informes.
"""

class Templates:
    """
    Proporciona acceso a plantillas y estilos para diferentes formatos de informe.
    """
    
    @staticmethod
    def get_html_style():
        """
        Obtiene el estilo CSS para informes HTML.
        
        Returns:
            str: Código CSS para estilizar informes HTML
        """
        return """
<style>
    body { 
        font-family: Arial, sans-serif; 
        line-height: 1.6; 
        margin: 0; 
        padding: 20px;
        color: #333;
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 { color: #2c3e50; }
    h1 { 
        border-bottom: 2px solid #3498db; 
        padding-bottom: 10px; 
        margin-top: 30px;
    }
    h2 { 
        border-bottom: 1px solid #bdc3c7; 
        padding-bottom: 5px; 
        margin-top: 25px; 
    }
    h3 {
        margin-top: 20px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 4px;
    }
    table { 
        border-collapse: collapse; 
        width: 100%; 
        margin: 20px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    th, td { 
        text-align: left; 
        padding: 12px; 
        border: 1px solid #ddd; 
    }
    th { 
        background-color: #f2f2f2; 
        color: #333;
        position: sticky;
        top: 0;
    }
    tr:nth-child(even) { background-color: #f9f9f9; }
    tr:hover { background-color: #f1f1f1; }
    code, .file-path { 
        font-family: Consolas, monospace; 
        background-color: #f8f8f8; 
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 0.9em;
    }
    .sensitive { 
        color: #e74c3c; 
        font-weight: bold; 
    }
    .metadata-key { 
        font-weight: bold; 
        color: #2980b9; 
    }
    pre { 
        background-color: #f8f8f8; 
        padding: 15px; 
        border-radius: 5px; 
        overflow-x: auto;
        border: 1px solid #ddd;
    }
    footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #eee;
        text-align: center;
        font-size: 0.9em;
        color: #777;
    }
</style>
"""

    @staticmethod
    def get_latex_header():
        """
        Obtiene el preámbulo LaTeX para informes PDF.
        
        Returns:
            str: Preámbulo LaTeX para personalizar informes PDF
        """
        return r"""
\usepackage{titling}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{colortbl}
\usepackage{hyperref}
\usepackage{etoolbox}

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

% Modificar el entorno longtable para aplicar colores alternativos a las filas de manera segura
\AtBeginEnvironment{longtable}{%
  \rowcolors{2}{white}{table-row-color}%
}

\let\oldtoprule\toprule
\renewcommand{\toprule}{
  \arrayrulecolor{table-header-color}
  \oldtoprule
  \arrayrulecolor{black}
}
"""

    @staticmethod
    def get_latex_table_style():
        """
        Obtiene el estilo LaTeX para tablas cuando se usa el método de dos pasos.
        
        Returns:
            str: Código LaTeX para estilizar tablas
        """
        return r"""
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}
\usepackage{colortbl}
\usepackage{xcolor}
\usepackage{etoolbox}
\definecolor{table-header-color}{RGB}{44, 62, 80}
\definecolor{table-row-color}{RGB}{242, 242, 242}

\renewcommand{\arraystretch}{1.3}

% Definir colores para filas de tabla de manera segura
\AtBeginEnvironment{longtable}{%
  \rowcolors{2}{white}{table-row-color}%
}

% Aplicar estilo a las cabeceras
\let\oldhead\head
\renewcommand{\head}[1]{\rowcolor{table-header-color}\color{white}\bfseries #1}
"""

    @staticmethod
    def get_basic_pandoc_args():
        """
        Obtiene los argumentos básicos para pandoc que funcionan en la mayoría de sistemas.
        
        Returns:
            list: Lista de argumentos para pandoc
        """
        return [
            '--pdf-engine=xelatex',
            '--variable=geometry:margin=2cm',
            '--toc',
            '--toc-depth=2',
            '-V', 'lang=es'
        ] 