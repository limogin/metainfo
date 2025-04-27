# Arquitectura de Capas de Metainfo

Este documento presenta la arquitectura por capas de la aplicación Metainfo.

## Diagrama de Arquitectura por Capas

```mermaid
graph TD
    subgraph "Capa de Interfaz de Usuario"
        A[Línea de Comandos]
    end

    subgraph "Capa de Aplicación"
        B[MetaInfo - Controlador Principal]
    end

    subgraph "Capa de Dominio"
        C1[Main - Coordinador]
        C2[Reporter - Generación de Informes]
        C3[Cleaner - Limpieza de Metadatos]
    end

    subgraph "Capa de Servicios"
        D1[SensitivePatterns]
        D2[SupportedExtensions]
    end

    subgraph "Capa de Infraestructura"
        E1[ExifTool]
        E2[Sistema de Archivos]
        E3[Pandoc]
    end

    %% Conexiones entre capas
    A -->|Argumentos CLI| B
    B -->|Delegación| C1
    C1 -->|Usar| C2
    C1 -->|Usar| C3
    C2 -->|Consultar| D1
    C3 -->|Consultar| D1
    C1 -->|Consultar| D2
    C2 -->|Generar Informe| E2
    C2 -->|Convertir a PDF| E3
    C3 -->|Escribir Archivos| E2
    C1 -->|Inspeccionar Metadatos| E1
```

## Descripción de las Capas

### Capa de Interfaz de Usuario
- **Línea de Comandos**: Proporciona la interfaz para interactuar con la aplicación mediante argumentos CLI.

### Capa de Aplicación
- **MetaInfo**: Actúa como controlador principal de la aplicación, procesando argumentos y delegando a las clases de dominio.

### Capa de Dominio
- **Main**: Coordina las operaciones principales, dirigiendo el flujo de trabajo entre componentes.
- **Reporter**: Responsable de generar informes con los metadatos analizados.
- **Cleaner**: Responsable de limpiar metadatos sensibles o todos los metadatos.

### Capa de Servicios
- **SensitivePatterns**: Define y gestiona los patrones considerados sensibles.
- **SupportedExtensions**: Define y gestiona las extensiones de archivo soportadas.

### Capa de Infraestructura
- **ExifTool**: Herramienta externa utilizada para extraer y manipular metadatos.
- **Sistema de Archivos**: Acceso a archivos y directorios para lectura y escritura.
- **Pandoc**: Herramienta externa para la conversión de documentos (Markdown a PDF).

## Flujo de Información

1. Los argumentos del usuario se reciben a través de la línea de comandos.
2. El controlador principal (MetaInfo) procesa estos argumentos y configura el entorno.
3. Las capas de dominio implementan la lógica principal, coordinando las operaciones solicitadas.
4. La capa de servicios proporciona funcionalidades especializadas.
5. La capa de infraestructura gestiona el acceso a herramientas y recursos externos.

Esta arquitectura por capas facilita la separación de responsabilidades y mejora la mantenibilidad del sistema. 