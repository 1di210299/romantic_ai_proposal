#!/usr/bin/env python3
"""
Script para generar estadísticas REALES desde los archivos JSON
y crear cache para DigitalOcean Spaces
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

def load_messages_from_json_files():
    """Carga todos los mensajes desde los archivos JSON locales"""
    
    messages = []
    conversation_dir = Path("karemramos_1184297046409691")
    
    print(f"📂 Cargando mensajes desde: {conversation_dir}")
    
    if not conversation_dir.exists():
        print(f"❌ Directorio no encontrado: {conversation_dir}")
        return []
    
    # Cargar todos los archivos JSON
    for msg_file in sorted(conversation_dir.glob('message_*.json')):
        try:
            print(f"📄 Procesando: {msg_file.name}")
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_messages = data.get('messages', [])
                messages.extend(file_messages)
                print(f"   ✅ {len(file_messages):,} mensajes cargados")
                
        except Exception as e:
            print(f"   ❌ Error leyendo {msg_file}: {e}")
    
    print(f"📊 Total mensajes cargados: {len(messages):,}")
    return messages

def analyze_real_messages(messages):
    """Analiza los mensajes reales y extrae estadísticas"""
    
    if not messages:
        print("❌ No hay mensajes para analizar")
        return None
    
    print("🔍 Analizando mensajes reales...")
    
    # Contadores y análisis
    total_messages = len(messages)
    dates = []
    message_times = []
    senders = {}
    content_analysis = {
        'total_chars': 0,
        'romantic_keywords': 0,
        'emojis': Counter(),
        'longest_message': 0,
        'conversations_by_month': Counter(),
        'words_total': 0
    }
    
    # Palabras románticas en español
    romantic_words = [
        'amor', 'te amo', 'mi vida', 'corazón', 'besitos', 'hermosa', 
        'princesa', 'mi amor', 'baby', 'cariño', 'te quiero', 'bebe',
        'cielo', 'preciosa', 'bonita', 'linda', 'guapa', 'eres todo',
        'mi mundo', 'mi cielo', 'te extraño', 'te necesito', 'siempre juntos'
    ]
    
    # Patrón para emojis
    emoji_pattern = re.compile("["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    print("📈 Procesando cada mensaje...")
    
    for i, msg in enumerate(messages):
        try:
            # Progreso cada 5000 mensajes
            if i % 5000 == 0 and i > 0:
                print(f"   📊 Procesados {i:,}/{total_messages:,} mensajes...")
            
            # Análisis de fecha y hora
            if 'timestamp_ms' in msg:
                timestamp = datetime.fromtimestamp(msg['timestamp_ms'] / 1000)
                dates.append(timestamp)
                message_times.append(timestamp.hour)
                month_key = timestamp.strftime('%Y-%m')
                content_analysis['conversations_by_month'][month_key] += 1
            
            # Análisis de remitente
            sender = msg.get('sender_name', 'Unknown')
            senders[sender] = senders.get(sender, 0) + 1
            
            # Análisis de contenido
            content = msg.get('content', '')
            if content:
                content_analysis['total_chars'] += len(content)
                content_analysis['longest_message'] = max(
                    content_analysis['longest_message'], 
                    len(content)
                )
                
                # Contar palabras
                words = len(content.split())
                content_analysis['words_total'] += words
                
                # Buscar palabras románticas
                content_lower = content.lower()
                for word in romantic_words:
                    if word in content_lower:
                        content_analysis['romantic_keywords'] += 1
                
                # Contar emojis
                emojis_found = emoji_pattern.findall(content)
                for emoji in emojis_found:
                    content_analysis['emojis'][emoji] += 1
                    
        except Exception as e:
            continue
    
    print("✅ Análisis de mensajes completo")
    
    # Calcular estadísticas finales
    if dates:
        dates.sort()
        first_date = dates[0]
        last_date = dates[-1]
        total_days = (last_date - first_date).days + 1
        avg_messages_per_day = round(total_messages / total_days, 1) if total_days > 0 else 0
        
        # Hora más activa
        most_active_hour = Counter(message_times).most_common(1)[0][0] if message_times else 12
        
        # Score de sentimiento basado en palabras románticas
        romantic_ratio = content_analysis['romantic_keywords'] / total_messages
        sentiment_score = min(10, round(romantic_ratio * 100 + 6, 1))  # Base 6 + boost por romance
        
        # Top 5 emojis
        top_emojis = [emoji for emoji, count in content_analysis['emojis'].most_common(5)]
        if not top_emojis:
            top_emojis = ['❤️', '😘', '💜', '😍', '🥰']  # Fallback
        
        # Fases de la relación basadas en datos por mes
        monthly_data = sorted(content_analysis['conversations_by_month'].items())
        phases = []
        
        if len(monthly_data) >= 3:
            # Dividir en 3 fases temporales
            third = len(monthly_data) // 3
            
            phase1_msgs = sum(count for _, count in monthly_data[:third])
            phase2_msgs = sum(count for _, count in monthly_data[third:third*2])
            phase3_msgs = sum(count for _, count in monthly_data[third*2:])
            
            phases = [
                {
                    "phase": "Inicio",
                    "messages": phase1_msgs,
                    "period": f"{monthly_data[0][0]} - {monthly_data[third-1][0]}"
                },
                {
                    "phase": "Creciendo", 
                    "messages": phase2_msgs,
                    "period": f"{monthly_data[third][0]} - {monthly_data[third*2-1][0]}"
                },
                {
                    "phase": "Consolidación",
                    "messages": phase3_msgs,
                    "period": f"{monthly_data[third*2][0]} - {monthly_data[-1][0]}"
                }
            ]
        
        # Crear estadísticas finales
        stats = {
            "totalMessages": total_messages,
            "totalDays": total_days,
            "avgMessagesPerDay": avg_messages_per_day,
            "longestConversation": content_analysis['longest_message'],
            "mostActiveHour": most_active_hour,
            "sentimentScore": sentiment_score,
            "relationshipPhases": phases,
            "topEmojis": top_emojis,
            "specialMoments": content_analysis['romantic_keywords'],
            "senderDistribution": senders,
            "totalChars": content_analysis['total_chars'],
            "totalWords": content_analysis['words_total'],
            "firstMessage": first_date.strftime('%Y-%m-%d'),
            "lastMessage": last_date.strftime('%Y-%m-%d'),
            "generated_at": datetime.now().isoformat(),
            "data_source": "real_json_analysis"
        }
        
        return stats
    
    return None

def create_cache_file(stats):
    """Crea el archivo de cache con las estadísticas"""
    
    if not stats:
        print("❌ No hay estadísticas para guardar")
        return None
    
    # Estructura del cache
    cache_data = {
        'stats': stats,
        'cached_at': datetime.now().isoformat(),
        'cache_version': '1.0'
    }
    
    # Crear directorio y archivo
    cache_dir = Path('backend/cache')
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / 'relationship_stats.json'
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Cache creado: {cache_file}")
    print(f"   📊 {stats['totalMessages']:,} mensajes analizados")
    print(f"   📅 {stats['totalDays']} días de conversación")
    print(f"   💝 {stats['specialMoments']} momentos románticos")
    print(f"   📝 {stats['totalWords']:,} palabras totales")
    print(f"   💾 Tamaño: {cache_file.stat().st_size / 1024:.1f} KB")
    
    return cache_file

def main():
    print("🏗️  Generador de Cache de Estadísticas REALES")
    print("=" * 60)
    
    # 1. Cargar mensajes desde JSON
    messages = load_messages_from_json_files()
    
    if not messages:
        print("❌ No se pudieron cargar mensajes")
        return False
    
    # 2. Analizar mensajes reales
    stats = analyze_real_messages(messages)
    
    if not stats:
        print("❌ No se pudieron generar estadísticas")
        return False
    
    # 3. Crear archivo de cache
    cache_file = create_cache_file(stats)
    
    if cache_file:
        print(f"\n🎉 ¡Cache generado exitosamente!")
        print(f"📁 Archivo: {cache_file}")
        print(f"🚀 Ahora puedes subirlo a Spaces con:")
        print(f"   ./upload_to_spaces.sh {cache_file} relationship_stats.json")
        return True
    
    return False

if __name__ == "__main__":
    main()