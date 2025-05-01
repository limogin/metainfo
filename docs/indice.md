# Índice de la Documentación de MetaInfo

## Navegación Rápida

- 📋 [**Actualizaciones Recientes**](README.md) - Últimas mejoras implementadas
- 📚 [**Índice Técnico**](indice_tecnico.md) - Guía técnica detallada
- 🔍 [**Casos de Uso**](casos_uso.md) - Escenarios de interacción usuario-sistema
- 🏗️ [**Arquitectura**](#documentos-de-arquitectura) - Documentos sobre la estructura del sistema
- 📊 [**Diagramas**](#documentos-de-diagramas) - Representaciones visuales del sistema

## Introducción

MetaInfo es una aplicación especializada en el análisis y gestión de metadatos en archivos digitales. Esta documentación está estructurada para proporcionar una comprensión progresiva del sistema, sus fundamentos teóricos y su implementación práctica.

## Documentos de Arquitectura

- [**Modelo de Dominio**](modelo_dominio.md) - Conceptos clave y relaciones
- [**Arquitectura por Capas**](arquitectura_capas.md) - Estructura general del sistema
- [**Arquitectura Modular**](arquitectura_modular.md) - Componentes y sus interacciones
- [**Diagrama de Componentes**](diagrama_componentes.md) - Visión de alto nivel de los módulos del sistema

## Documentos de Diagramas

- [**Diagrama de Clases**](diagrama_clases.md) - Diseño estático y relaciones entre clases
- [**Diagramas de Interacción**](diagramas_interaccion.md) - Comportamiento dinámico del sistema
- [**Diagrama de Flujo de Datos**](diagrama_flujo_datos.md) - Procesamiento de información

## Metodología de Desarrollo

La documentación sigue los principios del **Proceso Unificado (UP)** utilizando notación **UML**:

- **Dirigido por casos de uso**: La arquitectura se centra en resolver escenarios de uso específicos
- **Centrado en la arquitectura**: Estructura modular con separación clara de responsabilidades
- **Iterativo e incremental**: Desarrollo por fases con mejoras continuas
- **Dirigido por riesgos**: Análisis temprano de riesgos técnicos y de negocio
- **Verificación continua de la calidad**: Pruebas unitarias e integración automatizadas

## Aspectos Funcionales

### Gestión de Metadatos
MetaInfo ofrece capacidades para:

- **Detectar y extraer** metadatos de diversos tipos de archivos
- **Identificar información sensible** mediante patrones predefinidos y personalizables
- **Generar informes detallados** en formatos Markdown, HTML y PDF con rutas relativas
- **Limpiar selectivamente** metadatos que contienen información sensible
- **Manejo inteligente de archivos** omitiendo formatos sin metadatos relevantes
- **Recuperación de errores robusta** con múltiples estrategias de limpieza

### Extensibilidad
El sistema está diseñado para facilitar:

- La incorporación de **nuevos formatos de archivo**
- La definición de **patrones adicionales** para detectar información sensible
- La implementación de **nuevos formatos de informe**
- La integración de **estrategias alternativas de limpieza**
- La exclusión de **tipos de archivo específicos** del procesamiento

## Guía de Estudio Recomendada

Para comprender el sistema de manera efectiva, se recomienda seguir este orden:

1. Primero: [**Actualizaciones Recientes**](README.md) y [**Modelo de Dominio**](modelo_dominio.md)
2. Segundo: [**Casos de Uso**](casos_uso.md) y [**Arquitectura por Capas**](arquitectura_capas.md)
3. Tercero: [**Diagrama de Componentes**](diagrama_componentes.md) y [**Diagrama de Clases**](diagrama_clases.md)
4. Finalmente: [**Diagramas de Interacción**](diagramas_interaccion.md) y [**Diagrama de Flujo de Datos**](diagrama_flujo_datos.md)

---

*Última actualización: 11/06/2024* 