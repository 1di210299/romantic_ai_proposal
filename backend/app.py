"""
Main Flask application for Romantic AI Proposal System.
A personalized chatbot that guides your loved one through a relationship quiz.

Las preguntas se generan dinámicamente usando OpenAI + RAG (Retrieval-Augmented Generation).
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime
from openai import OpenAI
from services.rag_service import get_rag_service
from prompts.question_generator_prompt import get_question_generator_prompt

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'

# OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# RAG Service (inicializado después de cargar mensajes)
rag_service = None

# Conversation data path - resolver ruta absoluta
CONVERSATION_PATH = os.getenv('CONVERSATION_DATA_PATH', '../karemramos_1184297046409691')
# Convertir a ruta absoluta desde la ubicación del script
CONVERSATION_PATH = Path(__file__).parent / CONVERSATION_PATH
CONVERSATION_PATH = CONVERSATION_PATH.resolve()

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
    """Carga TODOS los mensajes para el RAG (sin límite)."""
    print(f"📂 Cargando TODOS los mensajes desde {CONVERSATION_PATH} para RAG...")
    
    all_messages = []
    conversation_dir = Path(CONVERSATION_PATH)
    
    for msg_file in sorted(conversation_dir.glob('message_*.json')):
        try:
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = data.get('messages', [])
                all_messages.extend(messages)
        except Exception as e:
            print(f"⚠️  Error leyendo {msg_file.name}: {e}")
    
    # Ordenar por timestamp
    all_messages.sort(key=lambda x: x.get('timestamp_ms', 0))
    
    print(f"✅ {len(all_messages):,} mensajes totales cargados para RAG")
    return all_messages


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
    global rag_service
    
    print(f"🤖 Generando pregunta #{question_number} con OpenAI + RAG...")
    
    # 🔍 PASO 1: Usar RAG para encontrar mensajes relevantes según el tipo de pregunta
    # TEMAS DIVERSOS Y GENERALES para preguntas variadas sobre la relación
    question_topics = [
        "momento gracioso risa divertido chistoso",  # Pregunta 1 - Momentos divertidos
        "viaje vacaciones salir pasear lugar",  # Pregunta 2 - Viajes y lugares
        "comida favorita comer restaurante pizza",  # Pregunta 3 - Gustos/comida
        "película serie Netflix ver juntos película favorita",  # Pregunta 4 - Entretenimiento
        "sueño futuro planes juntos casarnos hijos",  # Pregunta 5 - Planes futuros
        "pelea enojado discusión problema perdón",  # Pregunta 6 - Superación/conflictos
        "sorpresa regalo detalle especial romántico",  # Pregunta 7 - Detalles románticos
        "música canción artista bailar escuchar",  # Pregunta 8 - Música
        "familia amigos conocer presentar",  # Pregunta 9 - Familia/social
        "primera vez conocimos beso te amo",  # Pregunta 10 - Primeras veces
    ]
    
    # Usar el índice exacto de la pregunta (sin rotar) para variedad
    topic_index = min(question_number - 1, len(question_topics) - 1)
    search_query = question_topics[topic_index]
    
    print(f"🔍 Búsqueda RAG: '{search_query}'...")
    
    # Buscar chunks relevantes
    relevant_chunks = rag_service.search(search_query, k=15)
    
    # Extraer todos los mensajes de los chunks relevantes
    relevant_messages = []
    for chunk in relevant_chunks:
        relevant_messages.extend(chunk['messages_in_chunk'])
    
    print(f"📚 Encontrados {len(relevant_messages)} mensajes relevantes para el tema")
    
    # 📊 PASO 2: Analizar los mensajes relevantes para extraer datos
    dates = []
    romantic_locations = []
    nicknames = set()
    romantic_phrases = []
    nickname_counts = {}
    phrase_counts = {}
    location_counts = {}
    message_examples = []
    
    for msg in relevant_messages:
        # Fechas específicas
        if msg.get('timestamp_ms'):
            date = datetime.fromtimestamp(msg['timestamp_ms'] / 1000).strftime('%d de %B de %Y')
            dates.append(date)
        
        content = msg.get('content', '').lower()
        sender = msg.get('sender_name', 'Unknown')
        
        # Guardar ejemplos literales de mensajes relevantes
        if len(message_examples) < 20:
            message_examples.append({
                'sender': sender,
                'content': msg.get('content', '')[:150],
                'date': datetime.fromtimestamp(msg['timestamp_ms'] / 1000).strftime('%d/%m/%Y') if msg.get('timestamp_ms') else 'unknown'
            })
        
        # Apodos y términos cariñosos - CONTAR FRECUENCIA
        terms = ['amor', 'bebe', 'bb', 'mi vida', 'corazon', 'cielo', 'chapo', 'chapozita', 
                 'princesa', 'rey', 'reina', 'tesoro', 'cariño', 'mi todo', 'mi mundo']
        for term in terms:
            if term in content:
                nicknames.add(term)
                nickname_counts[term] = nickname_counts.get(term, 0) + 1
        
        # Frases románticas - CONTAR FRECUENCIA
        romantic_keywords = ['te amo', 'te quiero', 'te extraño', 'te necesito', 'mi amor', 
                            'siempre juntos', 'para siempre', 'eres todo', 'eres mi vida']
        for keyword in romantic_keywords:
            if keyword in content:
                romantic_phrases.append(keyword)
                phrase_counts[keyword] = phrase_counts.get(keyword, 0) + 1
        
        # Lugares ROMÁNTICOS - CONTAR FRECUENCIA
        places = ['parque', 'playa', 'cine', 'restaurante', 'nuestra casa', 'nuestro lugar',
                  'mirador', 'café']
        for place in places:
            if place in content:
                romantic_locations.append(place)
                location_counts[place] = location_counts.get(place, 0) + 1
    
    # Ordenar por frecuencia (más usados primero)
    top_nicknames = sorted(nickname_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # 📝 Crear contexto rico con datos reales
    first_date = dates[0] if dates else "fecha no disponible"
    last_date = dates[-1] if dates else "fecha no disponible"
    
    # Formatear ejemplos literales
    examples_text = "\n".join([
        f"- [{ex['date']}] {ex['sender']}: \"{ex['content']}\""
        for ex in message_examples
    ])
    
    previous_qs = "\n".join([f"- {q.get('question', '')}" for q in (previous_questions or [])]) if previous_questions else "ninguna"
    
    # 🤖 PASO 3: Generar prompt usando el módulo separado
    prompt = get_question_generator_prompt(
        top_nicknames=top_nicknames,
        top_phrases=top_phrases,
        top_locations=top_locations,
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
            "success_message": result.get('success_message', '¡Correcto! 💕'),
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
        
        # Fallback: pregunta genérica si falla la IA
        return {
            "question": "¿Cuál es uno de los apodos cariñosos que usamos?",
            "options": ["amor", "cielo", "vida", "corazón"],
            "correct_answers": ["amor", "mi amor"],
            "hints": ["Lo digo muy seguido...", "Es el más común...", "A-M-O-R"],
            "success_message": "¡Sí! 'Amor' es nuestro apodo especial 💕",
            "category": "apodos",
            "difficulty": "easy",
            "data_source": "Fallback: pregunta genérica"
        }


# Health check endpoint for monitoring and Docker
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check if OpenAI API key is configured
        api_key_status = "configured" if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here' else "missing"
        
        # Check if RAG service is initialized
        rag_status = "initialized" if rag_service else "not_initialized"
        
        # Check if conversation data exists
        data_status = "found" if CONVERSATION_PATH.exists() else "missing"
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "openai_api": api_key_status,
            "rag_service": rag_status,
            "conversation_data": data_status,
            "active_sessions": len(quiz_sessions)
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
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
    
    # Verificar que RAG esté inicializado
    if not rag_service:
        return jsonify({
            "success": False,
            "error": "El sistema RAG no está inicializado. Reinicie el servidor."
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
        first_question = {
            "question": "¿Cuál es el apodo que más uso para llamarte?",
            "options": ["amor", "cielo", "vida", "bebé"],
            "correct_answers": ["amor", "mi amor"],
            "hints": ["Lo digo muy seguido...", "Es el más común...", "A-M-O-R"],
            "success_message": "¡Sí! 'Amor' es nuestro apodo especial 💕"
        }
    
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
        f"¡Hola {user_name}! 💕\n\n"
        f"Preparé algo especial para ti. "
        f"Responde estas {total_questions} preguntas sobre nuestra relación y descubre algo maravilloso al final. ✨\n\n"
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
            return jsonify({
                "success": True,
                "message": (
                    f"{current_question.get('success_message', '¡Correcto! 💕')}\n\n"
                    f"🎉 ¡FELICIDADES! 🎉\n\n"
                    f"Completaste el quiz con {session['correct_answers']} respuestas correctas. "
                    f"Conoces muy bien nuestra historia. 💕\n\n"
                    f"Ahora descubre el lugar especial que preparé para ti... 📍"
                ),
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
            next_question = {
                "question": "¿Qué es lo que más te gusta de nuestra relación?",
                "options": ["Todo", "Tu amor", "Nuestra conexión", "Nuestros momentos"],
                "correct_answers": ["todo", "tu amor", "nuestra conexión", "nuestros momentos"],
                "hints": ["Piensa en lo especial que somos...", "Es todo...", "TODO"],
                "success_message": "¡Exacto! Amo todo de nosotros 💕"
            }
        
        session['questions_asked'].append(next_question)
        session['current_question_index'] += 1
        
        response_message = (
            f"{current_question.get('success_message', '¡Correcto! 💕')}\n\n"
            f"Pregunta {next_question_number} de {total_questions}:\n\n"
            f"{next_question['question']}"
        )
        
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
                    "message": "❌ Has agotado todos los intentos disponibles.\n\nNo te preocupes, puedes intentarlo de nuevo cuando quieras. 💕",
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
                new_question = {
                    "question": "¿Cuál fue nuestro primer lugar especial juntos?",
                    "options": ["La universidad", "Un parque", "Un café", "El cine"],
                    "correct_answers": ["universidad", "u", "la u"],
                    "hints": ["Pasamos mucho tiempo ahí...", "Es donde estudiamos...", "La U"],
                    "success_message": "¡Exacto! La universidad es nuestro lugar especial 💕"
                }
            
            session['questions_asked'].append(new_question)
            session['current_question_index'] += 1
            
            response_message = (
                f"No te preocupes, probemos con otra pregunta. 😊\n\n"
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
        
        response_message = f"Mmm... no es eso. 🤔{hint_text}\n\n¡Te quedan {attempts_left} intentos!"
        
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
            "¡Lo lograste! 🎉\n\n"
            "Conoces muy bien nuestra historia. "
            "Ahora ven a este lugar... "
            "tengo algo importante que preguntarte. 💕"
        )
    }
    
    return jsonify({
        "success": True,
        **final_location
    })


if __name__ == '__main__':
    # 🚀 Inicializar RAG Service al inicio
    print("\n" + "="*60)
    print("🚀 Inicializando Romantic AI Proposal System")
    print("="*60)
    
    try:
        # Cargar todos los mensajes
        all_messages = load_all_messages()
        
        # Inicializar RAG
        print("\n📡 Inicializando RAG Service...")
        rag_service = get_rag_service(os.getenv('OPENAI_API_KEY'))
        
        # Construir índice (o cargar desde cache)
        rag_service.build_index(all_messages, force_rebuild=False)
        
        # Mostrar estadísticas
        stats = rag_service.get_statistics()
        print("\n📊 Estadísticas del RAG:")
        print(f"  - Total chunks: {stats['total_chunks']:,}")
        print(f"  - Total mensajes: {stats['total_messages']:,}")
        print(f"  - Total vectores: {stats['total_vectors']:,}")
        print(f"  - Modelo embeddings: {stats['embedding_model']}")
        print(f"  - Dimensión: {stats['embedding_dimension']}")
        print(f"  - Tamaño índice: {stats['index_size_mb']:.2f} MB")
        print(f"  - Cache existe: {'✅' if stats['cache_exists'] else '❌'}")
        
        print("\n" + "="*60)
        print("✅ Sistema inicializado correctamente")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error inicializando sistema: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  El sistema continuará sin RAG, usando método básico.")
    
    # Iniciar servidor
    port = int(os.getenv('BACKEND_PORT', os.getenv('PORT', 5000)))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"\n🌐 Servidor iniciando en http://{host}:{port}")
    print(f"🔧 Modo debug: {app.config['DEBUG']}")
    print(f"🔑 OpenAI API configurado: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("⚠️  ADVERTENCIA: OpenAI API Key no configurado correctamente")
        print("   Configura OPENAI_API_KEY en el archivo .env")
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])