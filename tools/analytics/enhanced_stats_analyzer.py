#!/usr/bin/env python3
"""
Analizador de estadísticas mejorado con IA
Genera análisis más precisos y personalizados de la conversación
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno desde el archivo .env específico
env_path = Path(__file__).parent / '.env'
print(f"🔧 Cargando variables de entorno desde: {env_path}")
load_dotenv(env_path)

class EnhancedStatsAnalyzer:
    """Analizador avanzado de estadísticas con IA"""
    
    def __init__(self):
        # Verificar que la API key esté disponible
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY no encontrada en variables de entorno")
        
        print(f"✅ API Key cargada: {api_key[:20]}...")
        self.client = OpenAI(api_key=api_key)
        self.messages = []
        self.emoji_pattern = re.compile("["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
    
    def load_messages(self) -> List[Dict]:
        """Carga mensajes desde archivos JSON"""
        messages = []
        conversation_dir = Path("karemramos_1184297046409691")
        
        print(f"📂 Cargando mensajes desde: {conversation_dir}")
        
        if not conversation_dir.exists():
            print(f"❌ Directorio no encontrado: {conversation_dir}")
            return []
        
        for msg_file in sorted(conversation_dir.glob('message_*.json')):
            try:
                print(f"📄 Procesando: {msg_file.name}")
                with open(msg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_messages = data.get('messages', [])
                    messages.extend(file_messages)
                    
            except Exception as e:
                print(f"❌ Error leyendo {msg_file}: {e}")
        
        print(f"📊 Total mensajes cargados: {len(messages):,}")
        self.messages = messages
        return messages
    
    def analyze_emoji_usage(self) -> Dict:
        """Analiza el uso real de emojis en la conversación"""
        print("😊 Analizando uso real de emojis...")
        
        emoji_counter = Counter()
        emoji_by_sender = defaultdict(Counter)
        emoji_contexts = defaultdict(list)
        total_emoji_messages = 0
        
        for msg in self.messages:
            content = msg.get('content', '')
            sender = msg.get('sender_name', 'Unknown')
            
            if content:
                # Solo buscar emojis unicode reales
                emojis = self.emoji_pattern.findall(content)
                if emojis:
                    total_emoji_messages += 1
                    for emoji in emojis:
                        emoji_counter[emoji] += 1
                        emoji_by_sender[sender][emoji] += 1
        
        # Solo reportar si no se encontraron emojis reales
        if not emoji_counter:
            print("ℹ️ No se detectaron emojis unicode en los mensajes")
        
        print(f"🔍 Total emojis encontrados: {sum(emoji_counter.values())}")
        print(f"📊 Mensajes con emojis: {total_emoji_messages}")
        
        return {
            'most_used': dict(emoji_counter.most_common(10)),
            'by_sender': dict(emoji_by_sender),
            'contexts': dict(emoji_contexts),
            'total_emoji_messages': total_emoji_messages
        }
    
    def analyze_conversation_patterns(self) -> Dict:
        """Analiza patrones de conversación específicos"""
        print("📈 Analizando patrones de conversación...")
        
        patterns = {
            'response_times': [],
            'conversation_starters': Counter(),
            'goodnight_messages': 0,
            'good_morning_messages': 0,
            'long_messages': [],
            'short_bursts': 0,
            'voice_messages': 0,
            'photos_shared': 0,
            'videos_shared': 0
        }
        
        # Contar archivos multimedia reales en las carpetas
        print("🎵 Contando archivos multimedia...")
        multimedia_base_path = Path("karemramos_1184297046409691")
        
        # Contar audios
        audio_path = multimedia_base_path / "audio"
        if audio_path.exists():
            audio_files = [f for f in audio_path.iterdir() if f.is_file()]
            patterns['voice_messages'] = len(audio_files)
            print(f"🎤 Mensajes de voz encontrados: {len(audio_files)}")
        
        # Contar fotos
        photos_path = multimedia_base_path / "photos"
        if photos_path.exists():
            photo_files = [f for f in photos_path.iterdir() if f.is_file()]
            patterns['photos_shared'] = len(photo_files)
            print(f"📸 Fotos compartidas encontradas: {len(photo_files)}")
        
        # Contar videos
        videos_path = multimedia_base_path / "videos"
        if videos_path.exists():
            video_files = [f for f in videos_path.iterdir() if f.is_file()]
            patterns['videos_shared'] = len(video_files)
            print(f"🎬 Videos compartidos encontrados: {len(video_files)}")
        
        # Análisis temporal y patrones
        prev_timestamp = None
        prev_sender = None
        current_burst = 0
        
        for msg in self.messages:
            content = msg.get('content', '').lower()
            sender = msg.get('sender_name', 'Unknown')
            
            # Timestamp analysis
            if 'timestamp_ms' in msg:
                current_time = datetime.fromtimestamp(msg['timestamp_ms'] / 1000)
                
                # Response time analysis
                if prev_timestamp and prev_sender != sender:
                    response_time = (current_time - prev_timestamp).total_seconds() / 60
                    patterns['response_times'].append(response_time)
                
                # Morning/night messages
                hour = current_time.hour
                if 'buen' in content and ('día' in content or 'mañana' in content) and hour < 12:
                    patterns['good_morning_messages'] += 1
                elif ('buenas noches' in content or 'que descanses' in content) and hour > 20:
                    patterns['goodnight_messages'] += 1
                
                prev_timestamp = current_time
            
            # Content analysis
            if content:
                # Conversation starters
                if prev_sender != sender:
                    first_words = ' '.join(content.split()[:3])
                    patterns['conversation_starters'][first_words] += 1
                
                # Message length analysis
                if len(content) > 200:
                    patterns['long_messages'].append({
                        'length': len(content),
                        'sender': sender,
                        'preview': content[:100] + '...'
                    })
            
            # Message type analysis
            if msg.get('type') == 'Generic':
                if msg.get('audio_files'):
                    patterns['voice_messages'] += 1
                elif msg.get('photos'):
                    patterns['photos_shared'] += len(msg['photos'])
                elif msg.get('videos'):
                    patterns['videos_shared'] += len(msg['videos'])
            
            # Burst detection (multiple messages in quick succession)
            if prev_sender == sender:
                current_burst += 1
            else:
                if current_burst >= 3:
                    patterns['short_bursts'] += 1
                current_burst = 0
            
            prev_sender = sender
        
        return patterns
    
    def analyze_with_ai(self, sample_messages: List[str]) -> Dict:
        """Usa IA para analizar sentimientos y patrones complejos"""
        print("🤖 Analizando con IA...")
        
        # Tomar muestra representativa
        sample_text = "\n".join(sample_messages[:50])  # Primeros 50 mensajes como muestra
        
        prompt = f"""Analiza esta conversación de pareja y proporciona insights profundos:

