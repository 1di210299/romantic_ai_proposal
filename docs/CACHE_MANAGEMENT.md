# 📂 Cache Management - Romantic AI Proposal

Este documento explica cómo se almacenan y gestionan los embeddings y chunks del sistema RAG.

## 📍 Ubicación de los Archivos

Los datos de cache se almacenan en **`backend/cache/`**:

```
backend/cache/
├── rag_embeddings.pkl    # Chunks y metadatos (5.5 MB)
└── faiss_index.bin       # Índice vectorial FAISS (39 MB)
```

## 📄 Descripción de Archivos

### `rag_embeddings.pkl`
- **Contenido**: Chunks de mensajes procesados y sus metadatos
- **Formato**: Python pickle serializado
- **Incluye**:
  - Chunks de 5 mensajes consecutivos cada uno
  - Metadatos (fechas, autores, contexto)
  - Información de creación del cache
- **Tamaño actual**: ~5.5 MB
- **Chunks almacenados**: 6,725

### `faiss_index.bin`
- **Contenido**: Índice vectorial optimizado para búsqueda semántica
- **Formato**: FAISS binary format
- **Propósito**: Búsqueda rápida de vectores similares
- **Tamaño actual**: ~39 MB
- **Vectores**: 6,725 (uno por chunk)

## 🔧 Gestión del Cache

### Ver información del cache
```bash
python manage_cache.py info
```

### Limpiar cache (forzar regeneración)
```bash
python manage_cache.py clear
```

### Hacer backup del cache
```bash
python manage_cache.py backup
```

## 🔄 Regeneración Automática

El cache se regenera automáticamente cuando:
- Los archivos de cache no existen
- Se detectan cambios en los datos fuente
- Se fuerza la regeneración con `force_rebuild=True`

## 💾 Espacio en Disco

- **Total actual**: ~45 MB
- **Crecimiento**: Proporcional al número de mensajes procesados
- **Optimización**: El sistema usa chunks para reducir redundancia

## 🚀 Optimización del Rendimiento

### Primera ejecución (sin cache)
- Procesa todos los mensajes (~30-60 segundos)
- Genera embeddings via OpenAI API
- Crea índice FAISS
- Guarda cache para futuros usos

### Ejecuciones posteriores (con cache)
- Carga cache existente (~2-5 segundos)
- No requiere llamadas a OpenAI API
- Búsquedas instantáneas

## 🔍 Estructura del Cache

```python
# rag_embeddings.pkl contiene:
{
    'metadata': [
        {
            'chunk_id': str,
            'messages_in_chunk': List[Dict],
            'combined_text': str,
            'start_date': str,  
            'end_date': str,
            'authors': List[str],
            'message_count': int
        },
        # ... más chunks
    ],
    'created_at': str  # ISO timestamp
}
```

## 🐳 Docker Considerations

En deployment con Docker:
- El cache se monta como volumen persistente
- Se preserva entre reinicios del contenedor
- Configurado en `docker-compose.yml`:
  ```yaml
  volumes:
    - ./backend/cache:/app/cache
  ```

## 🔐 Seguridad

- Los archivos de cache **NO** contienen credenciales
- Solo metadatos y vectores numéricos
- Los mensajes originales se almacenan localmente
- No se envía información personal a servicios externos

## 📊 Monitoreo

Para monitorear el cache:
```bash
# Tamaño de archivos
ls -lh backend/cache/

# Información detallada
python manage_cache.py info

# Estadísticas en tiempo real
tail -f logs/app.log | grep "RAG"
```