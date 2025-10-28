"""
Main Flask application for Romantic AI Proposal System.
A personalized chatbot that guides your loved one through a relationship quiz.

Las preguntas se generan dinámicamente usando OpenAI + RAG (Retrieval-Augmented Generation).
"""

import os
import json
import logging
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime
from openai import OpenAI
from services.rag_service import get_rag_service
from prompts.question_generator_prompt import get_question_generator_prompt
from services.chatbot import generate_conversational_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

logger.info("🚀 Iniciando aplicación Flask...")

app = Flask(__name__)
CORS(app)

logger.info("✅ Flask y CORS configurados")

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'

logger.info(f"🔧 Configuración - DEBUG: {app.config['DEBUG']}")

# OpenAI client
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    logger.info("✅ OpenAI API key encontrada")
    openai_client = OpenAI(api_key=openai_api_key)
else:
    logger.error("❌ OpenAI API key NO encontrada!")
    openai_client = None

# RAG Service (inicializado después de cargar mensajes)
rag_service = None
_rag_initialized = False

def ensure_rag_initialized():
    """Asegura que el RAG service esté inicializado."""
    global rag_service, _rag_initialized
    
    if _rag_initialized and rag_service is not None:
        return rag_service
    
    try:
        logger.info("📡 Inicializando RAG Service...")
        print("📡 Inicializando RAG Service...")
        
        # Crear instancia del RAG service
        rag_service = get_rag_service(os.getenv('OPENAI_API_KEY'))
        
        # Cargar mensajes regulares
        all_messages = load_all_messages()
        logger.info(f"📥 {len(all_messages)} mensajes cargados para RAG")
        
        # Cargar chunks prioritarios de transcripción
        from services.spaces_loader import SpacesDataLoader
        spaces_loader = SpacesDataLoader()
        priority_messages = spaces_loader.download_priority_transcription()
        logger.info(f"🎯 {len(priority_messages)} chunks prioritarios cargados")
        
        # Construir índice (o cargar desde cache) con prioridades
        rag_service.build_index(all_messages, force_rebuild=False, priority_messages=priority_messages)
        
        # Mostrar estadísticas
        stats = rag_service.get_statistics()
        logger.info(f"✅ RAG inicializado - Chunks: {stats.get('total_chunks', 0):,}")
        print(f"✅ RAG inicializado - {stats.get('total_chunks', 0):,} chunks")
        
        _rag_initialized = True
        return rag_service
        
    except Exception as e:
        logger.error(f"❌ Error inicializando RAG: {e}")
        print(f"❌ Error inicializando RAG: {e}")
        rag_service = None
        return None

# Conversation data path - resolver ruta absoluta
CONVERSATION_PATH = os.getenv('CONVERSATION_DATA_PATH', '../karemramos_1184297046409691')
# Convertir a ruta absoluta desde la ubicación del script
CONVERSATION_PATH = Path(__file__).parent / CONVERSATION_PATH
CONVERSATION_PATH = CONVERSATION_PATH.resolve()

logger.info(f"📂 Ruta de conversación: {CONVERSATION_PATH}")
print(f"📂 Ruta de conversación: {CONVERSATION_PATH}")

# Global state (in production, use a database)
# Estructura: {session_id: {questions, current_index, answers, etc}}
quiz_sessions = {}


def load_messages_sample(max_messages: int = 1000):
    """Carga una muestra de mensajes para análisis."""
    print(f"📂 Cargando mensajes desde {CONVERSATION_PATH}...")
    
    all_messages = []
    conversation_dir = Path(CONVERSATION_PATH)
    
    # Leer todos los archivos de mensajes
    for msg_file in sorted(conversation_dir.glob('message_*.json')):
        try:
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = data.get('messages', [])
                all_messages.extend(messages)
                
                # Limitar para no cargar todo
                if len(all_messages) >= max_messages:
                    break
        except Exception as e:
            print(f"⚠️  Error leyendo {msg_file.name}: {e}")
    
    # Ordenar por timestamp
    all_messages.sort(key=lambda x: x.get('timestamp_ms', 0))
    
    # Tomar solo los más recientes
    recent_messages = all_messages[-max_messages:] if len(all_messages) > max_messages else all_messages
    
    print(f"✅ {len(recent_messages)} mensajes cargados")
    return recent_messages


def load_all_messages():
    """Carga TODOS los mensajes disponibles para RAG."""
    print(f"📂 Ruta de conversación: {CONVERSATION_PATH}")
    
    all_messages = []
    
    # PRIMERO: Intentar cargar desde DigitalOcean Spaces
    try:
        from services.spaces_loader import load_messages_from_spaces
        print("🌐 Intentando cargar desde DigitalOcean Spaces...")
        
        spaces_messages = load_messages_from_spaces()
        if spaces_messages:
            print(f"✅ {len(spaces_messages)} mensajes cargados desde Spaces")
            return spaces_messages
        else:
            print("⚠️  Spaces no disponible, usando método local...")
            
    except Exception as e:
        print(f"⚠️  Error con Spaces: {e}")
        print("🔄 Continuando con búsqueda local...")
    
    # FALLBACK: Buscar archivos locales
    possible_paths = [
        Path(CONVERSATION_PATH),  # Ruta configurada
        Path("../karemramos_1184297046409691"),  # Relativa desde backend
        Path("./karemramos_1184297046409691"),   # Relativa desde directorio actual
        Path("/workspace/karemramos_1184297046409691"),  # DigitalOcean workspace
        Path(__file__).parent.parent / "karemramos_1184297046409691",  # Desde raíz del proyecto
        Path("../data"),  # Backup en carpeta data desde backend
        Path("./data"),   # Backup en carpeta data desde directorio actual
        Path(__file__).parent.parent / "data"  # Backup en data desde raíz
    ]
    
    conversation_dir = None
    
    # Probar cada ruta posible
    for path in possible_paths:
        print(f"🔍 Probando ruta: {path.resolve()}")
        if path.exists():
            conversation_dir = path
            print(f"✅ Directorio encontrado: {conversation_dir.resolve()}")
            break
    
    if not conversation_dir:
        print("❌ No se encontró el directorio de conversación en ninguna ubicación")
        print("📁 Contenido del directorio actual:")
        current_dir = Path(".")
        for item in current_dir.iterdir():
            print(f"  - {item.name}")
        
        # También mostrar el directorio padre
        print("📁 Contenido del directorio padre:")
        parent_dir = Path("..").resolve()
        try:
            for item in parent_dir.iterdir():
                print(f"  - {item.name}")
        except Exception as e:
            print(f"❌ Error listando directorio padre: {e}")
        
        return []
    
    # Buscar archivos JSON
    json_files = list(conversation_dir.glob('message_*.json'))
    print(f"🔍 Archivos JSON encontrados: {len(json_files)}")
    
    if not json_files:
        print("❌ No se encontraron archivos message_*.json")
        print("📁 Contenido del directorio de conversación:")
        try:
            for item in conversation_dir.iterdir():
                print(f"  - {item.name}")
        except Exception as e:
            print(f"❌ Error listando directorio: {e}")
        return []
    
    # Leer todos los archivos de mensajes
    for msg_file in sorted(json_files):
        try:
            print(f"📖 Leyendo {msg_file.name}...")
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = data.get('messages', [])
                all_messages.extend(messages)
                print(f"  ✅ {len(messages)} mensajes cargados desde {msg_file.name}")
        except Exception as e:
            print(f"⚠️  Error leyendo {msg_file.name}: {e}")
    
    # Agregar archivos adicionales de transcripción e historia
    additional_messages = load_additional_story_files()
    all_messages.extend(additional_messages)
    
    print(f"✅ {len(all_messages)} mensajes totales cargados para RAG")
    return all_messages