CONVERSACIÓN (MUESTRA):
{sample_text}

ANALIZA:
1. **Dinámicas de comunicación**: ¿Cómo se comunican? ¿Quién inicia más conversaciones?
2. **Lenguaje único**: ¿Qué palabras, frases o expresiones son específicas de esta pareja?
3. **Temas principales**: ¿De qué hablan más? ¿Cuáles son sus intereses compartidos?
4. **Tono emocional**: ¿Cómo es el tono general? ¿Hay mucho cariño, humor, romanticismo?
5. **Momentos significativos**: ¿Qué tipos de momentos parecen importantes para ellos?

Responde en formato JSON:
{{
    "communication_style": {{
        "dominant_communicator": "quien habla más",
        "conversation_initiator": "quien inicia más",
        "response_style": "descripción del estilo de respuesta"
    }},
    "unique_language": {{
        "pet_names": ["apodos cariñosos encontrados"],
        "unique_phrases": ["frases específicas de ellos"],
        "communication_quirks": ["particularidades únicas"]
    }},
    "main_topics": ["tema1", "tema2", "tema3"],
    "emotional_tone": {{
        "overall_sentiment": "positivo/romántico/divertido/etc",
        "affection_level": "alto/medio/bajo",
        "humor_presence": "alto/medio/bajo"
    }},
    "relationship_insights": {{
        "connection_strength": "fuerte/medio/débil",
        "shared_interests": ["intereses compartidos"],
        "special_moments_types": ["tipos de momentos especiales"]
    }}
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto psicólogo de parejas que analiza comunicación y dinámicas relacionales. Proporciona insights profundos y precisos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"❌ Error en análisis IA: {e}")
            return {}
    
    def calculate_enhanced_metrics(self, emoji_data: Dict, patterns: Dict, ai_insights: Dict) -> Dict:
        """Calcula métricas mejoradas y más precisas"""
        print("📊 Calculando métricas mejoradas...")
        
        if not self.messages:
            return {}
        
        # Datos básicos
        total_messages = len(self.messages)
        senders = Counter(msg.get('sender_name', 'Unknown') for msg in self.messages)
        
        # Análisis temporal
        dates = []
        for msg in self.messages:
            if 'timestamp_ms' in msg:
                dates.append(datetime.fromtimestamp(msg['timestamp_ms'] / 1000))
        
        dates.sort()
        first_date, last_date = dates[0], dates[-1]
        total_days = (last_date - first_date).days + 1
        
        # Métricas mejoradas
        response_times = patterns.get('response_times', [])
        # Filtrar tiempos de respuesta negativos y muy grandes
        valid_response_times = [t for t in response_times if 0 <= t <= 1440]  # Entre 0 y 24 horas
        avg_response_time = sum(valid_response_times) / len(valid_response_times) if valid_response_times else 15
        
        # Score de conexión basado en múltiples factores (optimizado para relaciones muy activas)
        
        # Factor base: frecuencia de mensajes (escala ajustada para parejas súper activas)
        messages_per_day = total_messages / total_days
        if messages_per_day >= 100:  # 100+ mensajes/día es extraordinario
            frequency_score = 10
        elif messages_per_day >= 50:  # 50+ mensajes/día es muy alto
            frequency_score = 9
        elif messages_per_day >= 20:  # 20+ mensajes/día es alto
            frequency_score = 8
        else:
            frequency_score = min(10, messages_per_day / 5)  # Escala normal
        
        # Factor emocional: expresividad (no solo emojis)
        emoji_percentage = emoji_data.get('total_emoji_messages', 0) / total_messages * 100
        
        if emoji_percentage > 15:  # Si tiene buen % de emojis
            emoji_score = 10
        elif emoji_percentage > 8:
            emoji_score = 8
        elif emoji_percentage > 3:
            emoji_score = 6
        else:
            # Si no hay muchos emojis, evaluar expresividad por otros medios
            # Short bursts (ráfagas de mensajes) indican intensidad emocional
            burst_ratio = patterns.get('short_bursts', 0) / total_days  # Bursts por día
            long_msg_ratio = len(patterns.get('long_messages', [])) / (total_messages / 1000)  # Mensajes largos por 1000
            
            # Usar el análisis de IA como indicador principal si disponible
            if ai_insights.get('emotional_tone', {}).get('affection_level') == 'alto':
                emoji_score = 8  # Alto por IA
            elif burst_ratio > 10:  # Más de 10 bursts por día indica alta expresividad
                emoji_score = 7
            elif long_msg_ratio > 5:  # Muchos mensajes largos indican expresividad
                emoji_score = 6
            else:
                emoji_score = 5  # Neutral
        
        # Factor de equilibrio: participación balanceada
        sender_values = list(senders.values())
        if len(sender_values) >= 2:
            balance_ratio = min(sender_values) / max(sender_values)
            balance_score = balance_ratio * 10  # Balance perfecto = 10
        else:
            balance_score = 5  # Neutral si solo hay un sender
        
        # Factor de intensidad: conversaciones largas e intensas
        long_msg_ratio = len(patterns.get('long_messages', [])) / (total_messages / 1000)  # Por cada 1000 mensajes
        burst_intensity = patterns.get('short_bursts', 0) / total_days  # Bursts por día
        intensity_score = min(10, (long_msg_ratio * 2) + (burst_intensity / 5) + 5)  # Base 5
        
        # Factor de tiempo de respuesta (muy permisivo)
        if avg_response_time <= 60:  # 1 hora o menos
            response_score = 10
        elif avg_response_time <= 180:  # 3 horas o menos
            response_score = 9
        elif avg_response_time <= 360:  # 6 horas o menos
            response_score = 8
        else:
            response_score = 7  # Mínimo alto para parejas activas
        
        # Factor de insights de IA (peso aumentado)
        ai_score = 5  # Base neutral
        if ai_insights.get('emotional_tone', {}).get('affection_level') == 'alto':
            ai_score += 2
        if ai_insights.get('emotional_tone', {}).get('overall_sentiment') in ['positivo', 'romántico', 'cariñoso', 'positivo y cariñoso']:
            ai_score += 2
        if ai_insights.get('relationship_insights', {}).get('connection_strength') == 'fuerte':
            ai_score += 1
        ai_score = min(10, ai_score)
        
        # Promedio ponderado (dando más peso a frecuencia y AI insights)
        connection_score = (
            frequency_score * 0.35 +      # 35% - Frecuencia de comunicación (aumentado)
            ai_score * 0.25 +             # 25% - Insights de IA (aumentado)
            balance_score * 0.15 +        # 15% - Equilibrio en participación 
            intensity_score * 0.15 +      # 15% - Intensidad de conversaciones
            response_score * 0.1          # 10% - Tiempo de respuesta
        )
        
        # Para relaciones súper activas como esta, ajustar rango (8.5-10)
        if messages_per_day >= 100 and ai_insights.get('relationship_insights', {}).get('connection_strength') == 'fuerte':
            connection_score = max(8.5, min(10.0, connection_score))
        else:
            connection_score = max(7.5, min(10.0, connection_score))
        
        connection_score = round(connection_score, 1)
        
        # Fases de relación más inteligentes
        phases = self.calculate_relationship_phases(dates)
        
        return {
            "totalMessages": total_messages,
            "totalDays": total_days,
            "avgMessagesPerDay": round(total_messages / total_days, 1),
            "connectionScore": min(10.0, connection_score),
            "avgResponseTime": f"{int(avg_response_time)}min" if avg_response_time < 60 else f"{int(avg_response_time/60)}h",
            "relationshipPhases": phases,
            "topEmojis": list(emoji_data.get('most_used', {}).keys())[:5],
            "specialMoments": self.calculate_special_moments(patterns, emoji_data, total_messages),
            "senderDistribution": dict(senders),
            "conversationPatterns": {
                "voiceMessages": patterns.get('voice_messages', 0),
                "photosShared": patterns.get('photos_shared', 0),
                "videosShared": patterns.get('videos_shared', 0),
                "longMessages": len(patterns.get('long_messages', [])),
                "shortBursts": patterns.get('short_bursts', 0)
            },
            "aiInsights": ai_insights,
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "enhanced_ai_analysis"
        }
    
    def calculate_special_moments(self, patterns: Dict, emoji_data: Dict, total_messages: int) -> int:
        """Calcula momentos especiales basado en varios indicadores"""
        special_count = 0
        
        # Rituales de pareja (buenos días/noches)
        special_count += patterns.get('good_morning_messages', 0)
        special_count += patterns.get('goodnight_messages', 0)
        
        # Mensajes largos (pueden ser cartas de amor)
        long_messages = patterns.get('long_messages', [])
        special_count += len([msg for msg in long_messages if msg.get('length', 0) > 300])
        
        # MULTIMEDIA (¡Los datos más importantes!)
        voice_messages = patterns.get('voice_messages', 0)
        photos_shared = patterns.get('photos_shared', 0)
        videos_shared = patterns.get('videos_shared', 0)
        
        # Mensajes de voz son muy personales (cada 10 = 1 momento especial)
        special_count += voice_messages // 10
        
        # Fotos compartidas (cada 5 = 1 momento especial)
        special_count += photos_shared // 5
        
        # Videos son súper especiales (cada uno cuenta como 3 momentos)
        special_count += videos_shared * 3
        
        # Bonus por alta actividad multimedia
        multimedia_total = voice_messages + photos_shared + videos_shared
        if multimedia_total > 1000:  # Más de 1000 archivos multimedia
            special_count += 100  # Gran bonus por pareja súper multimedia
        elif multimedia_total > 500:
            special_count += 50
        elif multimedia_total > 100:
            special_count += 20
        
        # Short bursts también indican momentos intensos
        burst_bonus = min(50, patterns.get('short_bursts', 0) // 50)  # Cada 50 bursts = 1 momento
        special_count += burst_bonus
        
        return special_count
    
    def calculate_relationship_phases(self, dates: List[datetime]) -> List[Dict]:
        """Calcula fases de relación basadas en actividad temporal"""
        if len(dates) < 30:  # Muy pocos datos
            return []
        
        # Agrupar por meses
        monthly_counts = defaultdict(int)
        for date in dates:
            month_key = date.strftime('%Y-%m')
            monthly_counts[month_key] += 1
        
        sorted_months = sorted(monthly_counts.items())
        
        if len(sorted_months) < 3:
            return []
        
        # Dividir en fases basado en patrones de actividad
        third = len(sorted_months) // 3
        
        phases = []
        phase_names = ["Inicio", "Creciendo", "Consolidación"]
        
        for i in range(3):
            start_idx = i * third if i < 2 else i * third
            end_idx = (i + 1) * third if i < 2 else len(sorted_months)
            
            phase_months = sorted_months[start_idx:end_idx]
            total_messages = sum(count for _, count in phase_months)
            avg_messages = total_messages / len(phase_months)
            
            phases.append({
                "phase": phase_names[i],
                "messages": total_messages,
                "avgPerMonth": round(avg_messages, 1),
                "period": f"{phase_months[0][0]} - {phase_months[-1][0]}",
                "months": len(phase_months)
            })
        
        return phases
    
    def generate_enhanced_stats(self) -> Dict:
        """Genera estadísticas completas mejoradas"""
        print("🚀 Iniciando análisis mejorado...")
        
        # Cargar mensajes
        if not self.messages:
            self.load_messages()
        
        if not self.messages:
            print("❌ No se encontraron mensajes para analizar")
            return {}
        
        # Ejecutar análisis en paralelo
        emoji_data = self.analyze_emoji_usage()
        patterns = self.analyze_conversation_patterns()
        
        # Preparar muestra para IA
        sample_messages = [
            msg.get('content', '') for msg in self.messages[:100] 
            if msg.get('content') and len(msg.get('content', '')) > 10
        ]
        
        ai_insights = self.analyze_with_ai(sample_messages)
        
        # Calcular métricas finales
        enhanced_stats = self.calculate_enhanced_metrics(emoji_data, patterns, ai_insights)
        
        print("✅ Análisis mejorado completado")
        return enhanced_stats


def main():
    """Función principal para ejecutar el análisis mejorado"""
    analyzer = EnhancedStatsAnalyzer()
    
    try:
        stats = analyzer.generate_enhanced_stats()
        
        if stats:
            # Guardar estadísticas mejoradas
            output_file = Path("cache/enhanced_relationship_stats.json")
            output_file.parent.mkdir(exist_ok=True)
            
            cache_data = {
                "stats": stats,
                "cached_at": datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Estadísticas mejoradas guardadas en: {output_file}")
            
            # Mostrar resumen
            print("\n📊 RESUMEN DE ANÁLISIS MEJORADO:")
            print(f"📱 Total mensajes: {stats.get('totalMessages', 0):,}")
            print(f"📅 Días de conversación: {stats.get('totalDays', 0):,}")  
            print(f"💕 Score de conexión: {stats.get('connectionScore', 0)}/10")
            print(f"😊 Emojis más usados: {', '.join(stats.get('topEmojis', [])[:3])}")
            print(f"⚡ Tiempo promedio de respuesta: {stats.get('avgResponseTime', 'N/A')}")
            
        else:
            print("❌ No se pudieron generar estadísticas")
            
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()