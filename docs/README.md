# MetaInfo

## Descripción General

MetaInfo es una aplicación especializada en el análisis y gestión de metadatos en archivos digitales. Permite detectar información sensible, generar informes detallados y limpiar metadatos para proteger la privacidad.

## Navegación Rápida

| Documentación Principal | Diagramas | Técnica |
|------------------------|-----------|---------|
| [📋 Índice Principal](indice.md) | [🔍 Diagrama de Clases](diagrama_clases.md) | [📘 Actualizaciones Recientes](#actualizaciones-recientes) |
| [📚 Casos de Uso](casos_uso.md) | [📊 Ejemplos de Uso](#ejemplos-de-uso) | [🔧 Instalación y Dependencias](#instalación-y-dependencias) |

## Actualizaciones Recientes

### Mejoras en Limpieza de Metadatos

- Exclusión automática de archivos `.txt` durante el proceso de limpieza
- Método de limpieza mejorado con múltiples estrategias y verificación
- Manejo de errores robusto con recuperación automática

### Mejoras en Generación de Informes

- Rutas relativas en informes para mejor portabilidad y privacidad
- Mejor identificación y presentación de patrones sensibles

### Mejoras en Pruebas

- Pruebas unitarias más claras y enfocadas
- Pruebas de integración más robustas y confiables

## Instalación y Dependencias

Para utilizar MetaInfo, necesitas:

```bash
# Instalación básica
pip install -r requirements.txt

# Dependencias opcionales para generación de PDF
apt-get install pandoc texlive-xetex
```

**Dependencias principales:**
- Python 3.7+
- ExifTool
- Pandoc (opcional, para PDF)

## Ejemplos de Uso

### Analizar metadatos y generar informe completo

```bash
python metainfo.py --i ~/Documentos --report_all --o ~/Informes --pdf
```

### Limpiar metadatos sensibles

```bash
python metainfo.py --i ~/Fotos/Privadas --wipe_sensitive --verbose
```

### Eliminar todos los metadatos

```bash
python metainfo.py --i ~/Documentos/ParaPublicar --wipe_all
```

## Estructura de la Documentación

La documentación sigue un enfoque progresivo y simplificado:

1. **[Índice](indice.md)** - Punto de entrada principal a toda la documentación
2. **[Casos de Uso](casos_uso.md)** - Escenarios de interacción usuario-sistema
3. **[Diagrama de Clases](diagrama_clases.md)** - Estructura principal del sistema

Para más información, consulte el [Índice Principal](indice.md).

---

*Última actualización: 11/06/2024* 