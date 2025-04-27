# Diagramas de Interacción - MetaInfo

Este documento presenta diagramas de interacción que muestran el comportamiento dinámico del sistema, ilustrando cómo los distintos componentes de MetaInfo colaboran para realizar las tareas principales.

## Diagrama de Secuencia: Generación de Informe

El siguiente diagrama muestra la secuencia de interacciones entre componentes para generar un informe de metadatos.

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as Línea de Comandos
    participant Main
    participant Scanner as Scanner de Archivos
    participant SensitivePat as SensitivePatterns
    participant Reporter
    participant ExifTool
    participant FS as Sistema de Archivos
    
    Usuario->>CLI: Ejecutar comando con --report_all
    CLI->>Main: Inicializar con argumentos
    
    Main->>Scanner: Escanear directorio
    Scanner->>FS: Listar archivos recursivamente
    FS-->>Scanner: Lista de archivos
    Scanner-->>Main: Lista de archivos a procesar
    
    loop Para cada archivo
        Main->>ExifTool: inspect(archivo)
        ExifTool->>FS: Leer metadatos
        FS-->>ExifTool: Datos binarios
        ExifTool-->>Main: Metadatos extraídos
        
        loop Para cada campo de metadatos
            Main->>SensitivePat: _check_sensitive_data(key, value)
            SensitivePat-->>Main: (is_sensitive, matching_patterns)
        end
        
        Main->>Main: Actualizar estadísticas
    end
    
    Main->>Reporter: generate_report(src_path, metadata_info)
    Reporter->>Reporter: _generate_markdown_content()
    Reporter->>FS: Escribir informe Markdown
    
    alt Se solicitó PDF
        Reporter->>Reporter: Convertir a PDF
        Reporter->>FS: Escribir informe PDF
    end
    
    Reporter-->>Main: (md_path, pdf_path)
    Main-->>CLI: Resultado
    CLI-->>Usuario: Notificación de finalización
```

## Diagrama de Secuencia: Limpieza de Metadatos Sensibles

El siguiente diagrama muestra la secuencia de interacciones para eliminar metadatos sensibles de los archivos.

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as Línea de Comandos
    participant Main
    participant Cleaner
    participant SensitivePat as SensitivePatterns
    participant ExifTool
    participant FS as Sistema de Archivos
    
    Usuario->>CLI: Ejecutar comando con --wipe_sensitive
    CLI->>Main: Inicializar con argumentos
    Main->>Cleaner: clean_metadata(src_path)
    
    Cleaner->>Cleaner: _process_directory()
    Cleaner->>FS: Listar archivos recursivamente
    FS-->>Cleaner: Lista de archivos
    
    loop Para cada archivo compatible
        Cleaner->>Main: inspect(file_path)
        Main->>ExifTool: Extraer metadatos
        ExifTool-->>Main: Metadatos extraídos
        Main-->>Cleaner: Metadatos
        
        loop Para cada campo de metadatos
            Cleaner->>Main: _check_sensitive_data(key, value)
            Main->>SensitivePat: Verificar sensibilidad
            SensitivePat-->>Main: (is_sensitive, matching_patterns)
            Main-->>Cleaner: (is_sensitive, matching_patterns)
            
            alt Metadato es sensible
                Cleaner->>ExifTool: Eliminar campo específico
                ExifTool->>FS: Modificar archivo
            end
        end
        
        Cleaner->>CLI: Notificar progreso
        CLI-->>Usuario: Mostrar progreso
    end
    
    Cleaner-->>Main: True/False (éxito/error)
    Main-->>CLI: Resultado final
    CLI-->>Usuario: Notificación de finalización
```

## Diagrama de Colaboración: Detección de Datos Sensibles

El siguiente diagrama muestra cómo colaboran los objetos durante el proceso de detección de datos sensibles.

```mermaid
graph TD
    User([Usuario]) -- "1. Iniciar análisis" --> CLI
    
    subgraph "Flujo de Colaboración"
        CLI[Línea de Comandos] -- "2. Parsear argumentos" --> Main
        Main -- "3. Solicitar patrones" --> SensitivePatterns
        SensitivePatterns -- "4. Devolver patrones" --> Main
        Main -- "5. Escanear directorios" --> FileSystem
        FileSystem -- "6. Devolver archivos" --> Main
        Main -- "7. Extraer metadatos" --> ExifTool
        ExifTool -- "8. Devolver metadatos" --> Main
        Main -- "9. Verificar sensibilidad" --> SensitivePatterns
        SensitivePatterns -- "10. Confirmar coincidencias" --> Main
        Main -- "11. Actualizar estadísticas" --> Reporter
        Reporter -- "12. Generar informe" --> FileSystem
    end
    
    FileSystem -- "13. Archivo creado" --> User
```

