"""
Statistics Cache Service
Cache de estadísticas pre-calculadas para acelerar la carga del dashboard
Con soporte para descarga desde DigitalOcean Spaces
"""

import os
import json
import pickle
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

class StatsCache:
    """
    Sistema de cache para estadísticas de conversación.
    Guarda análisis pre-calculados para evitar reprocesar datos cada vez.
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.stats_cache_file = self.cache_dir / "relationship_stats.json"
        self.cache_duration_hours = 24  # Cache válido por 24 horas
        self.spaces_url = os.getenv('SPACES_DATA_URL', 'https://romantic-ai-data.sfo3.digitaloceanspaces.com')
        
    def get_cached_stats(self) -> Optional[Dict]:
        """
        Obtiene estadísticas desde cache. Primero intenta local, luego descarga desde Spaces.
        
        Returns:
            Dict con estadísticas o None si no hay cache válido
        """
        try:
            # 1. Intentar cache local primero
            if self.stats_cache_file.exists():
                with open(self.stats_cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Verificar si el cache ha expirado
                cache_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
                current_time = datetime.now()
                age_hours = (current_time - cache_time).total_seconds() / 3600
                
                if age_hours <= self.cache_duration_hours:
                    print(f"✅ Cache local válido ({age_hours:.1f}h de antigüedad)")
                    return cached_data.get('stats')
                else:
                    print(f"📊 Cache local expirado ({age_hours:.1f}h)")
            
            # 2. Si no hay cache local válido, descargar desde Spaces
            print("🌐 Descargando cache de estadísticas desde Spaces...")
            return self._download_stats_from_spaces()
            
        except Exception as e:
            print(f"❌ Error obteniendo cache de estadísticas: {e}")
            return None
    
    def _download_stats_from_spaces(self) -> Optional[Dict]:
        """Descarga cache de estadísticas desde DigitalOcean Spaces"""
        try:
            stats_url = f"{self.spaces_url}/relationship_stats.json"
            print(f"📥 Descargando desde: {stats_url}")
            
            response = requests.get(stats_url, timeout=30)
            response.raise_for_status()
            
            # Parsear contenido
            cached_data = response.json()
            
            # Guardar en cache local para próximas consultas
            with open(self.stats_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
            
            # Verificar validez del cache descargado
            cache_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600
            
            print(f"✅ Cache descargado desde Spaces ({age_hours:.1f}h de antigüedad)")
            print(f"💾 Guardado localmente: {self.stats_cache_file}")
            
            return cached_data.get('stats')
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error descargando desde Spaces: {e}")
            return None
        except Exception as e:
            print(f"❌ Error procesando cache de Spaces: {e}")
            return None
    
    def save_stats_to_cache(self, stats: Dict):
        """
        Guarda estadísticas en cache con timestamp.
        
        Args:
            stats: Diccionario con las estadísticas calculadas
        """
        try:
            cache_data = {
                'stats': stats,
                'cached_at': datetime.now().isoformat(),
                'cache_version': '1.0'
            }
            
            with open(self.stats_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Estadísticas guardadas en cache: {self.stats_cache_file}")
            
        except Exception as e:
            print(f"❌ Error guardando cache de estadísticas: {e}")
    
    def clear_cache(self):
        """Limpia el cache de estadísticas."""
        try:
            if self.stats_cache_file.exists():
                self.stats_cache_file.unlink()
                print("🗑️ Cache de estadísticas limpiado")
            else:
                print("📊 No hay cache para limpiar")
        except Exception as e:
            print(f"❌ Error limpiando cache: {e}")
    
    def get_cache_info(self) -> Dict:
        """Obtiene información del estado del cache."""
        if not self.stats_cache_file.exists():
            return {
                'exists': False,
                'size_mb': 0,
                'age_hours': 0,
                'valid': False
            }
        
        try:
            stat = self.stats_cache_file.stat()
            size_mb = stat.st_size / 1024 / 1024
            
            with open(self.stats_cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600
            valid = age_hours <= self.cache_duration_hours
            
            return {
                'exists': True,
                'size_mb': round(size_mb, 2),
                'age_hours': round(age_hours, 1),
                'valid': valid,
                'cached_at': cached_data.get('cached_at'),
                'total_messages': cached_data.get('stats', {}).get('totalMessages', 0)
            }
            
        except Exception as e:
            return {
                'exists': True,
                'error': str(e),
                'valid': False
            }


# Instancia global del cache
_stats_cache_instance: Optional[StatsCache] = None

def get_stats_cache() -> StatsCache:
    """Obtiene la instancia singleton del cache de estadísticas."""
    global _stats_cache_instance
    if _stats_cache_instance is None:
        _stats_cache_instance = StatsCache()
    return _stats_cache_instance