# Índice de la Documentación Técnica

## Introducción
Este documento sirve como guía para navegar a través de la documentación técnica de la aplicación MetaInfo, una herramienta desarrollada para la gestión de metadatos en archivos. La documentación sigue los principios del Proceso Unificado (UP), incorporando patrones GRASP (General Responsibility Assignment Software Patterns) y patrones de diseño GoF (Gang of Four).

## Metodología de Desarrollo
La aplicación MetaInfo ha sido desarrollada siguiendo un enfoque iterativo e incremental basado en el Proceso Unificado, poniendo énfasis en:

- **Arquitectura centrada en casos de uso**: La funcionalidad del sistema ha sido diseñada a partir de los casos de uso identificados durante el análisis de requisitos.
- **Desarrollo dirigido por riesgos**: Las partes más críticas del sistema fueron abordadas primero para mitigar riesgos técnicos.
- **Verificación continua de la calidad**: Mediante pruebas unitarias y de integración en cada fase del desarrollo.

## Patrones de Diseño Aplicados
La aplicación implementa varios patrones de diseño que mejoran su mantenibilidad y escalabilidad:

### Patrones GRASP
- **Experto en Información**: Las clases como `Main`, `Reporter` y `Cleaner` encapsulan la información necesaria para realizar sus responsabilidades.
- **Creador**: Se asigna la responsabilidad de crear objetos a las clases que tienen la información necesaria para inicializarlos correctamente.
- **Alta Cohesión y Bajo Acoplamiento**: Las clases están diseñadas para tener un propósito único y bien definido, con dependencias mínimas entre ellas.
- **Controlador**: La clase `MetaInfo` actúa como un controlador central que coordina las operaciones del sistema.

### Patrones GoF
- **Singleton**: Utilizado para garantizar que solo existe una instancia de ciertas clases, como el gestor de mensajes (`Messages`).
- **Facade**: La clase `Main` proporciona una interfaz simplificada al subsistema complejo de gestión de metadatos.
- **Strategy**: Permite seleccionar diferentes algoritmos para la limpieza de metadatos (completa o selectiva) en tiempo de ejecución.

## Estructura de la Documentación

1. [**Arquitectura Modular**](arquitectura_modular.md)
   - Descripción de los módulos principales y sus interacciones
   - Principios de diseño aplicados

2. [**Diagrama de Clases**](diagrama_clases.md)
   - Estructura estática del sistema
   - Relaciones entre las clases principales

3. [**Diagramas de Interacción**](diagramas_interaccion.md)
   - Secuencias de interacción entre objetos
   - Colaboraciones para casos de uso clave

4. [**Casos de Uso**](casos_uso.md)
   - Descripción detallada de los casos de uso
   - Flujos principales y alternativos

5. [**Diagrama de Flujo de Datos**](diagrama_flujo_datos.md)
   - Representación del flujo de información en el sistema
   - Transformaciones de datos entre componentes

6. [**Arquitectura por Capas**](arquitectura_capas.md)
   - Organización del sistema en capas lógicas
   - Mecanismos de comunicación entre capas

7. [**Modelo de Dominio**](modelo_dominio.md)
   - Conceptos clave del dominio y sus relaciones
   - Reglas de negocio implementadas

## Aspectos Funcionales Destacados

### Gestión de Metadatos
La aplicación permite la detección, análisis y manipulación de metadatos en diversos tipos de archivos, centrándose en:

- **Detección de información sensible**: Identificación de patrones sensibles en los metadatos mediante expresiones regulares y análisis heurístico.
- **Limpieza selectiva**: Capacidad para eliminar solo los metadatos que contienen información sensible.
- **Generación de informes**: Creación de reportes detallados en formatos Markdown, HTML y PDF.

### Extensibilidad
El diseño modular facilita la incorporación de:

- Nuevos formatos de archivo
- Patrones adicionales para la detección de información sensible
- Formatos de informe personalizados

## Guía de Estudio Recomendada

Para comprender eficientemente la arquitectura y funcionamiento de MetaInfo, se recomienda seguir este orden de lectura:

1. Casos de Uso: Para entender qué hace el sistema
2. Arquitectura Modular: Para obtener una visión general de los componentes
3. Modelo de Dominio: Para familiarizarse con los conceptos clave
4. Diagrama de Clases: Para conocer la estructura estática
5. Diagramas de Interacción: Para entender el comportamiento dinámico
6. Arquitectura por Capas: Para profundizar en los aspectos de implementación
7. Diagrama de Flujo de Datos: Para analizar la transformación de la información

## Consideraciones para el Desarrollo Futuro

La documentación también incluye directrices para futuras mejoras, centradas en:

- Ampliación de los formatos de archivo soportados
- Mejora de los algoritmos de detección de información sensible
- Optimización del rendimiento para grandes volúmenes de archivos
- Integración con sistemas de gestión documental 