## Diagrama de Secuencia: Consulta de Patrones Sensibles

El siguiente diagrama muestra la interacción cuando un usuario consulta los patrones sensibles.

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as Línea de Comandos
    participant Main
    participant SensitivePat as SensitivePatterns
    
    Usuario->>CLI: Ejecutar --show_patterns
    CLI->>Main: Procesar argumentos
    Main->>SensitivePat: print_patterns_by_language()
    SensitivePat-->>Main: Patrones formateados
    Main-->>CLI: Mostrar patrones
    CLI-->>Usuario: Visualizar patrones sensibles
```

## Diagrama de Estados: Procesamiento de un Archivo

El siguiente diagrama muestra los estados por los que pasa un archivo durante su procesamiento.

```mermaid
stateDiagram-v2
    [*] --> Identificado: Encontrado en directorio
    
    Identificado --> NoSoportado: Extensión no soportada
    NoSoportado --> [*]: Ignorar archivo
    
    Identificado --> EnProceso: Extensión soportada
    EnProceso --> Extraído: Extracción de metadatos
    
    Extraído --> Analizado: Análisis de sensibilidad
    
    Analizado --> SinMetadatos: No contiene metadatos
    SinMetadatos --> Reportado: Añadir a estadísticas
    
    Analizado --> ConMetadatos: Contiene metadatos
    ConMetadatos --> ConDatosSensibles: Contiene datos sensibles
    ConMetadatos --> SinDatosSensibles: No contiene datos sensibles
    
    ConDatosSensibles --> Reportado: Añadir a informe
    SinDatosSensibles --> Reportado: Añadir a informe
    
    state AlternativaLimpieza {
        [*] --> EnEspera: Modo limpieza
        EnEspera --> LimpiandoTodo: Opción --wipe_all
        EnEspera --> LimpiandoSensible: Opción --wipe_sensitive
        LimpiandoTodo --> Limpio: Eliminar todos los metadatos
        LimpiandoSensible --> Limpio: Eliminar solo metadatos sensibles
        Limpio --> [*]
    }
    
    Reportado --> [*]: Finalizar procesamiento
```

## Diagrama de Secuencia: Caso de Error en la Extracción de Metadatos

El siguiente diagrama muestra cómo el sistema maneja situaciones de error durante la extracción de metadatos.

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as Línea de Comandos
    participant Main
    participant ExifTool
    participant FS as Sistema de Archivos
    
    Usuario->>CLI: Ejecutar comando
    CLI->>Main: Inicializar con argumentos
    Main->>ExifTool: inspect(archivo)
    
    alt ExifTool disponible
        ExifTool->>FS: Intentar leer metadatos
        
        alt Archivo accesible
            FS-->>ExifTool: Datos binarios
            ExifTool-->>Main: Metadatos extraídos
        else Archivo no accesible
            FS--x ExifTool: Error de acceso
            ExifTool-->>Main: {"error": "No se puede acceder al archivo"}
        end
        
    else ExifTool no disponible
        ExifTool-->>Main: {"error": "exiftool no está disponible"}
    end
    
    Main-->>CLI: Notificar resultado/error
    CLI-->>Usuario: Mostrar resultado/error
```

## Explicación de los Diagramas

### Generación de Informe
Este diagrama muestra cómo el sistema procesa una solicitud para generar un informe. Ilustra el flujo desde la entrada del comando hasta la generación del archivo de informe, mostrando cómo se escanean los archivos, se extraen y analizan los metadatos, y se genera el informe.

### Limpieza de Metadatos Sensibles
Este diagrama detalla el proceso de limpieza selectiva de metadatos sensibles. Muestra cómo se identifica la información sensible y cómo se elimina mientras se preserva el resto de los metadatos.

### Detección de Datos Sensibles
Este diagrama de colaboración muestra las interacciones entre los diferentes componentes durante el proceso de detección de datos sensibles, destacando el flujo de la información y la colaboración entre objetos.

### Consulta de Patrones Sensibles
Este diagrama simple muestra la interacción cuando un usuario solicita ver los patrones considerados sensibles por el sistema.

### Estados de Procesamiento de un Archivo
Este diagrama de estados ilustra los diferentes estados por los que puede pasar un archivo durante su procesamiento, desde su identificación inicial hasta el informe final o la limpieza.

### Manejo de Errores
El último diagrama muestra cómo el sistema maneja situaciones de error durante la extracción de metadatos, ya sea por la falta de disponibilidad de ExifTool o por problemas al acceder a los archivos. 