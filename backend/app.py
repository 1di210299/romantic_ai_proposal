"""
Main Flask application for Romantic AI Proposal System.
A personalized chatbot that guides your loved one through a relationship quiz.

Las preguntas se generan dinámicamente usando OpenAI cuando se inicia el quiz.
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

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'

# OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
    
    if not conversation_dir.exists():
        print(f"❌ No se encontró: {CONVERSATION_PATH}")
        return []
    
    for msg_file in sorted(conversation_dir.glob("message_*.json")):
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


def generate_questions_with_openai(messages: list) -> dict:
    """
    Genera preguntas personalizadas usando OpenAI basadas en los mensajes.
    """
    print("🤖 Generando preguntas con OpenAI...")
    
    messages_text = format_messages_for_ai(messages)
    
    # Obtener info básica
    first_msg = messages[0] if messages else None
    first_date = datetime.fromtimestamp(first_msg['timestamp_ms'] / 1000).strftime('%Y-%m-%d') if first_msg else "desconocida"
    
    prompt = f"""Eres un experto en crear experiencias románticas personalizadas.

Analiza esta conversación de Instagram entre Juan Diego Gutierrez y Karem Ramos y genera 7 preguntas para un quiz romántico.

CONVERSACIÓN (últimos mensajes):
{messages_text}

CONTEXTO:
- Primera conversación: {first_date}
- Total de mensajes analizados: {len(messages)}
- Es una relación de pareja

TAREA:
Genera 7 preguntas personalizadas para un quiz romántico. Las preguntas deben:
1. Ser específicas de ESTA relación (basadas en los mensajes)
2. Variar en dificultad (2 fáciles, 3 medias, 2 difíciles)
3. Incluir respuestas múltiples aceptables
4. Tener 3 pistas progresivas
5. Mensajes de éxito románticos

Responde SOLO en formato JSON válido (sin markdown):
{{
  "questions": [
    {{
      "id": 1,
      "question": "pregunta específica basada en los mensajes",
      "category": "lugares/fechas/apodos/momentos/actividades",
      "difficulty": "easy/medium/hard",
      "correct_answers": ["respuesta exacta", "variación 1", "variación 2"],
      "hints": ["pista 1 sutil", "pista 2 más clara", "pista 3 casi la respuesta"],
      "success_message": "mensaje romántico al acertar",
      "context": "por qué esta pregunta (para el sistema)"
    }}
  ]
}}"""

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
        
        print(f"✅ Preguntas generadas ({tokens_used} tokens, ~${tokens_used * 0.000005:.4f})")
        
        return {
            "questions": result.get('questions', []),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tokens_used": tokens_used,
                "messages_analyzed": len(messages)
            }
        }
        
    except Exception as e:
        print(f"❌ Error generando preguntas: {e}")
        # Preguntas de respaldo genéricas
        return {
            "questions": [
                {
                    "id": 1,
                    "question": "¿Cuál es mi apodo favorito para ti?",
                    "category": "apodos",
                    "difficulty": "easy",
                    "correct_answers": ["amor", "mi amor"],
                    "hints": ["Es muy común...", "Empieza con 'a'...", "Es: amor"],
                    "success_message": "¡Sí! Mi amor siempre 💕",
                    "context": "Pregunta de respaldo"
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "is_fallback": True,
                "error": str(e)
            }
        }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Romantic AI Proposal System",
        "version": "1.0.0"
    })


@app.route('/api/start-quiz', methods=['POST'])
def start_quiz():
    """
    Initialize a new quiz session.
    Genera las preguntas dinámicamente usando OpenAI.
    
    Expected JSON body:
    {
        "user_name": "Name of your loved one"
    }
    """
    print("\n🚀 Iniciando nuevo quiz...")
    
    data = request.get_json() or {}
    user_name = data.get('user_name', 'Karem')
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    print(f"📝 Session ID: {session_id}")
    print(f"👤 Usuario: {user_name}")
    
    try:
        # 1. Cargar mensajes
        messages = load_messages_sample(max_messages=1000)
        
        if not messages:
            return jsonify({
                "success": False,
                "error": "No se pudieron cargar los mensajes de la conversación"
            }), 500
        
        # 2. Generar preguntas con OpenAI
        print("🤖 Generando preguntas personalizadas...")
        questions_result = generate_questions_with_openai(messages)
        
        if not questions_result.get('questions'):
            return jsonify({
                "success": False,
                "error": "No se pudieron generar preguntas"
            }), 500
        
        questions = questions_result['questions']
        total_questions = len(questions)
        
        print(f"✅ {total_questions} preguntas generadas")
        
        # 3. Inicializar sesión
        quiz_sessions[session_id] = {
            "user_name": user_name,
            "questions": questions,  # Preguntas generadas guardadas en la sesión
            "metadata": questions_result.get('metadata', {}),
            "current_question_index": 0,
            "correct_answers": 0,
            "hints_used": 0,
            "attempts_current_question": 0,
            "started_at": datetime.now().isoformat(),
            "completed": False,
            "answers_history": []
        }
        
        welcome_message = (
            f"¡Hola {user_name}! 💕\n\n"
            "He preparado algo especial para ti. "
            "Vamos a hacer un pequeño viaje por nuestros momentos favoritos juntos.\n\n"
            f"Tengo {total_questions} preguntas sobre nuestra relación. "
            "Responde correctamente y al final... "
            "habrá una sorpresa esperándote. 😊\n\n"
            "¿Lista para empezar? Escribe 'sí' o 'empezar'."
        )
        
        print("✅ Quiz iniciado exitosamente\n")
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": welcome_message,
            "current_question": 0,
            "total_questions": total_questions,
            "status": "ready"
        })
        
    except Exception as e:
        print(f"❌ Error iniciando quiz: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": f"Error iniciando quiz: {str(e)}"
        }), 500


def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison."""
    return answer.lower().strip().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

