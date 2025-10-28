#!/bin/bash

# warm_cache.sh - Script para pre-calentar el cache del sistema

echo "🔥 Warming up Romantic AI Cache..."
echo "=================================="

# Cambiar al directorio del backend
cd backend/

echo ""
echo "📊 1. Pre-generando estadísticas..."
python -c "
import sys
import os
sys.path.append('.')
sys.path.append('..')

try:
    from app import analyze_conversation_data
    from services.stats_cache import get_stats_cache
    
    print('🔄 Calculando estadísticas...')
    stats = analyze_conversation_data()
    
    if stats:
        stats_cache = get_stats_cache()
        stats_cache.save_stats_to_cache(stats)
        print(f'✅ Estadísticas cacheadas: {stats.get(\"totalMessages\", 0):,} mensajes')
    else:
        print('⚠️ No se pudieron generar estadísticas')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "📦 2. Verificando cache RAG..."
if [ -f "cache/rag_embeddings.pkl" ] && [ -f "cache/faiss_index.bin" ]; then
    echo "✅ Cache RAG disponible"
else
    echo "⚠️ Cache RAG no encontrado - se generará en el primer uso"
fi

echo ""
echo "📈 3. Información del cache:"
cd ..
python manage_cache.py info

echo ""
echo "🚀 Cache warming completado!"
echo "El dashboard ahora debería cargar más rápido"