def load_additional_story_files():
    """Carga archivos adicionales de historia y transcripción para enriquecer el RAG."""
    additional_messages = []
    
    # Rutas de archivos adicionales
    data_files = [
        "data/historia_completa_transcripcion.txt",
        "data/timeline_estructurado.json"
    ]
    
    base_path = Path(__file__).parent
    
    for file_path in data_files:
        full_path = base_path / file_path
        try:
            if full_path.exists():
                if file_path.endswith('.txt'):
                    # Cargar archivo de texto
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Crear mensaje simulado para RAG
                        additional_messages.append({
                            'sender_name': 'historia_transcripcion',
                            'content': content,
                            'timestamp_ms': int(datetime.now().timestamp() * 1000),
                            'type': 'historia_completa'
                        })
                        print(f"  ✅ Historia completa cargada desde {file_path}")
                        
                elif file_path.endswith('.json'):
                    # Cargar archivo JSON
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convertir JSON a texto para RAG
                        content = json.dumps(data, indent=2, ensure_ascii=False)
                        additional_messages.append({
                            'sender_name': 'timeline_estructurado',
                            'content': content,
                            'timestamp_ms': int(datetime.now().timestamp() * 1000),
                            'type': 'timeline_estructurado'
                        })
                        print(f"  ✅ Timeline estructurado cargado desde {file_path}")
            else:
                print(f"⚠️  Archivo no encontrado: {full_path}")
                
        except Exception as e:
            print(f"⚠️  Error cargando {file_path}: {e}")
    
    return additional_messages


def format_messages_for_ai(messages: list) -> str:
    """Formatea mensajes para enviar a OpenAI."""
    formatted = []
    for msg in messages:
        sender = msg.get('sender_name', 'Unknown')
        content = msg.get('content', '')
        timestamp = msg.get('timestamp_ms', 0)
        
        if content:
            date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            formatted.append(f"[{date}] {sender}: {content}")
    
    return "\n".join(formatted[-200:])  # Últimos 200 mensajes


