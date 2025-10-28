#!/usr/bin/env python3
"""
Test script para verificar que el cache de estadísticas funcione desde Spaces
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_stats_cache():
    """Prueba el cache de estadísticas"""
    
    print("🧪 Probando cache de estadísticas desde Spaces")
    print("=" * 50)
    
    try:
        from services.stats_cache import get_stats_cache
        
        # Crear instancia del cache
        stats_cache = get_stats_cache()
        
        # Limpiar cache local si existe
        cache_file = Path('backend/cache/relationship_stats.json')
        if cache_file.exists():
            cache_file.unlink()
            print("🗑️ Cache local limpiado para prueba")
        
        # Intentar obtener estadísticas (debería descargar desde Spaces)
        print("\n📥 Obteniendo estadísticas...")
        stats = stats_cache.get_cached_stats()
        
        if stats:
            print("✅ Estadísticas obtenidas exitosamente!")
            print(f"   📊 Total mensajes: {stats.get('totalMessages', 0):,}")
            print(f"   📅 Días analizados: {stats.get('totalDays', 0)}")
            print(f"   💕 Score sentiment: {stats.get('sentimentScore', 0)}")
            print(f"   📈 Promedio diario: {stats.get('avgMessagesPerDay', 0)}")
            print(f"   🎯 Fuente: {stats.get('data_source', 'unknown')}")
            
            # Verificar que se guardó el cache local
            if cache_file.exists():
                print(f"   💾 Cache local creado: {cache_file.stat().st_size / 1024:.1f} KB")
            
            return True
        else:
            print("❌ No se pudieron obtener estadísticas")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_info():
    """Prueba la información del cache"""
    
    print("\n📋 Información del cache:")
    print("-" * 30)
    
    try:
        from services.stats_cache import get_stats_cache
        stats_cache = get_stats_cache()
        
        cache_info = stats_cache.get_cache_info()
        
        print(f"✅ Cache existe: {cache_info.get('exists', False)}")
        print(f"📏 Tamaño: {cache_info.get('size_mb', 0)} MB")
        print(f"⏰ Edad: {cache_info.get('age_hours', 0):.1f} horas")
        print(f"✅ Válido: {cache_info.get('valid', False)}")
        
        if 'total_messages' in cache_info:
            print(f"📊 Mensajes: {cache_info['total_messages']:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error obteniendo info: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test Suite - Cache de Estadísticas")
    print("=" * 60)
    
    # Test 1: Funcionamiento básico
    test1_ok = test_stats_cache()
    
    # Test 2: Información del cache
    test2_ok = test_cache_info()
    
    print("\n" + "=" * 60)
    if test1_ok and test2_ok:
        print("🎉 ¡Todos los tests pasaron!")
        print("✅ El cache de estadísticas está funcionando correctamente")
        print("⚡ El dashboard ahora cargará súper rápido desde Spaces")
    else:
        print("❌ Algunos tests fallaron")
        print("🔧 Revisa la configuración de Spaces y las URLs")
    
    print("=" * 60)