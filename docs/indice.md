# Índice de la Documentación de MetaInfo

## Navegación Rápida

- 📋 [**Introducción**](#introducción) - ¿Qué es MetaInfo y para qué sirve?
- 📚 [**Casos de Uso**](casos_uso.md) - Ejemplos prácticos de uso de la aplicación
- 🔍 [**Diagrama de Clases**](diagrama_clases.md) - Estructura principal del sistema
- 📊 [**Instalación y Uso**](README.md#instalación-y-dependencias) - Cómo empezar con MetaInfo
- 🏗️ [**Actualizaciones Recientes**](README.md#actualizaciones-recientes) - Últimas mejoras

## Introducción

MetaInfo es una aplicación especializada en el análisis y gestión de metadatos en archivos digitales. Permite:

- **Detectar y extraer** metadatos de diversos tipos de archivos (imágenes, documentos, etc.)
- **Identificar información sensible** que podría comprometer tu privacidad
- **Generar informes detallados** en formatos fáciles de consultar (Markdown, HTML, PDF)
- **Limpiar selectivamente** metadatos sensibles o eliminarlos todos si lo prefieres

La aplicación está diseñada para ser fácil de usar tanto para usuarios sin conocimientos técnicos como para profesionales de seguridad informática.

## Estructura de la Documentación

Para entender cómo funciona MetaInfo, recomendamos seguir este orden:

1. [**Casos de Uso**](casos_uso.md) - Visualiza cómo diferentes personas utilizan la aplicación
2. [**Diagrama de Clases**](diagrama_clases.md) - Comprende la estructura principal del sistema

### ¿Qué puedo hacer con MetaInfo?

- **Como usuario general**: Analizar archivos para descubrir qué información contienen
- **Como fotógrafo**: Limpiar datos de localización y dispositivo de tus fotos antes de publicarlas
- **Como especialista en seguridad**: Identificar y eliminar información sensible en documentos
- **Como administrador IT**: Preparar documentos para publicación eliminando todos los metadatos

## Aspectos Técnicos Principales

MetaInfo está desarrollada siguiendo principios de diseño profesional que aseguran su calidad:

- **Diseño modular**: Cada parte de la aplicación tiene una responsabilidad específica
- **Extensibilidad**: Facilidad para añadir nuevos formatos de archivo y patrones de detección
- **Robustez**: Manejo inteligente de errores y múltiples estrategias de procesamiento

La implementación sigue metodologías estándar de la industria como patrones GRASP (Alta Cohesión, Bajo Acoplamiento) y patrones GoF (Factory, Strategy), lo que garantiza un código organizado y mantenible.

## Ejemplos de Uso Rápido

Para analizar archivos y generar un informe:
```bash
python metainfo.py --i ~/Documentos --report_all --o ~/Informes --pdf
```

Para limpiar metadatos sensibles:
```bash
python metainfo.py --i ~/Fotos/Privadas --wipe_sensitive --verbose
```

## Guía de Estudio Recomendada

Para comprender el sistema de manera efectiva, se recomienda seguir este orden:

1. [**Actualizaciones Recientes**](README.md#actualizaciones-recientes)
2. [**Casos de Uso**](casos_uso.md) 
3. [**Diagrama de Clases**](diagrama_clases.md)

---

*Última actualización: 11/06/2024* 