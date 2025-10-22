"""
Script para procesar conversaciones y extraer información de la relación.
Este script toma mensajes en formato texto y extrae datos relevantes.

INSTRUCCIONES DE USO:
1. Copia tus mensajes de WhatsApp/iMessage al archivo: data/raw_messages.txt
2. Ejecuta: python scripts/process_messages.py
3. Revisa los resultados en: data/conversation_analysis.json
"""

import json
import re
from datetime import datetime
from collections import Counter
from typing import Dict, List, Tuple


def parse_whatsapp_export(file_path: str) -> List[Dict]:
    """
    Parse WhatsApp chat export format.
    
    Format: [DD/MM/YYYY, HH:MM:SS] Name: Message
    """
    messages = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern for WhatsApp messages
        pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+?)(?=\[\d{1,2}/\d{1,2}/\d{2,4}|$)'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            date_str, time_str, sender, message = match.groups()
            
            messages.append({
                "date": date_str.strip(),
                "time": time_str.strip(),
                "sender": sender.strip(),
                "message": message.strip()
            })
        
        print(f"✓ Parsed {len(messages)} messages from WhatsApp export")
        return messages
        
    except FileNotFoundError:
        print("✗ File not found. Please create data/raw_messages.txt")
        return []


def extract_important_dates(messages: List[Dict]) -> List[Dict]:
    """
    Extract mentions of dates, months, or time references.
    """
    date_mentions = []
    
    # Patterns for date mentions in Spanish
    date_patterns = [
        r'\b\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',
        r'\b(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b',
        r'\bhace\s+\d+\s+(día|días|semana|semanas|mes|meses|año|años)\b',
    ]
    
    for msg in messages:
        text = msg['message'].lower()
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                date_mentions.append({
                    "date": msg['date'],
                    "sender": msg['sender'],
                    "mention": msg['message'][:100],
                    "context": msg['message']
                })
    
    print(f"✓ Found {len(date_mentions)} date mentions")
    return date_mentions


def extract_locations(messages: List[Dict]) -> List[Dict]:
    """
    Extract mentions of places and locations.
    """
    location_keywords = [
        'café', 'cafetería', 'restaurante', 'parque', 'plaza',
        'cine', 'centro', 'mall', 'universidad', 'casa',
        'bar', 'playa', 'montaña', 'ciudad', 'pueblo'
    ]
    
    locations = []
    
    for msg in messages:
        text = msg['message'].lower()
        for keyword in location_keywords:
            if keyword in text:
                locations.append({
                    "date": msg['date'],
                    "sender": msg['sender'],
                    "location_type": keyword,
                    "context": msg['message']
                })
    
    print(f"✓ Found {len(locations)} location mentions")
    return locations


def extract_special_phrases(messages: List[Dict]) -> Dict:
    """
    Extract frequently used phrases, nicknames, and inside jokes.
    """
    # Words that might be nicknames (capitalized, repeated)
    all_text = " ".join([msg['message'] for msg in messages])
    words = re.findall(r'\b[A-Z][a-z]+\b', all_text)
    
    word_freq = Counter(words)
    common_words = word_freq.most_common(20)
    
    # Emoji usage
    emojis = re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', all_text)
    emoji_freq = Counter(emojis)
    
    print(f"✓ Analyzed phrase patterns")
    
    return {
        "common_capitalized_words": common_words[:10],
        "most_used_emojis": emoji_freq.most_common(5),
        "total_words": len(all_text.split())
    }


def analyze_conversation_style(messages: List[Dict], your_name: str) -> Dict:
    """
    Analyze communication style (message length, frequency, tone).
    """
    your_messages = [msg for msg in messages if msg['sender'].lower() == your_name.lower()]
    her_messages = [msg for msg in messages if msg['sender'].lower() != your_name.lower()]
    
    your_avg_length = sum(len(msg['message']) for msg in your_messages) / max(len(your_messages), 1)
    her_avg_length = sum(len(msg['message']) for msg in her_messages) / max(len(her_messages), 1)
    
    print(f"✓ Analyzed conversation style")
    
    return {
        "your_message_count": len(your_messages),
        "her_message_count": len(her_messages),
        "your_avg_message_length": round(your_avg_length, 1),
        "her_avg_message_length": round(her_avg_length, 1),
        "total_conversations": len(messages)
    }


def generate_quiz_suggestions(analysis: Dict) -> List[Dict]:
    """
    Generate quiz question suggestions based on conversation analysis.
    """
    suggestions = []
    
    # Suggest questions based on dates
    if analysis.get('important_dates'):
        suggestions.append({
            "type": "date",
            "question": "¿Recuerdas qué día fue [evento importante]?",
            "tip": "Usa las fechas encontradas en los mensajes"
        })
    
    # Suggest questions based on locations
    if analysis.get('locations'):
        common_places = Counter([loc['location_type'] for loc in analysis['locations']])
        top_place = common_places.most_common(1)[0][0] if common_places else "café"
        suggestions.append({
            "type": "location",
            "question": f"¿Dónde fue nuestra primera vez en [{top_place}]?",
            "tip": "Revisa los mensajes sobre lugares visitados"
        })
    
    # Suggest nickname question
    if analysis.get('special_phrases'):
        suggestions.append({
            "type": "nickname",
            "question": "¿Cuál es el apodo especial que te puse?",
            "tip": "Revisa las palabras capitalizadas más frecuentes"
        })
    
    print(f"✓ Generated {len(suggestions)} quiz question suggestions")
    
    return suggestions


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("💕 ROMANTIC AI - MESSAGE PROCESSOR")
    print("="*60 + "\n")
    
    # File paths
    input_file = "data/raw_messages.txt"
    output_file = "data/conversation_analysis.json"
    
    print("📥 Step 1: Reading messages...")
    messages = parse_whatsapp_export(input_file)
    
    if not messages:
        print("\n⚠️  No messages found!")
        print("\nINSTRUCCIONES:")
        print("1. Exporta tu chat de WhatsApp")
        print("2. Guarda el archivo como: data/raw_messages.txt")
        print("3. Ejecuta este script nuevamente\n")
        return
    
    print(f"\n📊 Step 2: Analyzing {len(messages)} messages...\n")
    
    # Get your name
    your_name = input("¿Cuál es TU nombre en el chat? (como aparece en los mensajes): ").strip()
    
    # Extract information
    important_dates = extract_important_dates(messages)
    locations = extract_locations(messages)
    special_phrases = extract_special_phrases(messages)
    conversation_style = analyze_conversation_style(messages, your_name)
    
    # Compile analysis
    analysis = {
        "metadata": {
            "processed_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "date_range": {
                "first_message": messages[0]['date'] if messages else None,
                "last_message": messages[-1]['date'] if messages else None
            }
        },
        "important_dates": important_dates[:20],  # Top 20
        "locations": locations[:20],  # Top 20
        "special_phrases": special_phrases,
        "conversation_style": conversation_style,
        "quiz_suggestions": generate_quiz_suggestions({
            "important_dates": important_dates,
            "locations": locations,
            "special_phrases": special_phrases
        })
    }
    
    # Save results
    print(f"\n💾 Step 3: Saving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, indent=2, fp=f, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*60)
    print(f"\n📄 Resultados guardados en: {output_file}")
    print(f"💬 Total de mensajes analizados: {len(messages)}")
    print(f"📅 Fechas importantes encontradas: {len(important_dates)}")
    print(f"📍 Lugares mencionados: {len(locations)}")
    print(f"💡 Sugerencias de preguntas generadas: {len(analysis['quiz_suggestions'])}")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa data/conversation_analysis.json")
    print("2. Usa las sugerencias para crear preguntas en data/questions.json")
    print("3. Personaliza el contexto del chatbot con esta información\n")


if __name__ == "__main__":
    main()
