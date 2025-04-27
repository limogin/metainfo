# Modelo de Dominio de Metainfo

Este documento presenta el modelo de dominio de la aplicación Metainfo, mostrando las entidades principales y sus relaciones.

## Diagrama de Modelo de Dominio

```mermaid
classDiagram
    class Archivo {
        +String ruta
        +String tipo
        +DateTime fechaModificacion
        +obtenerMetadatos()
        +limpiarMetadatos(soloSensibles)
    }
    
    class Metadato {
        +String clave
        +String valor
        +Archivo archivo
        +Boolean esSensible
        +verificarSensibilidad()
    }
    
    class PatronSensible {
        +String patron
        +String idioma
        +String categoria
        +Boolean coincideCon(texto)
    }
    
    class ExtensionSoportada {
        +String extension
        +String tipoMIME
        +String descripcion
    }
    
    class Informe {
        +DateTime fechaGeneracion
        +String rutaDestino
        +String formato
        +Boolean soloSensibles
        +generarInforme()
        +exportarPDF()
    }
    
    class SistemaMetainfo {
        +String rutaOrigen
        +String rutaDestino
        +analizarDirectorio()
        +reportarMetadatos(soloSensibles)
        +limpiarMetadatos(soloSensibles)
        +mostrarPatrones()
        +mostrarExtensiones()
    }
    
    Archivo "1" -- "n" Metadato : contiene
    Metadato "n" -- "n" PatronSensible : evaluado_por
    Archivo "n" -- "n" ExtensionSoportada : identificado_por
    SistemaMetainfo "1" -- "n" Archivo : procesa
    SistemaMetainfo "1" -- "n" Informe : genera
    SistemaMetainfo "1" -- "n" PatronSensible : utiliza
    SistemaMetainfo "1" -- "n" ExtensionSoportada : soporta
```

## Explicación de las Entidades

### Archivo
Representa un archivo físico en el sistema que puede ser procesado por Metainfo.

### Metadato
Representa un par clave-valor de metadatos extraídos de un archivo.

### PatronSensible
Define los patrones que se utilizan para identificar información potencialmente sensible.

### ExtensionSoportada
Define las extensiones de archivo que son soportadas por la aplicación.

### Informe
Representa un informe generado con los metadatos analizados.

### SistemaMetainfo
Representa el sistema completo que coordina todas las operaciones.

## Relaciones Principales

- Un **Archivo** contiene múltiples **Metadatos**.
- Cada **Metadato** es evaluado por múltiples **PatronesSensibles** para determinar si contiene información sensible.
- Un **Archivo** es identificado por su **ExtensionSoportada**.
- El **SistemaMetainfo** procesa múltiples **Archivos**.
- El **SistemaMetainfo** genera múltiples **Informes**.
- El **SistemaMetainfo** utiliza **PatronesSensibles** y soporta **ExtensionesCompatibles**. 