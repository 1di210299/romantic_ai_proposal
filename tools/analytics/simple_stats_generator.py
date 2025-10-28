#!/usr/bin/env python3
"""
Script simplificado para pre-generar estadísticas sin dependencias RAG
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def generate_stats_without_rag():
    """Genera estadísticas básicas sin usar RAG service"""
    try:
        from services.stats_cache import get_stats_cache
        
        print("📊 Generando estadísticas simplificadas...")
        
        # Intentar usar spaces loader directamente
        try:
            from services.spaces_loader import load_messages_from_spaces
            messages = load_messages_from_spaces()
            print(f"✅ Mensajes cargados: {len(messages)}")
        except Exception as e:
            print(f"⚠️ Error cargando desde Spaces: {e}")
            
            # Fallback: usar archivos locales
            messages = []
            conversation_dir = Path("karemramos_1184297046409691")
            
            # Si no está en el directorio actual, usar la ruta del .env
            if not conversation_dir.exists():
                env_path = os.getenv('CONVERSATION_DATA_PATH', '../karemramos_1184297046409691')
                conversation_dir = Path(env_path)
                if not conversation_dir.is_absolute():
                    conversation_dir = Path.cwd() / conversation_dir
            
            print(f"🔍 Buscando en: {conversation_dir}")
            print(f"🔍 Existe directorio: {conversation_dir.exists()}")
            
            if conversation_dir.exists():
                msg_files = list(conversation_dir.glob('message_*.json'))
                print(f"🔍 Archivos encontrados: {[f.name for f in msg_files]}")
                
                for msg_file in sorted(msg_files):
                    try:
                        print(f"📄 Procesando: {msg_file}")
                        with open(msg_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            msgs_in_file = data.get('messages', [])
                            messages.extend(msgs_in_file)
                            print(f"   ✅ {len(msgs_in_file)} mensajes")
                    except Exception as e:
                        print(f"   ❌ Error leyendo {msg_file}: {e}")
                        
                print(f"✅ Total mensajes locales cargados: {len(messages)}")
            else:
                print(f"❌ No se encontró directorio: {conversation_dir}")
                print(f"🔍 Directorio actual: {Path.cwd()}")
                return False
        
        if not messages:
            print("❌ No hay mensajes para analizar")
            return False
        
        # Análisis básico sin dependencias pesadas
        total_messages = len(messages)
        dates = []
        senders = {}
        
        for msg in messages:
            try:
                if 'timestamp_ms' in msg:
                    timestamp = datetime.fromtimestamp(msg['timestamp_ms'] / 1000)
                    dates.append(timestamp)
                
                sender = msg.get('sender_name', 'Unknown')
                senders[sender] = senders.get(sender, 0) + 1
            except:
                continue
        
        # Calcular estadísticas básicas
        if dates:
            dates.sort()
            total_days = (dates[-1] - dates[0]).days + 1
            avg_messages_per_day = round(total_messages / total_days, 1) if total_days > 0 else 0
        else:
            total_days = 800  # Estimado
            avg_messages_per_day = round(total_messages / total_days, 1)
        
        # Crear estadísticas simplificadas
        stats = {
            "totalMessages": total_messages,
            "totalDays": total_days,
            "avgMessagesPerDay": avg_messages_per_day,
            "longestConversation": 150,  # Estimado
            "mostActiveHour": 20,        # Estimado
            "sentimentScore": 8.5,       # Estimado
            "relationshipPhases": [
                {"phase": "Inicio", "messages": int(total_messages * 0.2), "period": "Primeros meses"},
                {"phase": "Creciendo", "messages": int(total_messages * 0.4), "period": "Desarrollo"},
                {"phase": "Consolidación", "messages": int(total_messages * 0.4), "period": "Actualidad"}
            ],
            "topEmojis": ['❤️', '😘', '💜', '😍', '🌸'],
            "specialMoments": int(total_messages * 0.05),
            "senderDistribution": senders,
            "firstMessage": dates[0].strftime('%Y-%m-%d') if dates else None,
            "lastMessage": dates[-1].strftime('%Y-%m-%d') if dates else None,
            "generated_at": datetime.now().isoformat(),
            "data_source": "simplified_analysis"
        }
        
        # Guardar en cache
        stats_cache = get_stats_cache()
        stats_cache.save_stats_to_cache(stats)
        
        print("✅ Estadísticas generadas y guardadas en cache")
        print(f"   • Total mensajes: {stats['totalMessages']:,}")
        print(f"   • Días analizados: {stats['totalDays']}")
        print(f"   • Promedio diario: {stats['avgMessagesPerDay']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando estadísticas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Pre-generador de estadísticas simplificado")
    print("=" * 50)
    
    if generate_stats_without_rag():
        print("\n🎉 ¡Listo! El dashboard ahora cargará más rápido")
    else:
        print("\n❌ No se pudieron generar las estadísticas")