def generate_single_question_with_openai(messages: list, question_number: int, previous_questions: list = None) -> dict:
    """
    Genera UNA pregunta específica usando OpenAI + RAG.
    Usa búsqueda semántica para encontrar contexto relevante en los mensajes.
    """
    # Asegurar que RAG esté inicializado - OBLIGATORIO, sin fallbacks
    current_rag = ensure_rag_initialized()
    if not current_rag:
        print("❌ RAG service no disponible - no se pueden generar preguntas sin datos reales")
        return None
    
    print(f"🤖 Generando pregunta #{question_number} con OpenAI + RAG...")
    
    # 🔍 PASO 1: Temas ultra específicos para búsqueda contextual profunda
    # CADA TEMA busca contextos únicos e irrepetibles de la relación  
    question_topics = [
        "jajaja risa chistoso gracioso divertido reír humor broma chiste",  # Momentos específicos de humor
        "lugar salir ir vamos fuimos parque casa restaurante cine café",  # Lugares y experiencias específicas
        "comida comer hambre desayuno almuerzo cena pizza hamburguesa",  # Contextos gastronómicos únicos
        "película ver Netflix serie programa televisión película favorita",  # Entertainment específico visto
        "futuro planes casarnos hijos familia sueños juntos siempre",  # Planes concretos mencionados
        "problema enojado pelea discusión triste mal perdón disculpa",  # Conflictos y resoluciones específicas
        "regalo sorpresa detalle especial romántico cumpleaños aniversario",  # Momentos románticos únicos
        "canción música artista bailar escuchar spotify reproducir",  # Referencias musicales específicas
        "amigos familia conocer presentar mamá papá hermana hermano",  # Contextos sociales/familiares
        "primera vez beso te amo inicio conocimos empezamos",  # Hitos relacionales específicos
        "trabajo estudios universidad clase profesor examen tarea",  # Contexto académico/profesional  
        "viaje vacaciones playa montaña ciudad país avión carro",  # Experiencias de viaje específicas
        "enfermo dolor cabeza medicina doctor hospital cuidar",  # Momentos de cuidado mutuo
        "noche dormir sueño despertar mañana tarde madrugada",  # Rutinas y horarios específicos
        "foto selfie imagen bonita hermosa guapo lindo",  # Contextos visuales/estéticos
    ]
    
    # Usar el índice exacto de la pregunta (sin rotar) para variedad
    topic_index = min(question_number - 1, len(question_topics) - 1)
    search_query = question_topics[topic_index]
    
    print(f"🔍 Búsqueda RAG: '{search_query}'...")
    
    # Buscar chunks relevantes
    relevant_chunks = current_rag.search(search_query, k=15)
    
    # Extraer todos los mensajes de los chunks relevantes
    relevant_messages = []
    for chunk in relevant_chunks:
        relevant_messages.extend(chunk['messages_in_chunk'])
    
    print(f"📚 Encontrados {len(relevant_messages)} mensajes relevantes para el tema")
    
    # 📊 PASO 2: ANÁLISIS CONTEXTUAL ULTRA PROFUNDO
    print(f"🔬 Analizando {len(relevant_messages)} mensajes para encontrar contextos únicos e irrepetibles...")
    
    # Filtrar mensajes por calidad y relevancia
    high_quality_messages = []
    for msg in relevant_messages:
        content = msg.get('content', '').strip()
        if len(content) > 10 and len(content) < 300:  # Mensajes de longitud óptima
            high_quality_messages.append(msg)
    
    print(f"📋 {len(high_quality_messages)} mensajes de alta calidad seleccionados para análisis profundo")
    
    # Recopilar todos los mensajes completos para análisis detallado
    detailed_messages = []
    word_frequency = {}
    phrase_patterns = {}
    unique_contexts = {}
    
    for msg in relevant_messages:
        content = msg.get('content', '')
        sender = msg.get('sender_name', 'Unknown')
        timestamp = msg.get('timestamp_ms', 0)
        
        if not content.strip():
            continue
            
        date_str = datetime.fromtimestamp(timestamp / 1000).strftime('%d/%m/%Y %H:%M') if timestamp else 'fecha desconocida'
        
        # Guardar mensaje completo para análisis contextual
        detailed_messages.append({
            'sender': sender,
            'content': content,
            'date': date_str,
            'timestamp': timestamp,
            'length': len(content)
        })
        
        # Análisis de frecuencia de palabras (dinámico)
        words = content.lower().split()
        for word in words:
            if len(word) > 2:  # Ignorar palabras muy cortas
                word_frequency[word] = word_frequency.get(word, 0) + 1
        
        # Detectar patrones de frases (bigramas y trigramas)
        for i in range(len(words) - 1):
            bigram = ' '.join(words[i:i+2])
            phrase_patterns[bigram] = phrase_patterns.get(bigram, 0) + 1
            
        for i in range(len(words) - 2):
            trigram = ' '.join(words[i:i+3])
            phrase_patterns[trigram] = phrase_patterns.get(trigram, 0) + 1
    
    # Filtrar y ordenar por relevancia
    significant_words = {word: count for word, count in word_frequency.items() 
                        if count >= 2 and word not in ['que', 'para', 'con', 'por', 'una', 'del', 'las', 'los', 'pero', 'como', 'más', 'ser', 'hay', 'muy', 'fue', 'sus', 'son', 'ese', 'esa']}
    
    significant_phrases = {phrase: count for phrase, count in phrase_patterns.items() 
                          if count >= 2 and len(phrase.split()) >= 2}
    
    # Ordenar por frecuencia
    top_words = sorted(significant_words.items(), key=lambda x: x[1], reverse=True)[:10]
    top_phrases = sorted(significant_phrases.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"📈 Palabras más frecuentes: {[f'{word}({count})' for word, count in top_words[:5]]}")
    print(f"📈 Frases más frecuentes: {[f'{phrase}({count})' for phrase, count in top_phrases[:3]]}")
    
    # Usar los nuevos datos dinámicos en lugar de hardcodeados
    dynamic_nicknames = top_words  # Las palabras más frecuentes pueden incluir apodos
    dynamic_phrases = top_phrases
    dynamic_locations = [(word, count) for word, count in top_words if any(loc in word for loc in ['casa', 'parque', 'cine', 'restaurante', 'lugar', 'café', 'playa'])]
    
    # 📝 Crear contexto rico con mensajes reales detallados
    # Ordenar mensajes por timestamp para obtener fechas correctas
    sorted_messages = sorted(detailed_messages, key=lambda x: x.get('timestamp', 0))
    first_date = sorted_messages[0]['date'] if sorted_messages else "fecha no disponible"
    last_date = sorted_messages[-1]['date'] if sorted_messages else "fecha no disponible"
    
    # Formatear los mensajes más relevantes para análisis
    examples_text = "\n".join([
        f"- [{msg['date']}] {msg['sender']}: \"{msg['content']}\""
        for msg in detailed_messages[:15]  # Los primeros 15 mensajes más relevantes
    ])
    
    previous_qs = "\n".join([f"- {q.get('question', '')}" for q in (previous_questions or [])]) if previous_questions else "ninguna"
    
    # 🤖 PASO 3: Generar prompt usando análisis dinámico
    prompt = get_question_generator_prompt(
        top_nicknames=dynamic_nicknames,
        top_phrases=dynamic_phrases,
        top_locations=dynamic_locations,
        examples_text=examples_text,
        last_date=last_date,
        previous_qs=previous_qs,
        question_number=question_number
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en crear quizzes románticos personalizados. Respondes SIEMPRE en JSON válido sin formato markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        tokens_used = response.usage.total_tokens
        
        print(f"✅ Pregunta generada ({tokens_used} tokens, ~${tokens_used * 0.000005:.4f})")
        
        # Validar que las opciones no se repitan con preguntas anteriores
        new_options = set(result.get('options', []))
        if previous_questions:
            for prev_q in previous_questions:
                prev_options = set(prev_q.get('options', []))
                overlapping = new_options & prev_options
                if overlapping:
                    print(f"⚠️ ADVERTENCIA: Opciones repetidas detectadas: {overlapping}")
        
        question_data = {
            "question": result.get('question', ''),
            "options": result.get('options', []),
            "correct_answers": result.get('correct_answers', []),
            "hints": result.get('hints', []),
            "success_message": result.get('success_message', 'Correcto.'),
            "category": result.get('category', 'general'),
            "difficulty": result.get('difficulty', 'medium'),
            "data_source": result.get('data_source', 'Datos de conversación')
        }
        
        print(f"📋 Pregunta: {question_data['question']}")
        print(f"🎯 Respuestas correctas: {question_data['correct_answers']}")
        print(f"📊 Fuente: {question_data['data_source']}")
        
        return question_data
    
    except Exception as e:
        print(f"❌ Error generando pregunta con OpenAI: {e}")
        import traceback
        traceback.print_exc()
        
        # Sin fallbacks - retornar None si falla
        print("❌ No se pudo generar pregunta - sin fallbacks disponibles")
        return None


# Health check endpoint for monitoring and Docker
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment verification"""
    logger.info("🔍 Health check endpoint called")
    try:
        current_rag = ensure_rag_initialized()
        rag_enabled = current_rag is not None
        total_messages = len(current_rag.chunk_texts) if current_rag else 0
        
        logger.info(f"✅ Health check successful - RAG: {rag_enabled}, Messages: {total_messages}")
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "rag_enabled": rag_enabled,
            "total_messages": total_messages,
            "environment": os.environ.get('FLASK_ENV', 'development'),
            "port": os.environ.get('BACKEND_PORT', '5000')
        })
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500

def analyze_conversation_data():
    """Analiza los datos reales de conversación cargados"""
    try:
        from services.spaces_loader import load_messages_from_spaces
        
        print("📊 Analizando datos reales de conversación...")
        
        # Intentar cargar mensajes desde Spaces o local
        messages = []
        try:
            messages = load_messages_from_spaces()
            print(f"✅ Mensajes cargados desde Spaces: {len(messages)}")
        except:
            print("⚠️ No se pudieron cargar desde Spaces, usando datos locales...")
            # Cargar desde archivos locales como fallback
            pass
        
        if not messages:
            return None
            
        # ANÁLISIS REAL DE DATOS
        total_messages = len(messages)
        
        # Extraer fechas de los mensajes
        dates = []
        message_times = []
        senders = {}
        content_analysis = {
            'total_chars': 0,
            'romantic_keywords': 0,
            'emojis': {},
            'longest_message': 0,
            'conversations_by_date': {}
        }
        
        for msg in messages:
            try:
                # Análisis de fecha y hora
                if 'timestamp_ms' in msg:
                    timestamp = datetime.fromtimestamp(msg['timestamp_ms'] / 1000)
                    dates.append(timestamp)
                    message_times.append(timestamp.hour)
                    date_key = timestamp.strftime('%Y-%m')
                    content_analysis['conversations_by_date'][date_key] = content_analysis['conversations_by_date'].get(date_key, 0) + 1
                
                # Análisis de remitente
                sender = msg.get('sender_name', 'Unknown')
                senders[sender] = senders.get(sender, 0) + 1
                
                # Análisis de contenido
                content = msg.get('content', '')
                if content:
                    content_analysis['total_chars'] += len(content)
                    content_analysis['longest_message'] = max(content_analysis['longest_message'], len(content))
                    
                    # Buscar palabras románticas
                    romantic_words = ['amor', 'te amo', 'mi vida', 'corazón', 'besitos', 'hermosa', 'princesa', 'mi amor', 'baby', 'cariño']
                    content_lower = content.lower()
                    for word in romantic_words:
                        if word in content_lower:
                            content_analysis['romantic_keywords'] += 1
                    
                    # Contar emojis
                    import re
                    emoji_pattern = re.compile("["
                        "\U0001F600-\U0001F64F"  # emoticons
                        "\U0001F300-\U0001F5FF"  # symbols & pictographs
                        "\U0001F680-\U0001F6FF"  # transport & map symbols
                        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "\U00002702-\U000027B0"
                        "\U000024C2-\U0001F251"
                        "]+", flags=re.UNICODE)
                    
                    emojis_found = emoji_pattern.findall(content)
                    for emoji in emojis_found:
                        content_analysis['emojis'][emoji] = content_analysis['emojis'].get(emoji, 0) + 1
                        
            except Exception as e:
                print(f"Error procesando mensaje: {e}")
                continue
        
        # Calcular estadísticas
        if dates:
            dates.sort()
            total_days = (dates[-1] - dates[0]).days + 1
            avg_messages_per_day = round(total_messages / total_days, 1) if total_days > 0 else 0
            
            # Hora más activa
            most_active_hour = max(set(message_times), key=message_times.count) if message_times else 12
            
            # Score de sentimiento basado en palabras románticas
            sentiment_score = min(10, round((content_analysis['romantic_keywords'] / total_messages) * 100 + 5, 1))
            
            # Top emojis
            top_emojis = sorted(content_analysis['emojis'].items(), key=lambda x: x[1], reverse=True)[:5]
            top_emojis_list = [emoji[0] for emoji in top_emojis] if top_emojis else ['❤', '�', '💜']
            
            # Fases de la relación basadas en datos reales
            monthly_data = sorted(content_analysis['conversations_by_date'].items())
            phases = []
            if len(monthly_data) >= 3:
                third = len(monthly_data) // 3
                # Forzar que el inicio sea marzo 2025
                start_period = "2025-03"
                phases = [
                    {
                        "phase": "Inicio",
                        "messages": sum([monthly_data[i][1] for i in range(third)]),
                        "period": f"{start_period} - {monthly_data[third-1][0]}"
                    },
                    {
                        "phase": "Creciendo", 
                        "messages": sum([monthly_data[i][1] for i in range(third, third*2)]),
                        "period": f"{monthly_data[third][0]} - {monthly_data[third*2-1][0]}"
                    },
                    {
                        "phase": "Consolidación",
                        "messages": sum([monthly_data[i][1] for i in range(third*2, len(monthly_data))]),
                        "period": f"{monthly_data[third*2][0]} - {monthly_data[-1][0]}"
                    }
                ]
            
            return {
                "totalMessages": total_messages,
                "totalDays": total_days,
                "avgMessagesPerDay": avg_messages_per_day,
                "longestConversation": content_analysis['longest_message'],
                "mostActiveHour": most_active_hour,
                "sentimentScore": sentiment_score,
                "relationshipPhases": phases,
                "topEmojis": top_emojis_list,
                "specialMoments": content_analysis['romantic_keywords'],
                "senderDistribution": senders,
                "totalChars": content_analysis['total_chars'],
                "firstMessage": dates[0].strftime('%Y-%m-%d') if dates else None,
                "lastMessage": dates[-1].strftime('%Y-%m-%d') if dates else None
            }
        
        return None
        
    except Exception as e:
        print(f"Error en análisis: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/api/relationship-stats', methods=['GET'])
def get_relationship_stats():
    """Generate relationship statistics from real conversation data (with enhanced AI analysis)"""
    try:
        # Verificar si se solicita análisis forzado
        force_analysis = request.args.get('force', 'false').lower() == 'true'
        
        # 🚀 OPTIMIZACIÓN: Intentar cargar desde cache primero (si no es forzado)
        if not force_analysis:
            from services.stats_cache import get_stats_cache
            stats_cache = get_stats_cache()
            
            # Verificar cache mejorado primero
            enhanced_cache_file = Path("../cache/enhanced_relationship_stats.json")
            if enhanced_cache_file.exists():
                try:
                    with open(enhanced_cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cached_at = datetime.fromisoformat(cache_data.get('cached_at', ''))
                    age_hours = (datetime.now() - cached_at).total_seconds() / 3600
                    
                    if age_hours <= 24:  # Cache válido por 24 horas
                        enhanced_stats = cache_data.get('stats', {})
                        enhanced_stats["cache_hit"] = True
                        enhanced_stats["cache_age_hours"] = round(age_hours, 1)
                        print(f"⚡ Estadísticas mejoradas servidas desde cache ({age_hours:.1f}h)")
                        return jsonify(enhanced_stats)
                except Exception as e:
                    print(f"⚠️ Error leyendo cache mejorado: {e}")
            
            # Verificar cache tradicional
            cached_stats = stats_cache.get_cached_stats()
            if cached_stats:
                cached_stats["generated_at"] = datetime.now().isoformat()
                cached_stats["data_source"] = "cached_analysis"
                cached_stats["cache_hit"] = True
                print("⚡ Estadísticas tradicionales servidas desde cache")
                return jsonify(cached_stats)
        
        # Usar análisis mejorado con IA
        print("🤖 Ejecutando análisis mejorado con IA...")
        try:
            # Importar y ejecutar el analizador mejorado
            sys.path.append('..')
            from enhanced_stats_analyzer import EnhancedStatsAnalyzer
            
            analyzer = EnhancedStatsAnalyzer()
            enhanced_stats = analyzer.generate_enhanced_stats()
            
            if enhanced_stats:
                enhanced_stats["cache_hit"] = False
                enhanced_stats["analysis_type"] = "enhanced_ai_powered"
                print("✅ Análisis mejorado completado")
                return jsonify(enhanced_stats)
                
        except ImportError as e:
            print(f"⚠️ No se pudo importar analizador mejorado: {e}")
        except Exception as e:
            print(f"⚠️ Error en análisis mejorado: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback al análisis tradicional
        print("📊 Fallback a análisis tradicional...")
        real_stats = analyze_conversation_data()
        
        if real_stats:
            real_stats["generated_at"] = datetime.now().isoformat()
            real_stats["data_source"] = "traditional_analysis"
            real_stats["cache_hit"] = False
            current_rag = ensure_rag_initialized()
            if current_rag and hasattr(current_rag, 'chunk_texts'):
                real_stats["rag_chunks"] = len(current_rag.chunk_texts)
            
            return jsonify(real_stats)
        
        # Fallback final: estimación basada en RAG
        current_rag = ensure_rag_initialized()
        if current_rag and hasattr(current_rag, 'chunk_texts'):
            total_chunks = len(current_rag.chunk_texts)
            estimated_messages = total_chunks * 5
            
            fallback_stats = {
                "totalMessages": estimated_messages,
                "totalDays": 800,
                "avgMessagesPerDay": round(estimated_messages / 800, 1),
                "connectionScore": 8.5,
                "avgResponseTime": "15min",
                "relationshipPhases": [
                    {"phase": "Inicio", "messages": int(estimated_messages * 0.2), "period": "Primeros meses"},
                    {"phase": "Creciendo", "messages": int(estimated_messages * 0.4), "period": "Desarrollo"},
                    {"phase": "Consolidación", "messages": int(estimated_messages * 0.4), "period": "Actualidad"}
                ],
                "topEmojis": ['❤️', '😘', '💜', '😍', '🥰'],
                "specialMoments": int(estimated_messages * 0.05),
                "generated_at": datetime.now().isoformat(),
                "data_source": "rag_estimation_fallback",
                "cache_hit": False,
                "rag_chunks": total_chunks
            }
            
            return jsonify(fallback_stats)
        
        # Sin datos disponibles
        return jsonify({
            "error": "No conversation data available",
            "message": "No analysis method succeeded"
        }), 503
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "data_source": "error_fallback"
        }), 500

@app.route('/api/relationship-stats/regenerate', methods=['POST'])
def regenerate_relationship_stats():
    """Fuerza la regeneración de estadísticas con análisis mejorado"""
    try:
        print("🔄 Forzando regeneración de estadísticas mejoradas...")
        
        # Importar y ejecutar el analizador mejorado
        sys.path.append('..')
        from enhanced_stats_analyzer import EnhancedStatsAnalyzer
        
        analyzer = EnhancedStatsAnalyzer()
        enhanced_stats = analyzer.generate_enhanced_stats()
        
        if enhanced_stats:
            enhanced_stats["cache_hit"] = False
            enhanced_stats["regenerated_at"] = datetime.now().isoformat()
            enhanced_stats["analysis_type"] = "enhanced_ai_forced_regeneration"
            
            # Limpiar cache antiguo
            try:
                from services.stats_cache import get_stats_cache
                stats_cache = get_stats_cache()
                stats_cache.clear_cache()
                print("🗑️ Cache anterior limpiado")
            except:
                pass
            
            print("✅ Estadísticas regeneradas exitosamente")
            return jsonify({
                "success": True,
                "message": "Estadísticas regeneradas con análisis mejorado",
                "stats": enhanced_stats
            })
        else:
            return jsonify({
                "success": False,
                "error": "No se pudieron generar estadísticas mejoradas"
            }), 500
            
    except Exception as e:
        print(f"❌ Error regenerando estadísticas: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error durante la regeneración de estadísticas"
        }), 500


@app.route('/api/cache/stats-info', methods=['GET'])
def get_stats_cache_info():
    """Obtiene información del cache de estadísticas"""
    try:
        from services.stats_cache import get_stats_cache
        stats_cache = get_stats_cache()
        
        cache_info = stats_cache.get_cache_info()
        return jsonify({
            "cache_info": cache_info,
            "success": True
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/cache/clear-stats', methods=['POST'])
def clear_stats_cache():
    """Limpia el cache de estadísticas para forzar recálculo"""
    try:
        from services.stats_cache import get_stats_cache
        stats_cache = get_stats_cache()
        
        stats_cache.clear_cache()
        return jsonify({
            "message": "Cache de estadísticas limpiado",
            "success": True
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/start', methods=['POST'])
@app.route('/api/start-quiz', methods=['POST'])  # Alias para compatibilidad con frontend
def start_quiz():
    """
    Initialize a new quiz session and generate the first question.
    
    Expected JSON body:
    {
        "user_name": "Karem",
        "total_questions": 7
    }
    
    Returns:
    {
        "success": true,
        "session_id": "uuid",
        "message": "Greeting + first question",
        "options": ["opt1", "opt2", ...],
        "current_question": 1,
        "total_questions": 7
    }
    """
    global rag_service
    
    data = request.get_json()
    user_name = data.get('user_name', 'Mi Amor')
    total_questions = data.get('total_questions', 7)
    
    # Create new session
    session_id = str(uuid.uuid4())
    
    print(f"\n{'='*60}")
    print(f"🎯 Nueva sesión iniciada: {session_id}")
    print(f"{'='*60}")
    
    # Asegurar que RAG esté inicializado
    current_rag = ensure_rag_initialized()
    if not current_rag:
        return jsonify({
            "success": False,
            "error": "No se pudo inicializar el sistema RAG. Verifique la configuración."
        }), 500
    
    # 🤖 Generar primera pregunta con OpenAI + RAG
    print(f"🤖 Generando pregunta #1 para {user_name}...")
    
    # Obtener mensajes de muestra para contexto inicial (ya no necesario con RAG, pero lo dejamos por compatibilidad)
    messages_sample = []
    
    first_question = generate_single_question_with_openai(
        messages_sample,
        question_number=1,
        previous_questions=None
    )
    
    if not first_question or not first_question.get('question'):
        return jsonify({
            "success": False,
            "error": "No se pudo generar la primera pregunta. Sistema RAG requerido para preguntas personalizadas."
        }), 500
    
    # Inicializar sesión
    quiz_sessions[session_id] = {
        "user_name": user_name,
        "total_questions": total_questions,
        "questions_asked": [first_question],
        "current_question_index": 0,
        "correct_answers": 0,
        "questions_skipped": 0,
        "attempts_current_question": 0,
        "max_attempts_per_question": 3,
        "hints_used": 0,
        "answers_history": [],
        "messages": messages_sample,
        "completed": False,
        "started_at": datetime.now().isoformat()
    }
    
    greeting = (
        f"Hola {user_name}.\n\n"
        f"He preparado {total_questions} preguntas basadas en nuestras conversaciones. "
        f"Al completarlas, tengo algo que decirte.\n\n"
        f"Pregunta 1 de {total_questions}:\n\n"
        f"{first_question['question']}"
    )
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "message": greeting,
        "question": first_question['question'],  # Para frontend
        "options": first_question.get('options', []),
        "current_question": 1,
        "total_questions": total_questions,
        "attempts_left": 3
    })


@app.route('/api/answer', methods=['POST'])
@app.route('/api/chat', methods=['POST'])  # Alias para compatibilidad con frontend
def answer_question():
    """
    Process user's answer to the current question.
    
    Expected JSON body:
    {
        "session_id": "uuid",
        "message": "user's answer"
    }
    
    Returns:
    {
        "success": true,
        "message": "feedback + next question OR completion message",
        "options": [...] (if there's a next question),
        "current_question": number,
        "total_questions": number,
        "correct_answers": number,
        "is_correct": boolean,
        "completed": boolean
    }
    """
    data = request.get_json()
    session_id = data.get('session_id')
    user_message = data.get('message', '').strip().lower()
    
    if not session_id or session_id not in quiz_sessions:
        return jsonify({
            "success": False,
            "error": "Invalid session ID"
        }), 400
    
    session = quiz_sessions[session_id]
    
    if session['completed']:
        return jsonify({
            "success": False,
            "error": "Quiz already completed"
        }), 400
    
    current_index = session['current_question_index']
    questions_asked = session['questions_asked']
    total_questions = session['total_questions']
    
    # Get current question
    if current_index >= len(questions_asked):
        return jsonify({
            "success": False,
            "error": "No current question available"
        }), 400
    
    current_question = questions_asked[current_index]
    correct_answers = current_question.get('correct_answers', [])
    
    # Check if answer is correct (case-insensitive, flexible matching)
    is_correct = any(
        correct.lower() in user_message or user_message in correct.lower()
        for correct in correct_answers
    )
    
    if is_correct:
        # ✅ RESPUESTA CORRECTA
        session['correct_answers'] += 1
        session['attempts_current_question'] = 0
        session['answers_history'].append({
            'question': current_question.get('question', ''),
            'answer': user_message,
            'correct': True,
            'attempts': session['attempts_current_question']
        })
        
        print(f"✅ Respuesta correcta! Total: {session['correct_answers']}/{total_questions}")
        
        # 🎉 CHECK IF QUIZ COMPLETED
        if session['correct_answers'] >= total_questions:
            session['completed'] = True
            
            # 🤖 Generar mensaje de completación conversacional con OpenAI
            try:
                from services.chatbot import generate_completion_message
                completion_message = generate_completion_message(
                    openai_client=openai_client,
                    session_info={
                        'correct_answers': session['correct_answers'],
                        'total_questions': total_questions,
                        'current_question': current_index + 1
                    },
                    rag_service=rag_service
                )
            except Exception as e:
                print(f"❌ Error generando mensaje de completación: {e}")
                return jsonify({
                    "success": False,
                    "error": "No se pudo generar mensaje de completación personalizado.",
                    "completed": True
                }), 500
            
            return jsonify({
                "success": True,
                "message": completion_message,
                "completed": True,
                "is_correct": True,
                "options": []
            })
        
        # 🤖 GENERAR SIGUIENTE PREGUNTA
        next_question_number = current_index + 2
        print(f"🤖 Generando pregunta #{next_question_number}...")
        
        next_question = generate_single_question_with_openai(
            session['messages'],
            question_number=next_question_number,
            previous_questions=questions_asked
        )
        
        if not next_question or not next_question.get('question'):
            # Sin fallbacks - finalizar quiz si no se puede generar siguiente pregunta
            session['completed'] = True
            return jsonify({
                "success": False,
                "error": "No se pudo generar la siguiente pregunta. Quiz finalizado.",
                "completed": True,
                "message": "El quiz ha terminado debido a problemas técnicos."
            }), 500
        
        session['questions_asked'].append(next_question)
        session['current_question_index'] += 1
        
        # 🤖 Generar respuesta conversacional para respuesta correcta
        try:
            conversational_response = generate_conversational_response(
                openai_client=openai_client,
                context="",
                user_answer=user_message,
                is_correct=True,
                question_info=current_question,
                session_info={
                    'current_question': current_index + 1,
                    'total_questions': total_questions,
                    'correct_answers': session['correct_answers']
                },
                rag_service=rag_service
            )
            
            # Generar introducción para la siguiente pregunta
            from services.chatbot import generate_next_question_intro
            question_intro = generate_next_question_intro(
                openai_client=openai_client,
                next_question=next_question,
                session_info={
                    'current_question': current_index + 1,
                    'total_questions': total_questions,
                    'correct_answers': session['correct_answers']
                }
            )
            
            response_message = f"{conversational_response}\n\n{question_intro}\n\n{next_question['question']}"
            
        except Exception as e:
            print(f"❌ Error generando respuesta conversacional: {e}")
            return jsonify({
                "success": False,
                "error": "No se pudo generar respuesta conversacional personalizada.",
                "completed": True
            }), 500
        
        return jsonify({
            "success": True,
            "message": response_message,
            "options": next_question.get('options', []),
            "current_question": next_question_number,
            "total_questions": total_questions,
            "correct_answers": session['correct_answers'],
            "is_correct": True,
            "completed": False,
            "attempts_left": 3
        })
    
    else:
        # ❌ RESPUESTA INCORRECTA
        session['attempts_current_question'] += 1
        attempts = session['attempts_current_question']
        max_attempts = session.get('max_attempts_per_question', 3)
        attempts_left = max_attempts - attempts
        
        print(f"❌ Respuesta incorrecta. Intento {attempts}/{max_attempts}")
        
        # 🤖 Generar respuesta conversacional para respuesta incorrecta
        try:
            conversational_response = generate_conversational_response(
                openai_client=openai_client,
                context="",
                user_answer=user_message,
                is_correct=False,
                question_info=current_question,
                session_info={
                    'current_question': current_index + 1,
                    'total_questions': total_questions,
                    'correct_answers': session['correct_answers']
                },
                rag_service=rag_service
            )
        except Exception as e:
            print(f"❌ Error generando respuesta conversacional: {e}")
            correct_answer = current_question.get('correct_answers', ['la respuesta correcta'])[0]
            conversational_response = f"No exactamente, mi amor. La respuesta correcta era: {correct_answer} 💕"
        
        # Obtener pista si hay disponible
        hints = current_question.get('hints', [])
        hint_text = ""
        if attempts > 0 and attempts <= len(hints):
            hint_text = f"\n\n💡 Pista: {hints[attempts - 1]}"
        
        # Verificar si agotó los 3 intentos
        if attempts >= max_attempts:
            # ⚠️ AGOTÓ LOS INTENTOS - Cambiar de pregunta
            print(f"⚠️ Agotó los {max_attempts} intentos. Cambiando de pregunta...")
            
            session['questions_skipped'] += 1
            session['attempts_current_question'] = 0
            session['answers_history'].append({
                'question': current_question.get('question', ''),
                'answer': user_message,
                'correct': False,
                'attempts': attempts,
                'skipped': True
            })
            
            # Verificar si aún puede completar el quiz
            questions_remaining = total_questions - (session['correct_answers'] + session['questions_skipped'])
            
            if questions_remaining <= 0:
                # No puede completar el quiz
                session['completed'] = True
                return jsonify({
                    "success": True,
                    "message": "Has agotado los intentos disponibles.\n\nPuedes intentarlo de nuevo cuando gustes.",
                    "completed": True,
                    "is_correct": False,
                    "options": []
                })
            
            # 🤖 GENERAR NUEVA PREGUNTA (reemplazo)
            next_question_number = len(questions_asked) + 1
            print(f"🤖 Generando pregunta de reemplazo #{next_question_number}...")
            
            new_question = generate_single_question_with_openai(
                session['messages'],
                question_number=next_question_number,
                previous_questions=questions_asked
            )
            
            if not new_question or not new_question.get('question'):
                # Sin fallbacks - finalizar quiz
                session['completed'] = True
                return jsonify({
                    "success": False,
                    "error": "No se pudo generar pregunta de reemplazo. Quiz finalizado.",
                    "completed": True
                }), 500
            
            session['questions_asked'].append(new_question)
            session['current_question_index'] += 1
            
            response_message = (
                f"Probemos con otra pregunta.\n\n"
                f"Pregunta {next_question_number} de {total_questions}:\n\n"
                f"{new_question['question']}"
            )
            
            return jsonify({
                "success": True,
                "message": response_message,
                "options": new_question.get('options', []),
                "current_question": next_question_number,
                "total_questions": total_questions,
                "correct_answers": session['correct_answers'],
                "is_correct": False,
                "completed": False,
                "attempts_left": 3,
                "question_skipped": True
            })
        
        # 💡 DAR PISTA (aún tiene intentos)
        hints = current_question.get('hints', [])
        
        # Obtener la pista correcta según el intento
        if hints and len(hints) >= attempts:
            hint = hints[attempts - 1]  # Primera pista en intento 1, segunda en intento 2
        else:
            hint = "Piensa en nuestros momentos especiales... 💭"
        
        session['hints_used'] += 1
        
        response_message = f"{conversational_response}{hint_text}\n\n¡Te quedan {attempts_left} intentos!"
        
        # MANTENER LAS OPCIONES VISIBLES
        return jsonify({
            "success": True,
            "message": response_message,
            "options": current_question.get('options', []),  # ✅ Opciones siguen visibles
            "current_question": current_index + 1,
            "total_questions": total_questions,
            "correct_answers": session['correct_answers'],
            "is_correct": False,
            "completed": False,
            "attempts_left": attempts_left,
            "hint_given": True
        })


@app.route('/api/get-location', methods=['POST'])
def get_location():
    """
    Reveal final location (only after all questions answered correctly).
    
    Expected JSON body:
    {
        "session_id": "uuid"
    }
    """
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in quiz_sessions:
        return jsonify({
            "success": False,
            "error": "Invalid session ID"
        }), 400
    
    session = quiz_sessions[session_id]
    
    if not session['completed']:
        return jsonify({
            "success": False,
            "error": "Complete all questions first"
        }), 403
    
    final_location = {
        "latitude": float(os.getenv('FINAL_LATITUDE', 19.4326)),
        "longitude": float(os.getenv('FINAL_LONGITUDE', -99.1332)),
        "address": os.getenv('FINAL_ADDRESS', 'Te espero en un lugar especial'),
        "message": (
            f"Karem Kiyomi Ramos,\n\n"
            "Has demostrado que conoces bien nuestra historia. "
            "Ahora, ¿podrías venir a este lugar? "
            "Hay algo importante que quiero preguntarte."
        )
    }
    
    return jsonify({
        "success": True,
        **final_location
    })


if __name__ == '__main__':
    # 🚀 Inicializar RAG Service al inicio
    print("\n" + "="*60)
    print("🚀 Inicializando Romantic AI Proposal System v3.0 - Dashboard Edition")
    print("="*60)
    print(f"🏷️  Build: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Cargar todos los mensajes
        logger.info("📥 Cargando mensajes...")
        all_messages = load_all_messages()
        logger.info(f"✅ {len(all_messages)} mensajes cargados")
        
        # Inicializar RAG
        logger.info("📡 Inicializando RAG Service...")
        print("\n📡 Inicializando RAG Service...")
        rag_service = get_rag_service(os.getenv('OPENAI_API_KEY'))
        logger.info("✅ RAG Service creado")
        
        # Construir índice (o cargar desde cache)
        logger.info("🔨 Construyendo índice RAG...")
        rag_service.build_index(all_messages, force_rebuild=False)
        logger.info("✅ Índice RAG construido")
        
        # Mostrar estadísticas
        stats = rag_service.get_statistics()
        logger.info(f"📊 RAG Stats - Chunks: {stats.get('total_chunks', 0):,}")
        print("\n📊 Estadísticas del RAG:")
        print(f"  - Total chunks: {stats.get('total_chunks', 0):,}")
        print(f"  - Total mensajes: {stats.get('total_messages', 0):,}")
        print(f"  - Total vectores: {stats.get('total_vectors', 0):,}")
        print(f"  - Modelo embeddings: {stats.get('embedding_model', 'N/A')}")
        print(f"  - Dimensión: {stats.get('embedding_dimension', 0)}")
        print(f"  - Tamaño índice: {stats.get('index_size_mb', 0):.2f} MB")
        print(f"  - Cache existe: {'✅' if stats.get('cache_exists', False) else '❌'}")
        
        print("\n" + "="*60)
        print("✅ Sistema inicializado correctamente")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error inicializando sistema: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  El sistema continuará sin RAG, usando método básico.")
    
    # Iniciar servidor
    # DigitalOcean usa puerto 8080 por defecto para health checks
    port = int(os.getenv('PORT', os.getenv('BACKEND_PORT', 8080)))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"🌐 Servidor iniciando en http://{host}:{port}")
    logger.info(f"🔧 Modo debug: {app.config['DEBUG']}")
    logger.info(f"🔑 OpenAI API configurado: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    
    print(f"\n🌐 Servidor iniciando en http://{host}:{port}")
    print(f"🔧 Modo debug: {app.config['DEBUG']}")
    print(f"🔑 OpenAI API configurado: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        logger.warning("⚠️ OpenAI API Key no configurado correctamente")
        print("⚠️  ADVERTENCIA: OpenAI API Key no configurado correctamente")
        print("   Configura OPENAI_API_KEY en el archivo .env")
    
    # Usar servidor de producción si no estamos en debug
    if app.config['DEBUG']:
        logger.info("🔧 Iniciando servidor de desarrollo...")
        app.run(host=host, port=port, debug=True)
    else:
        # En producción, usar waitress (servidor WSGI más robusto)
        logger.info("🚀 Iniciando servidor de producción con Waitress...")
        print("🚀 Iniciando servidor de producción con Waitress...")
        try:
            from waitress import serve
            serve(app, host=host, port=port, threads=4)
        except ImportError:
            logger.warning("⚠️ Waitress no disponible, usando servidor Flask")
            print("⚠️ Waitress no disponible, usando servidor Flask")
            app.run(host=host, port=port, debug=False, threaded=True)