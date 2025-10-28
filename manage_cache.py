#!/usr/bin/env python3
"""
Cache Management Tool for Romantic AI Proposal System
Herramienta para gestionar el cache de embeddings y chunks
"""

import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def get_cache_info():
    """Obtiene información del cache actual."""
    cache_dir = Path('backend/cache')
    
    if not cache_dir.exists():
        print("❌ No se encontró directorio de cache")
        return
    
    print("📂 Información del Cache")
    print("=" * 50)
    
    # Archivos de cache
    embeddings_file = cache_dir / 'rag_embeddings.pkl'
    index_file = cache_dir / 'faiss_index.bin'
    
    if embeddings_file.exists():
        size_mb = embeddings_file.stat().st_size / 1024 / 1024
        modified = datetime.fromtimestamp(embeddings_file.stat().st_mtime)
        print(f"📄 rag_embeddings.pkl: {size_mb:.1f} MB (modificado: {modified.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # Cargar y mostrar estadísticas
        try:
            with open(embeddings_file, 'rb') as f:
                data = pickle.load(f)
                if 'metadata' in data:
                    print(f"   • Chunks almacenados: {len(data['metadata']):,}")
                    print(f"   • Creado: {data.get('created_at', 'Desconocido')}")
                    if data['metadata']:
                        first_chunk = data['metadata'][0]
                        print(f"   • Mensajes por chunk: ~{len(first_chunk.get('messages_in_chunk', []))}")
                        print(f"   • Rango temporal: {first_chunk.get('start_date', 'N/A')} - {first_chunk.get('end_date', 'N/A')}")
                else:
                    # Formato antiguo
                    print(f"   • Datos: {list(data.keys())}")
        except Exception as e:
            print(f"   ⚠️  Error leyendo archivo: {e}")
    else:
        print("❌ rag_embeddings.pkl no encontrado")
    
    if index_file.exists():
        size_mb = index_file.stat().st_size / 1024 / 1024
        modified = datetime.fromtimestamp(index_file.stat().st_mtime)
        print(f"📄 faiss_index.bin: {size_mb:.1f} MB (modificado: {modified.strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        print("❌ faiss_index.bin no encontrado")
    
    # Espacio total
    total_size = 0
    for file in cache_dir.glob('*'):
        if file.is_file():
            total_size += file.stat().st_size
    
    print(f"\n💾 Espacio total del cache: {total_size / 1024 / 1024:.1f} MB")

def clear_cache():
    """Limpia el cache completamente."""
    cache_dir = Path('backend/cache')
    
    if not cache_dir.exists():
        print("❌ No se encontró directorio de cache")
        return
    
    print("🗑️  Limpiando cache...")
    
    files_removed = 0
    for file in cache_dir.glob('*'):
        if file.is_file():
            try:
                file.unlink()
                print(f"   ✅ Eliminado: {file.name}")
                files_removed += 1
            except Exception as e:
                print(f"   ❌ Error eliminando {file.name}: {e}")
    
    if files_removed > 0:
        print(f"\n✅ Cache limpiado ({files_removed} archivos eliminados)")
        print("💡 El cache se regenerará automáticamente en el próximo inicio")
    else:
        print("ℹ️  No había archivos para eliminar")

def backup_cache():
    """Hace backup del cache."""
    cache_dir = Path('backend/cache')
    backup_dir = Path('cache_backup')
    
    if not cache_dir.exists():
        print("❌ No se encontró directorio de cache")
        return
    
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_subdir = backup_dir / f"cache_backup_{timestamp}"
    backup_subdir.mkdir(exist_ok=True)
    
    print(f"💾 Creando backup en: {backup_subdir}")
    
    files_backed_up = 0
    for file in cache_dir.glob('*'):
        if file.is_file():
            try:
                import shutil
                shutil.copy2(file, backup_subdir / file.name)
                print(f"   ✅ Backup: {file.name}")
                files_backed_up += 1
            except Exception as e:
                print(f"   ❌ Error con {file.name}: {e}")
    
    print(f"\n✅ Backup completado ({files_backed_up} archivos)")

def main():
    if len(sys.argv) < 2:
        print("🔧 Cache Management Tool")
        print("=" * 30)
        print("Uso: python manage_cache.py [comando]")
        print("")
        print("Comandos disponibles:")
        print("  info     - Mostrar información del cache")
        print("  clear    - Limpiar cache completo")
        print("  backup   - Hacer backup del cache")
        print("")
        print("Ejemplos:")
        print("  python manage_cache.py info")
        print("  python manage_cache.py clear")
        print("  python manage_cache.py backup")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'info':
        get_cache_info()
    elif command == 'clear':
        print("⚠️  ¿Estás seguro de que quieres limpiar el cache?")
        print("   Esto eliminará todos los embeddings y se tendrán que regenerar.")
        confirm = input("   Escribe 'yes' para confirmar: ")
        if confirm.lower() == 'yes':
            clear_cache()
        else:
            print("❌ Operación cancelada")
    elif command == 'backup':
        backup_cache()
    else:
        print(f"❌ Comando desconocido: {command}")
        print("Comandos disponibles: info, clear, backup")

if __name__ == '__main__':
    main()