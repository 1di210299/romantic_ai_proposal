"""
Script para procesar mensajes de Instagram DM exportados.
Extrae información relevante de los mensajes directos de Instagram.
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from collections import Counter


def load_instagram_messages(base_path: str) -> List[Dict]:
    """
    Carga mensajes de Instagram desde el export de datos.
    
    Args:
        base_path: Ruta al folder de export de Instagram
    
    Returns:
        Lista de conversaciones con mensajes
    """
    messages_path = os.path.join(base_path, "your_instagram_activity", "messages", "inbox")
    
    if not os.path.exists(messages_path):
        print(f"✗ No se encontró la carpeta de mensajes: {messages_path}")
        return []
    
    all_conversations = []
    
    # Buscar todos los archivos message_*.json en subdirectorios
    for root, dirs, files in os.walk(messages_path):
        for file in files:
            if file.startswith("message_") and file.endswith(".json"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        conv_data = json.load(f)
                        all_conversations.append(conv_data)
                except Exception as e:
                    print(f"✗ Error leyendo {file}: {e}")
    
    print(f"✓ Cargadas {len(all_conversations)} conversaciones de Instagram")
    return all_conversations


def filter_target_conversation(conversations: List[Dict], target_participant: str) -> Dict:
    """
    Filtra la conversación específica con tu enamorada.
    
    Args:
        conversations: Lista de todas las conversaciones
        target_participant: Nombre o username de tu enamorada
    
    Returns:
        Conversación filtrada
    """
    target_conv = None
    
    for conv in conversations:
        participants = conv.get('participants', [])
        participant_names = [p.get('name', '').lower() for p in participants]
        
        if any(target_participant.lower() in name for name in participant_names):
            target_conv = conv
            break
    
    if target_conv:
        msg_count = len(target_conv.get('messages', []))
        print(f"✓ Encontrada conversación con {target_participant}: {msg_count} mensajes")
        return target_conv
    else:
        print(f"✗ No se encontró conversación con '{target_participant}'")
        print("\n📋 Participantes disponibles:")
        unique_names = set()
        for conv in conversations:
            for p in conv.get('participants', []):
                unique_names.add(p.get('name', 'Unknown'))
        for name in sorted(unique_names):
            print(f"   - {name}")
        return None


def extract_instagram_data(conversation: Dict, your_name: str) -> Dict:
    """
    Extrae información relevante de los mensajes de Instagram.
    
    Args:
        conversation: Conversación de Instagram
        your_name: Tu nombre como aparece en Instagram
    
    Returns:
        Diccionario con análisis de la conversación
    """
    messages = conversation.get('messages', [])
    
    # Separar mensajes por remitente
    your_messages = []
    her_messages = []
    
    for msg in messages:
        sender = msg.get('sender_name', '')
        content = msg.get('content', '')
        timestamp = msg.get('timestamp_ms', 0)
        
        if not content:  # Skip empty messages (reactions, media, etc.)
            continue
        
        msg_data = {
            'sender': sender,
            'content': content,
            'timestamp': timestamp,
            'date': datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if sender.lower() == your_name.lower():
            your_messages.append(msg_data)
        else:
            her_messages.append(msg_data)
    
    # Análisis de contenido
    all_content = " ".join([msg['content'] for msg in messages if msg.get('content')])
    
    # Buscar menciones de lugares
    location_keywords = [
        'café', 'cafetería', 'restaurante', 'parque', 'plaza',
        'cine', 'centro', 'mall', 'universidad', 'casa',
        'bar', 'playa', 'montaña'
    ]
    
    location_mentions = []
    for msg in messages:
        content = msg.get('content', '').lower()
        for keyword in location_keywords:
            if keyword in content:
                location_mentions.append({
                    'date': datetime.fromtimestamp(msg.get('timestamp_ms', 0) / 1000).strftime('%Y-%m-%d'),
                    'sender': msg.get('sender_name', ''),
                    'mention': msg.get('content', '')[:100],
                    'location_type': keyword
                })
    
    # Buscar fechas mencionadas
    import re
    date_pattern = r'\b\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b'
    date_mentions = []
    
    for msg in messages:
        content = msg.get('content', '')
        if re.search(date_pattern, content, re.IGNORECASE):
            date_mentions.append({
                'date': datetime.fromtimestamp(msg.get('timestamp_ms', 0) / 1000).strftime('%Y-%m-%d'),
                'sender': msg.get('sender_name', ''),
                'mention': content
            })
    
    # Palabras más frecuentes
    words = re.findall(r'\b\w+\b', all_content.lower())
    word_freq = Counter(words)
    common_words = [w for w, c in word_freq.most_common(50) if len(w) > 3]  # Palabras de más de 3 letras
    
    print(f"✓ Analizados {len(messages)} mensajes de Instagram")
    
    return {
        'metadata': {
            'total_messages': len(messages),
            'your_messages': len(your_messages),
            'her_messages': len(her_messages),
            'first_message': messages[-1] if messages else None,
            'last_message': messages[0] if messages else None,
            'conversation_span_days': (messages[0].get('timestamp_ms', 0) - messages[-1].get('timestamp_ms', 0)) / (1000 * 60 * 60 * 24) if messages else 0
        },
        'location_mentions': location_mentions[:30],
        'date_mentions': date_mentions[:20],
        'common_words': common_words[:20],
        'sample_your_messages': [msg['content'] for msg in your_messages[:5]],
        'sample_her_messages': [msg['content'] for msg in her_messages[:5]]
    }


def generate_relationship_context(analysis: Dict, your_name: str, her_name: str) -> Dict:
    """
    Genera el contexto de la relación para el chatbot.
    """
    return {
        "his_name": your_name,
        "her_name": her_name,
        "relationship_data": {
            "total_messages": analysis['metadata']['total_messages'],
            "conversation_span_days": round(analysis['metadata']['conversation_span_days'], 1),
            "first_interaction": analysis['metadata']['first_message']['date'] if analysis['metadata']['first_message'] else None,
            "common_topics": analysis['common_words'][:10],
            "places_mentioned": list(set([loc['location_type'] for loc in analysis['location_mentions']]))[:5]
        },
        "conversation_style": "casual, using emojis and informal language based on Instagram DM patterns",
        "special_moments": [
            f"Han intercambiado {analysis['metadata']['total_messages']} mensajes",
            f"Conversación activa por {round(analysis['metadata']['conversation_span_days'])} días"
        ]
    }


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("💕 INSTAGRAM MESSAGE PROCESSOR - Romantic AI Proposal")
    print("="*70 + "\n")
    
    # Detect Instagram export folder
    current_dir = os.getcwd()
    instagram_folders = [f for f in os.listdir(current_dir) if f.startswith('instagram-') and os.path.isdir(f)]
    
    if not instagram_folders:
        print("✗ No se encontró export de Instagram en esta carpeta")
        print("\n📥 INSTRUCCIONES:")
        print("1. Ve a Instagram → Settings → Security → Download data")
        print("2. Solicita tu información")
        print("3. Descarga el archivo ZIP")
        print("4. Extrae el contenido en la carpeta romantic_ai_proposal/")
        print("5. Ejecuta este script nuevamente\n")
        return
    
    # Use first Instagram folder found
    instagram_path = instagram_folders[0]
    print(f"✓ Export de Instagram encontrado: {instagram_path}\n")
    
    # Load conversations
    print("📥 Cargando conversaciones...")
    conversations = load_instagram_messages(instagram_path)
    
    if not conversations:
        print("\n✗ No se pudieron cargar las conversaciones")
        return
    
    # Get target person
    print("\n" + "-"*70)
    her_name = input("¿Cuál es el NOMBRE de tu enamorada en Instagram? (como aparece en DMs): ").strip()
    your_name = input("¿Cuál es TU nombre en Instagram? (como aparece en DMs): ").strip()
    print("-"*70 + "\n")
    
    # Filter conversation
    print("🔍 Buscando conversación...")
    target_conv = filter_target_conversation(conversations, her_name)
    
    if not target_conv:
        return
    
    # Extract data
    print("\n📊 Analizando mensajes...")
    analysis = extract_instagram_data(target_conv, your_name)
    
    # Generate context
    print("🎯 Generando contexto de la relación...")
    relationship_context = generate_relationship_context(analysis, your_name, her_name)
    
    # Combine all data
    output_data = {
        "processed_at": datetime.now().isoformat(),
        "source": "Instagram DM Export",
        "relationship_context": relationship_context,
        "conversation_analysis": analysis
    }
    
    # Save results
    output_file = "data/instagram_analysis.json"
    print(f"\n💾 Guardando análisis en {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, indent=2, fp=f, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70)
    print(f"\n📊 RESUMEN:")
    print(f"   📧 Total de mensajes: {analysis['metadata']['total_messages']}")
    print(f"   ✍️  Tus mensajes: {analysis['metadata']['your_messages']}")
    print(f"   💬 Sus mensajes: {analysis['metadata']['her_messages']}")
    print(f"   📅 Días de conversación: {round(analysis['metadata']['conversation_span_days'], 1)}")
    print(f"   📍 Lugares mencionados: {len(analysis['location_mentions'])}")
    print(f"   🗓️  Fechas importantes: {len(analysis['date_mentions'])}")
    
    print(f"\n📄 Resultados guardados en: {output_file}")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa data/instagram_analysis.json")
    print("2. Usa la información para crear preguntas personalizadas")
    print("3. Actualiza data/questions.json con tus preguntas")
    print("4. Configura el contexto del chatbot en backend/app.py\n")


if __name__ == "__main__":
    main()