def check_answer(user_answer: str, correct_answers: list) -> bool:
    """Check if user answer matches any correct answer."""
    normalized_user = normalize_answer(user_answer)
    
    for correct in correct_answers:
        normalized_correct = normalize_answer(correct)
        
        # Exact match
        if normalized_user == normalized_correct:
            return True
        
        # Contains match (for longer answers)
        if normalized_correct in normalized_user or normalized_user in normalized_correct:
            if len(normalized_user) > 3:  # Avoid false positives with short words
                return True
    
    return False


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process user message and return chatbot response.
    Usa las preguntas generadas dinámicamente.
    
    Expected JSON body:
    {
        "session_id": "uuid",
        "message": "User's answer or message"
    }
    """
    data = request.get_json()
    session_id = data.get('session_id')
    user_message = data.get('message', '').strip()
    
    print(f"\n💬 Mensaje recibido: '{user_message}' (Session: {session_id[:8]}...)")
    
    if not session_id or session_id not in quiz_sessions:
        return jsonify({
            "success": False,
            "error": "Sesión inválida. Por favor inicia de nuevo."
        }), 400
    
    if not user_message:
        return jsonify({
            "success": False,
            "error": "Mensaje vacío"
        }), 400
    
    session = quiz_sessions[session_id]
    questions = session.get('questions', [])  # Preguntas de la sesión, no global
    total_questions = len(questions)
    
    # Check if quiz is completed
    if session['completed']:
        return jsonify({
            "success": True,
            "message": "¡Ya completaste todas las preguntas! 🎉 Ahora puedes ver la ubicación final.",
            "completed": True,
            "current_question": total_questions,
            "total_questions": total_questions
        })
    
    current_index = session['current_question_index']
    
    # Handle initial "sí" to start
    if current_index == 0 and session['correct_answers'] == 0 and normalize_answer(user_message) in ['si', 'sí', 'yes', 'ok', 'dale', 'vamos']:
        # Present first question
        first_question = questions[0]
        response_message = f"¡Perfecto! 💕\n\nPregunta 1 de {total_questions}:\n\n{first_question['question']}"
        
        return jsonify({
            "success": True,
            "message": response_message,
            "current_question": 1,
            "total_questions": total_questions,
            "is_correct": None,
            "completed": False
        })
    
    # Get current question
    if current_index >= total_questions:
        session['completed'] = True
        return jsonify({
            "success": True,
            "message": "¡Completaste todas las preguntas! 🎉",
            "completed": True,
            "current_question": total_questions,
            "total_questions": total_questions
        })
    
    current_question = questions[current_index]
    
    # Check answer
    is_correct = check_answer(user_message, current_question['correct_answers'])
    
    if is_correct:
        # Correct answer!
        session['correct_answers'] += 1
        session['attempts_current_question'] = 0
        session['answers_history'].append({
            'question_id': current_question['id'],
            'answer': user_message,
            'correct': True,
            'attempts': session['attempts_current_question'] + 1
        })
        
        # Move to next question
        session['current_question_index'] += 1
        next_index = session['current_question_index']
        
        # Success message
        success_msg = current_question.get('success_message', '¡Correcto! 💕')
        
        if next_index < total_questions:
            # There are more questions
            next_question = questions[next_index]
            response_message = (
                f"{success_msg}\n\n"
                f"Pregunta {next_index + 1} de {total_questions}:\n\n"
                f"{next_question['question']}"
            )
        else:
            # All questions completed!
            session['completed'] = True
            response_message = (
                f"{success_msg}\n\n"
                "🎉 ¡LO LOGRASTE! 🎉\n\n"
                "Respondiste todas las preguntas correctamente. "
                "Conoces muy bien nuestra historia... 💕\n\n"
                "Ahora tengo algo especial que mostrarte. "
                "Solicita la ubicación final para descubrir dónde te espero. 📍"
            )
        
        return jsonify({
            "success": True,
            "message": response_message,
            "current_question": next_index + 1,
            "total_questions": total_questions,
            "correct_answers": session['correct_answers'],
            "is_correct": True,
            "completed": session['completed']
        })
    
    else:
        # Incorrect answer
        session['attempts_current_question'] += 1
        attempts = session['attempts_current_question']
        
        # Give hints based on attempts
        hints = current_question.get('hints', [])
        
        if attempts <= len(hints):
            hint = hints[attempts - 1]
            response_message = f"Mmm... no es exactamente eso. 🤔\n\n💡 Pista: {hint}\n\n¡Inténtalo de nuevo!"
        else:
            # Too many attempts, give more explicit hint
            last_hint = hints[-1] if hints else "Piensa en nuestros momentos juntos..."
            response_message = f"Aún no... 😊\n\n💡 {last_hint}\n\n¡Tú puedes!"
        
        session['hints_used'] += 1
        
        return jsonify({
            "success": True,
            "message": response_message,
            "current_question": current_index + 1,
            "total_questions": total_questions,
            "correct_answers": session['correct_answers'],
            "is_correct": False,
            "hint": hints[min(attempts - 1, len(hints) - 1)] if hints else None,
            "completed": False
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
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
