<svg xmlns="http://www.w3.org/2000/svg" width="300" height="120" viewBox="0 0 300 120">
  <style>
    .title { fill: #2c3e50; font-family: 'Arial', sans-serif; font-size: 36px; font-weight: bold; }
    .subtitle { fill: #34495e; font-family: 'Arial', sans-serif; font-size: 16px; }
    .icon-bg { fill: #3498db; }
    .icon-fg { fill: white; }
    .icon-highlight { fill: #2ecc71; }
  </style>
  <circle cx="60" cy="60" r="50" class="icon-bg" />
  <g transform="translate(35, 35)">
    <rect x="0" y="0" width="50" height="10" rx="2" class="icon-fg" />
    <rect x="0" y="15" width="40" height="10" rx="2" class="icon-fg" />
    <rect x="0" y="30" width="30" height="10" rx="2" class="icon-fg" />
    <rect x="0" y="45" width="20" height="10" rx="2" class="icon-highlight" />
  </g>
  <text x="120" y="55" class="title">MetaInfo</text>
  <text x="120" y="80" class="subtitle">Análisis y gestión de metadatos</text>
</svg>

# MetaInfo - Documentación del Sistema

## Descripción General

MetaInfo es una aplicación especializada en el análisis y gestión de metadatos en archivos digitales. Permite detectar información sensible, generar informes detallados y limpiar metadatos para proteger la privacidad.

## Navegación Rápida

| Documentación Principal | Diagramas | Técnica |
|------------------------|-----------|---------|
| [📋 Índice Principal](indice.md) | [🔍 Diagrama de Componentes](diagrama_componentes.md) | [📘 Actualizaciones Recientes](#actualizaciones-recientes) |
| [📚 Casos de Uso](casos_uso.md) | [📊 Diagrama de Clases](diagrama_clases.md) | [🔧 Instalación y Dependencias](#instalación-y-dependencias) |
| [📐 Modelo de Dominio](modelo_dominio.md) | [📈 Diagramas de Interacción](diagramas_interaccion.md) | [📝 Ejemplos de Uso](#ejemplos-de-uso) |

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

La documentación sigue un enfoque progresivo, desde aspectos conceptuales hasta detalles de implementación:

1. **[Índice](indice.md)** - Punto de entrada principal a toda la documentación
2. **[Casos de Uso](casos_uso.md)** - Escenarios de interacción usuario-sistema
3. **[Diagrama de Componentes](diagrama_componentes.md)** - Estructura de alto nivel
4. **[Diagrama de Clases](diagrama_clases.md)** - Detalles de implementación

Para más información, consulte el [Índice Principal](indice.md).

---

*Última actualización: 11/06/2024* 