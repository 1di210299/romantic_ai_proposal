"""
Analizador OPTIMIZADO de mensajes con procesamiento en CHUNKS.
Procesa mensajes en paralelo para máxima velocidad.
"""

import json
import os
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


class ChunkedMessageAnalyzer:
    """Analizador optimizado que procesa mensajes en chunks paralelos."""
    
    def __init__(self, conversation_path: str, chunk_size: int = 5000):
        """
        Initialize analyzer.
        
        Args:
            conversation_path: Ruta a la carpeta karemramos_XXXX
            chunk_size: Tamaño de cada chunk (mensajes por chunk)
        """
        self.conversation_path = Path(conversation_path)
        self.chunk_size = chunk_size
        self.your_name = "Juan Diego Gutierrez"
        self.her_name = "Karem Ramos"
        
    def load_all_messages(self) -> List[Dict]:
        """Carga TODOS los mensajes de todos los archivos."""
        print("\n" + "="*70)
        print("📂 CARGANDO MENSAJES DE INSTAGRAM")
        print("="*70)
        
        all_messages = []
        message_files = sorted(self.conversation_path.glob("message_*.json"))
        
        for msg_file in message_files:
            print(f"   📄 Cargando {msg_file.name}...")
            try:
                with open(msg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = data.get('messages', [])
                    all_messages.extend(messages)
                    print(f"      ✓ {len(messages):,} mensajes")
            except Exception as e:
                print(f"      ✗ Error: {e}")
        
        # Ordenar por timestamp (más antiguo primero)
        all_messages.sort(key=lambda x: x.get('timestamp_ms', 0))
        
        print(f"\n✅ Total mensajes cargados: {len(all_messages):,}")
        print(f"📦 Se dividirán en chunks de {self.chunk_size:,} mensajes\n")
        
        return all_messages
    
    def split_into_chunks(self, messages: List[Dict]) -> List[List[Dict]]:
        """Divide mensajes en chunks para procesamiento paralelo."""
        chunks = []
        for i in range(0, len(messages), self.chunk_size):
            chunk = messages[i:i + self.chunk_size]
            chunks.append(chunk)
        
        print(f"📦 Mensajes divididos en {len(chunks)} chunks")
        return chunks
    
    def analyze_chunk(self, chunk: List[Dict], chunk_id: int) -> Dict:
        """
        Analiza un chunk individual de mensajes.
        Esta función puede ejecutarse en paralelo.
        """
        result = {
            'chunk_id': chunk_id,
            'size': len(chunk),
            'juan_messages': 0,
            'karem_messages': 0,
            'location_mentions': [],
            'date_mentions': [],
            'words': [],
            'nicknames': [],
            'timestamps': []
        }
        
        # Patrones para búsqueda
        location_keywords = [
            'café', 'cafetería', 'restaurante', 'parque', 'plaza',
            'cine', 'centro', 'mall', 'casa', 'depa', 'departamento',
            'bar', 'playa', 'montaña', 'universidad', 'u', 'trabajo',
            'gimnasio', 'hospital', 'aeropuerto', 'terminal', 'hotel',
            'museo', 'teatro', 'concierto', 'estadio'
        ]
        
        date_pattern = r'\b\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b'
        
        affection_patterns = [
            r'\b(amor|amorcito|mi amor|bb|bebe|bebé|nena|nene|cielo|vida|corazón)\b',
            r'\b(hermosa|hermoso|linda|lindo|preciosa|precioso|reina|rey)\b',
            r'\b(mi vida|mi cielo|mi todo|gordita|gordito|flaca|flaco|chiquita|chiquito)\b'
        ]
        
        stop_words = {
            'que', 'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 
            'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'es', 'lo', 
            'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha',
            'si', 'me', 'te', 'mi', 'tu', 'yo', 'ti', 'eso', 'bien', 'muy',
            'todo', 'cuando', 'hasta', 'sin', 'sobre', 'también', 'donde'
        }
        
        # Procesar cada mensaje del chunk
        for msg in chunk:
            sender = msg.get('sender_name', '')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp_ms', 0)
            
            # Contar mensajes por persona
            if self.your_name in sender:
                result['juan_messages'] += 1
            elif self.her_name in sender:
                result['karem_messages'] += 1
            
            # Solo procesar mensajes con contenido
            if not content:
                continue
            
            # Guardar timestamp
            if timestamp:
                result['timestamps'].append(timestamp)
            
            content_lower = content.lower()
            
            # Buscar ubicaciones
            for keyword in location_keywords:
                if keyword in content_lower:
                    result['location_mentions'].append({
                        'date': datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d') if timestamp else None,
                        'sender': sender,
                        'keyword': keyword,
                        'context': content[:150]
                    })
            
            # Buscar fechas
            date_matches = re.findall(date_pattern, content, re.IGNORECASE)
            if date_matches:
                result['date_mentions'].append({
                    'date': datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d') if timestamp else None,
                    'sender': sender,
                    'mention': content[:200]
                })
            
            # Buscar apodos
            for pattern in affection_patterns:
                nickname_matches = re.findall(pattern, content_lower, re.IGNORECASE)
                result['nicknames'].extend(nickname_matches)
            
            # Extraer palabras
            words = re.findall(r'\b\w+\b', content_lower)
            filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
            result['words'].extend(filtered_words)
        
        return result
    
    def merge_chunk_results(self, chunk_results: List[Dict]) -> Dict:
        """Combina resultados de todos los chunks."""
        print("\n🔄 Combinando resultados de todos los chunks...")
        
        merged = {
            'total_messages': sum(r['size'] for r in chunk_results),
            'juan_messages': sum(r['juan_messages'] for r in chunk_results),
            'karem_messages': sum(r['karem_messages'] for r in chunk_results),
            'location_mentions': [],
            'date_mentions': [],
            'word_frequency': Counter(),
            'nickname_frequency': Counter(),
            'all_timestamps': []
        }
        
        # Combinar todas las listas
        for result in chunk_results:
            merged['location_mentions'].extend(result['location_mentions'])
            merged['date_mentions'].extend(result['date_mentions'])
            merged['word_frequency'].update(result['words'])
            merged['nickname_frequency'].update(result['nicknames'])
            merged['all_timestamps'].extend(result['timestamps'])
        
        # Calcular estadísticas temporales
        if merged['all_timestamps']:
            merged['all_timestamps'].sort()
            first_ts = merged['all_timestamps'][0]
            last_ts = merged['all_timestamps'][-1]
            
            merged['first_message'] = {
                'date': datetime.fromtimestamp(first_ts / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': first_ts
            }
            merged['last_message'] = {
                'date': datetime.fromtimestamp(last_ts / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': last_ts
            }
            
            first_date = datetime.fromtimestamp(first_ts / 1000)
            last_date = datetime.fromtimestamp(last_ts / 1000)
            merged['days_together'] = (last_date - first_date).days
            merged['avg_messages_per_day'] = merged['total_messages'] / max(merged['days_together'], 1)
        
        print(f"   ✓ Combinados {len(chunk_results)} chunks")
        print(f"   ✓ Total mensajes: {merged['total_messages']:,}")
        
        return merged
    
    def generate_analysis_report(self, merged_data: Dict) -> Dict:
        """Genera reporte final con análisis completo."""
        print("\n📊 GENERANDO REPORTE DE ANÁLISIS...")
        
        # Top palabras más usadas
        top_words = merged_data['word_frequency'].most_common(50)
        
        # Top apodos
        top_nicknames = merged_data['nickname_frequency'].most_common(20)
        
        # Top ubicaciones mencionadas
        location_counter = Counter(
            loc['keyword'] for loc in merged_data['location_mentions']
        )
        top_locations = location_counter.most_common(15)
        
        # Análisis por mes
        messages_by_month = defaultdict(int)
        for ts in merged_data['all_timestamps']:
            date = datetime.fromtimestamp(ts / 1000)
            month_key = date.strftime('%Y-%m')
            messages_by_month[month_key] += 1
        
        # Crear reporte
        report = {
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'total_messages': merged_data['total_messages'],
                'chunk_size_used': self.chunk_size,
                'processing_method': 'parallel_chunks'
            },
            'timeline': {
                'first_message': merged_data.get('first_message'),
                'last_message': merged_data.get('last_message'),
                'days_together': merged_data.get('days_together', 0),
                'years_together': round(merged_data.get('days_together', 0) / 365, 2),
                'avg_messages_per_day': round(merged_data.get('avg_messages_per_day', 0), 1),
                'messages_by_month': dict(sorted(messages_by_month.items()))
            },
            'participants': {
                self.your_name: {
                    'total_messages': merged_data['juan_messages'],
                    'percentage': round(merged_data['juan_messages'] / merged_data['total_messages'] * 100, 1)
                },
                self.her_name: {
                    'total_messages': merged_data['karem_messages'],
                    'percentage': round(merged_data['karem_messages'] / merged_data['total_messages'] * 100, 1)
                }
            },
            'content_analysis': {
                'top_words': [{'word': w, 'count': c} for w, c in top_words],
                'top_nicknames': [{'nickname': n, 'count': c} for n, c in top_nicknames],
                'top_locations': [{'location': l, 'count': c} for l, c in top_locations],
                'total_unique_words': len(merged_data['word_frequency']),
                'total_location_mentions': len(merged_data['location_mentions']),
                'total_date_mentions': len(merged_data['date_mentions'])
            },
            'location_details': merged_data['location_mentions'][:100],  # Top 100
            'date_mentions': merged_data['date_mentions'][:50],  # Top 50
            'question_suggestions': []
        }
        
        # Generar sugerencias de preguntas
        suggestions = self.generate_question_suggestions(report)
        report['question_suggestions'] = suggestions
        
        return report
    
    def generate_question_suggestions(self, report: Dict) -> List[Dict]:
        """Genera sugerencias inteligentes de preguntas."""
        print("\n💡 Generando sugerencias de preguntas...")
        
        suggestions = []
        timeline = report['timeline']
        content = report['content_analysis']
        
        # 1. Pregunta sobre primer mensaje
        if timeline.get('first_message'):
            suggestions.append({
                'category': 'Inicio de la relación',
                'question': '¿Recuerdas cuándo fue nuestro primer mensaje en Instagram?',
                'type': 'date',
                'correct_answers': [
                    timeline['first_message']['date'],
                    datetime.fromisoformat(timeline['first_message']['date']).strftime('%d de %B de %Y'),
                    datetime.fromisoformat(timeline['first_message']['date']).strftime('%B %Y')
                ],
                'hints': [
                    f"Fue hace {timeline['years_together']} años...",
                    f"Fue en el mes de {datetime.fromisoformat(timeline['first_message']['date']).strftime('%B')}",
                    f"Exactamente el {datetime.fromisoformat(timeline['first_message']['date']).strftime('%d de %B de %Y')}"
                ],
                'difficulty': 'hard'
            })
        
        # 2. Pregunta sobre tiempo juntos
        if timeline.get('years_together', 0) >= 1:
            years = int(timeline['years_together'])
            suggestions.append({
                'category': 'Tiempo juntos',
                'question': '¿Cuántos años llevamos conversando?',
                'type': 'number',
                'correct_answers': [
                    str(years),
                    f"{years} años",
                    f"aproximadamente {years} años",
                    f"como {years} años"
                ],
                'hints': [
                    f"Son más de {years - 1} años...",
                    f"Estamos cerca de los {years + 1} años",
                    f"Exactamente {years} años"
                ],
                'difficulty': 'medium'
            })
        
        # 3. Pregunta sobre lugares
        if content['top_locations']:
            top_loc = content['top_locations'][0]
            suggestions.append({
                'category': 'Lugares especiales',
                'question': '¿Cuál es el tipo de lugar que más mencionamos en nuestras conversaciones?',
                'type': 'location',
                'correct_answers': [
                    top_loc['location'],
                    f"{top_loc['location']}s",
                    f"el {top_loc['location']}"
                ],
                'hints': [
                    f"Es un lugar donde solemos pasar tiempo...",
                    f"Tiene que ver con {top_loc['location'][0:3]}...",
                    f"Es: {top_loc['location']}"
                ],
                'context': f"Mencionado {top_loc['count']} veces",
                'difficulty': 'medium'
            })
        
        # 4. Pregunta sobre apodos
        if content['top_nicknames']:
            top_nick = content['top_nicknames'][0]
            suggestions.append({
                'category': 'Apodos cariñosos',
                'question': '¿Cómo te digo más seguido?',
                'type': 'nickname',
                'correct_answers': [
                    top_nick['nickname'],
                    f"mi {top_nick['nickname']}" if 'mi' not in top_nick['nickname'] else top_nick['nickname'],
                    top_nick['nickname'].replace('mi ', '')
                ],
                'hints': [
                    f"Es un apodo cariñoso muy común...",
                    f"Empieza con '{top_nick['nickname'][0:2]}'...",
                    f"Es: {top_nick['nickname']}"
                ],
                'context': f"Usado {top_nick['count']} veces",
                'difficulty': 'easy'
            })
        
        # 5. Pregunta sobre mensajes por día
        avg_msgs = timeline.get('avg_messages_per_day', 0)
        if avg_msgs > 10:
            suggestions.append({
                'category': 'Estadísticas',
                'question': '¿Cuántos mensajes nos enviamos aproximadamente por día?',
                'type': 'number',
                'correct_answers': [
                    str(int(avg_msgs)),
                    f"{int(avg_msgs)} mensajes",
                    f"como {int(avg_msgs)}",
                    f"alrededor de {int(avg_msgs)}"
                ],
                'hints': [
                    f"Son más de {int(avg_msgs * 0.7)}...",
                    f"Menos de {int(avg_msgs * 1.3)}...",
                    f"Exactamente {int(avg_msgs)} mensajes"
                ],
                'difficulty': 'hard'
            })
        
        print(f"   ✓ Generadas {len(suggestions)} sugerencias de preguntas")
        
        return suggestions
    
    def analyze_with_chunks(self, max_workers: int = 4) -> Dict:
        """
        Ejecuta análisis completo usando procesamiento paralelo.
        
        Args:
            max_workers: Número de threads paralelos (default: 4)
        """
        print("\n" + "="*70)
        print("🚀 ANÁLISIS DE MENSAJES CON PROCESAMIENTO EN CHUNKS")
        print("="*70)
        print(f"⚡ Usando {max_workers} workers paralelos\n")
        
        # 1. Cargar mensajes
        all_messages = self.load_all_messages()
        
        # 2. Dividir en chunks
        chunks = self.split_into_chunks(all_messages)
        
        # 3. Procesar chunks en paralelo
        print(f"\n⚙️  Procesando {len(chunks)} chunks en paralelo...")
        chunk_results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todos los chunks a procesar
            future_to_chunk = {
                executor.submit(self.analyze_chunk, chunk, i): i 
                for i, chunk in enumerate(chunks)
            }
            
            # Procesar resultados conforme se completan (con barra de progreso)
            with tqdm(total=len(chunks), desc="Analizando chunks") as pbar:
                for future in as_completed(future_to_chunk):
                    chunk_id = future_to_chunk[future]
                    try:
                        result = future.result()
                        chunk_results.append(result)
                        pbar.update(1)
                    except Exception as e:
                        print(f"\n✗ Error en chunk {chunk_id}: {e}")
        
        print(f"✅ Todos los chunks procesados\n")
        
        # 4. Combinar resultados
        merged_data = self.merge_chunk_results(chunk_results)
        
        # 5. Generar reporte final
        report = self.generate_analysis_report(merged_data)
        
        return report
    
    def save_report(self, report: Dict, output_file: str = None):
        """Guarda reporte en archivo JSON."""
        if output_file is None:
            output_file = "data/message_analysis_chunked.json"
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        print(f"\n💾 Guardando reporte en: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte guardado exitosamente\n")


def print_summary(report: Dict):
    """Imprime resumen visual del análisis."""
    print("\n" + "="*70)
    print("📊 RESUMEN DEL ANÁLISIS")
    print("="*70)
    
    timeline = report['timeline']
    participants = report['participants']
    content = report['content_analysis']
    
    print(f"\n⏰ LÍNEA DE TIEMPO:")
    print(f"   Primer mensaje: {timeline['first_message']['date']}")
    print(f"   Último mensaje: {timeline['last_message']['date']}")
    print(f"   Días conversando: {timeline['days_together']:,}")
    print(f"   Años juntos: {timeline['years_together']}")
    print(f"   Promedio mensajes/día: {timeline['avg_messages_per_day']}")
    
    print(f"\n👥 PARTICIPACIÓN:")
    for name, data in participants.items():
        print(f"   {name}:")
        print(f"      - Mensajes: {data['total_messages']:,}")
        print(f"      - Porcentaje: {data['percentage']}%")
    
    print(f"\n💬 CONTENIDO:")
    print(f"   Palabras únicas: {content['total_unique_words']:,}")
    print(f"   Lugares mencionados: {content['total_location_mentions']:,}")
    print(f"   Fechas mencionadas: {content['total_date_mentions']}")
    
    print(f"\n🏆 TOP 10 PALABRAS MÁS USADAS:")
    for i, word_data in enumerate(content['top_words'][:10], 1):
        print(f"   {i:2d}. {word_data['word']:15s} ({word_data['count']:,} veces)")
    
    print(f"\n💕 TOP 10 APODOS:")
    for i, nick_data in enumerate(content['top_nicknames'][:10], 1):
        print(f"   {i:2d}. {nick_data['nickname']:15s} ({nick_data['count']:,} veces)")
    
    print(f"\n📍 TOP 10 LUGARES:")
    for i, loc_data in enumerate(content['top_locations'][:10], 1):
        print(f"   {i:2d}. {loc_data['location']:15s} ({loc_data['count']:,} menciones)")
    
    print(f"\n💡 SUGERENCIAS DE PREGUNTAS GENERADAS:")
    for i, suggestion in enumerate(report['question_suggestions'], 1):
        print(f"   {i}. [{suggestion['difficulty'].upper()}] {suggestion['question']}")
        print(f"      Categoría: {suggestion['category']}")
        print()


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("💕 ROMANTIC AI - ANALIZADOR DE MENSAJES (CHUNKED)")
    print("   Procesamiento paralelo optimizado para máxima velocidad")
    print("="*70 + "\n")
    
    # Configuración
    conversation_path = "karemramos_1184297046409691"
    
    if not os.path.exists(conversation_path):
        print(f"✗ Error: No se encontró la carpeta {conversation_path}")
        print("\nAsegúrate de estar en la carpeta: romantic_ai_proposal/")
        return
    
    # Configurar parámetros
    print("⚙️  CONFIGURACIÓN:")
    print(f"   📁 Carpeta: {conversation_path}")
    
    try:
        chunk_size_input = input("\n   📦 Tamaño de chunk (default: 5000, presiona ENTER): ").strip()
        chunk_size = int(chunk_size_input) if chunk_size_input else 5000
    except ValueError:
        chunk_size = 5000
    
    try:
        workers_input = input("   ⚡ Workers paralelos (default: 4, presiona ENTER): ").strip()
        max_workers = int(workers_input) if workers_input else 4
    except ValueError:
        max_workers = 4
    
    print(f"\n   ✓ Chunk size: {chunk_size:,} mensajes")
    print(f"   ✓ Workers: {max_workers}")
    
    input("\n🚀 Presiona ENTER para comenzar el análisis...")
    
    # Inicializar analizador
    analyzer = ChunkedMessageAnalyzer(conversation_path, chunk_size=chunk_size)
    
    # Ejecutar análisis
    import time
    start_time = time.time()
    
    report = analyzer.analyze_with_chunks(max_workers=max_workers)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Guardar reporte
    analyzer.save_report(report)
    
    # Mostrar resumen
    print_summary(report)
    
    print("\n" + "="*70)
    print(f"⏱️  TIEMPO DE PROCESAMIENTO: {elapsed:.2f} segundos")
    print("="*70)
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. ✅ Revisa: data/message_analysis_chunked.json")
    print("2. 📝 Usa las sugerencias para crear preguntas en: data/questions.json")
    print("3. 🎨 Personaliza las preguntas con tu toque único")
    print("4. 🤖 Configura el backend con OpenAI API")
    print("5. 🚀 ¡Prueba el chatbot!\n")


if __name__ == "__main__":
    main()
