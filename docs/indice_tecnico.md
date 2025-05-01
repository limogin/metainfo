# Índice de Documentación Técnica

## Introducción

Este documento sirve como índice principal para la documentación técnica de MetaInfo, una herramienta especializada en el análisis y gestión de metadatos en archivos digitales. El índice está organizado siguiendo un enfoque metodológico que facilita la comprensión progresiva del sistema, desde sus aspectos conceptuales hasta los detalles de implementación.

## Metodología de Desarrollo

Esta documentación técnica está estructurada siguiendo los principios del **Proceso Unificado (UP)** con notación **UML** (Unified Modeling Language), e implementa los patrones de diseño **GRASP** (General Responsibility Assignment Software Patterns) y **GoF** (Gang of Four) para garantizar un diseño orientado a objetos de alta calidad.

### Contexto de Aplicación

MetaInfo es una herramienta especializada para el análisis y gestión de metadatos en archivos digitales, con enfoque particular en la identificación y tratamiento de información sensible. La implementación sigue un enfoque modular que separa claramente las responsabilidades entre:

- Extracción de metadatos
- Análisis de patrones sensibles
- Generación de informes en múltiples formatos
- Limpieza selectiva de metadatos

La arquitectura aprovecha los principios GRASP (Creador, Controlador, Polimorfismo, Alta Cohesión y Bajo Acoplamiento) para distribuir responsabilidades, y patrones GoF (principalmente Factory, Strategy, Template Method y Observer) para resolver problemas recurrentes de diseño.

## Itinerario de Estudio Recomendado

Para comprender completamente la arquitectura y funcionamiento de MetaInfo, se recomienda seguir este itinerario de estudio:

1. **[Modelo de Dominio](modelo_dominio.md)**
   * Visión conceptual de las entidades principales
   * Relaciones entre conceptos clave
   * Glosario de términos técnicos específicos

2. **[Casos de Uso](casos_uso.md)**
   * Escenarios de uso principales
   * Flujos de interacción usuario-sistema
   * Precondiciones y postcondiciones

3. **[Arquitectura por Capas](arquitectura_capas.md)**
   * Estructura general de la aplicación
   * Separación de responsabilidades
   * Patrones de diseño arquitectónicos

4. **[Diagrama de Clases](diagrama_clases.md)**
   * Estructura estática del sistema
   * Aplicación de patrones GRASP
   * Implementación de patrones GoF

5. **[Diagramas de Interacción](diagramas_interaccion.md)**
   * Diagramas de secuencia para operaciones clave
   * Diagramas de colaboración
   * Comportamiento dinámico del sistema

6. **[Arquitectura Modular](arquitectura_modular.md)**
   * Componentes principales
   * Mecanismos de extensibilidad
   * Gestión de dependencias

7. **[Diagrama de Flujo de Datos](diagrama_flujo_datos.md)**
   * Procesamiento de metadatos
   * Flujos de información
   * Puntos de integración

## Aspectos Funcionales Destacados

### Gestión de Metadatos
La aplicación permite la detección, análisis y manipulación de metadatos en diversos tipos de archivos, centrándose en:

- **Extracción de metadatos**: Identificación y extracción de metadatos de múltiples formatos de archivo mediante herramientas especializadas
- **Detección de información sensible**: Identificación de patrones sensibles en los metadatos mediante expresiones regulares y análisis heurístico
- **Limpieza selectiva**: Capacidad para eliminar solo los metadatos que contienen información sensible
- **Generación de informes**: Creación de reportes detallados en formatos Markdown, HTML y PDF

### Extensibilidad del Sistema
El diseño modular facilita la incorporación de:

- Nuevos formatos de archivo para análisis
- Patrones adicionales para la detección de información sensible
- Formatos de informe personalizados
- Estrategias alternativas de limpieza de metadatos

## Patrones GRASP Implementados

* **Creador**: Asignación de responsabilidades de creación a clases específicas (ej: `Main` crea instancias de `Reporter`).
* **Controlador**: Centralización de la lógica de control en clases como `MetaInfo` y `Main`.
* **Alta Cohesión**: Agrupación de funcionalidades relacionadas (ej: separación entre `Messages` y `ParameterValidator`).
* **Bajo Acoplamiento**: Minimización de dependencias entre módulos.
* **Polimorfismo**: Implementación de interfaces comunes para comportamientos variables.

## Patrones GoF Implementados

* **Factory Method**: Creación centralizada de informes en distintos formatos.
* **Strategy**: Diferentes estrategias para el procesamiento de metadatos según el tipo de archivo.
* **Template Method**: Estructura común para la generación de informes con pasos personalizables.
* **Observer**: Notificaciones durante el proceso de análisis y limpieza.
* **Singleton**: Utilizado para garantizar que solo existe una instancia de ciertas clases, como el gestor de mensajes.
* **Facade**: La clase `Main` proporciona una interfaz simplificada al subsistema complejo de gestión de metadatos.

## Principios de Diseño Adicionales

* **Principio de Responsabilidad Única (SRP)**: Cada clase tiene una única razón para cambiar.
* **Principio Abierto/Cerrado (OCP)**: El sistema está abierto a extensiones pero cerrado a modificaciones.
* **Inyección de Dependencias**: Reducción del acoplamiento mediante paso de dependencias.
* **Programación por Contrato**: Precondiciones y postcondiciones definidas para operaciones clave.

---

La aplicación de estos principios y patrones ha permitido crear una herramienta robusta, extensible y mantenible que cumple con los estándares de la ingeniería de software moderna. Este enfoque facilita la comprensión del código, la corrección de errores y la incorporación de nuevas funcionalidades. 