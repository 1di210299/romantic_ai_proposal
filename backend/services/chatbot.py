"""
Conversational Chatbot Service
Genera respuestas naturales y conversacionales usando OpenAI
"""

import json
import random
from openai import OpenAI
from typing import Dict, List, Optional


def generate_conversational_response(
    openai_client: OpenAI,
    context: str,
    user_answer: str,
    is_correct: bool,
    question_info: Dict,
    session_info: Dict,
    rag_service = None
) -> str:
    """
    Genera una respuesta conversacional y natural usando OpenAI.
    
    Args:
        openai_client: Cliente de OpenAI
        context: Contexto de la conversación
        user_answer: Respuesta del usuario
        is_correct: Si la respuesta fue correcta
        question_info: Información de la pregunta actual
        session_info: Información de la sesión
        rag_service: Servicio RAG para contexto adicional
    
    Returns:
        Respuesta conversacional del chatbot
    """
    
    try:
        # Obtener contexto adicional usando RAG si está disponible
        additional_context = ""
        if rag_service and hasattr(rag_service, 'search'):
            try:
                # Buscar mensajes relacionados con la respuesta del usuario
                related_chunks = rag_service.search(user_answer, k=3)
                if related_chunks:
                    additional_context = "\\n\\nRecuerdos relacionados:\\n"
                    for chunk in related_chunks[:2]:  # Solo los 2 más relevantes
                        messages_preview = chunk['messages_in_chunk'][:2]
                        for msg in messages_preview:
                            if msg.get('content'):
                                additional_context += f"- {msg['content'][:100]}...\\n"
            except:
                pass  # Si falla RAG, continuar sin contexto adicional
        
        # Construir el prompt para OpenAI
        system_prompt = f"""Eres Juan Diego hablándole a Karem en un quiz sobre su historia juntos. Este es tu regalo para ella.

PERSONALIDAD:
- Eres Juan Diego, habla normal y relajado
- NUNCA uses emojis en tus respuestas
- No seas muy romántico o intenso, habla casual
- Cuando recuerdes algo, da MUCHOS detalles específicos del contexto
- Incluye fechas, lugares, qué estaban haciendo exactamente

FORMA DE DIRIGIRTE A KAREM:
- Habla como normalmente le hablas: "amor", "loca", o "Karem"
- Tono casual y natural, no meloso

CONTEXTO ACTUAL:
- Pregunta #{session_info.get('current_question', 1)} de {session_info.get('total_questions', 7)}
- Respuestas correctas hasta ahora: {session_info.get('correct_answers', 0)}

PREGUNTA ACTUAL: {question_info.get('question', '')}
RESPUESTA DEL USUARIO: "{user_answer}"
RESPUESTA {'CORRECTA' if is_correct else 'INCORRECTA'}

{additional_context}

INSTRUCCIONES:
1. Si es CORRECTA: Celebra de manera casual, menciona por qué recuerdas ese momento
2. Si es INCORRECTA: Da la respuesta correcta CON MUCHOS DETALLES del contexto para que pueda recordar
3. Tono natural y relajado, no romántico intenso
4. Cuando des pistas, incluye fecha, lugar, qué estaban haciendo, cómo pasó exactamente
5. Máximo 120 palabras para dar suficiente contexto
6. Habla casual, como en una conversación normal

Responde de forma natural y relajada:"""

        user_prompt = f"Karem respondió: '{user_answer}'. {'Estuvo correcto' if is_correct else 'No estuvo correcto'}. Responde de manera natural como su novio."

        # Llamar a OpenAI para generar respuesta conversacional
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.7,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        conversational_response = response.choices[0].message.content.strip()
        
        # Agregar información técnica solo si es necesario
        if is_correct:
            # Para respuestas correctas, solo la respuesta conversacional
            return conversational_response
        else:
            # Para respuestas incorrectas, agregar la respuesta correcta si no la mencionó
            correct_answers = question_info.get('correct_answers', [])
            if correct_answers and not any(ans.lower() in conversational_response.lower() for ans in correct_answers):
                correct_answer = correct_answers[0]
                return f"{conversational_response}\\n\\nLa respuesta era: {correct_answer}"
            return conversational_response
            
    except Exception as e:
        print(f"❌ Error generando respuesta conversacional: {e}")
        
        # Fallback a respuestas básicas pero más naturales
        if is_correct:
            fallbacks = [
                "¡Exacto! Sabía que te acordarías.",
                "¡Sí! Bien recordado, amor.",
                "¡Correcto! Ese momento también me gusta recordar.",
                "¡Perfecto! Me alegra que lo tengas presente."
            ]
        else:
            correct_answer = question_info.get('correct_answers', ['la respuesta correcta'])[0]
            fallbacks = [
                f"No exactamente, la respuesta era: {correct_answer}",
                f"Casi, en realidad era: {correct_answer}",
                f"No amor, pero no te preocupes. Era: {correct_answer}"
            ]
        
        return random.choice(fallbacks)


def generate_next_question_intro(
    openai_client: OpenAI,
    next_question: Dict,
    session_info: Dict
) -> str:
    """
    Genera una introducción natural para la siguiente pregunta.
    
    Args:
        openai_client: Cliente de OpenAI
        next_question: Información de la siguiente pregunta
        session_info: Información de la sesión
    
    Returns:
        Introducción conversacional para la siguiente pregunta
    """
    
    try:
        question_number = session_info.get('current_question', 1) + 1
        total_questions = session_info.get('total_questions', 7)
        
        system_prompt = f"""Eres Juan Diego hablándole a Karem en un quiz especial sobre su historia juntos.

CONTEXTO:
- Van en la pregunta #{question_number} de {total_questions}
- Respuestas correctas: {session_info.get('correct_answers', 0)}

TAREA: Crear una transición natural hacia la siguiente pregunta.

INSTRUCCIONES:
1. Máximo 40 palabras
2. Tono natural, como realmente le hablarías
3. Menciona el número de pregunta de manera natural
4. NO reveles la respuesta
5. Mantén la emoción del quiz
6. NUNCA uses emojis

SIGUIENTE PREGUNTA: {next_question.get('question', '')}"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Introduce la pregunta #{question_number}: {next_question.get('question', '')}"}
            ],
            max_tokens=80,
            temperature=0.6
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ Error generando introducción: {e}")
        
        # Fallback simple
        question_number = session_info.get('current_question', 1) + 1
        total_questions = session_info.get('total_questions', 7)
        return f"¡Perfecto! Vamos con la pregunta {question_number} de {total_questions}: 💕"


def generate_completion_message(
    openai_client: OpenAI,
    session_info: Dict,
    rag_service = None
) -> str:
    """
    Genera un mensaje de completación personalizado cuando termina el quiz.
    
    Args:
        openai_client: Cliente de OpenAI
        session_info: Información completa de la sesión
        rag_service: Servicio RAG para contexto romántico
    
    Returns:
        Mensaje de completación personalizado
    """
    
    try:
        correct_answers = session_info.get('correct_answers', 0)
        total_questions = session_info.get('total_questions', 7)
        
        # Obtener momentos románticos usando RAG
        romantic_context = ""
        if rag_service and hasattr(rag_service, 'search'):
            try:
                romantic_chunks = rag_service.search("te amo amor siempre juntos futuro", k=3)
                if romantic_chunks:
                    romantic_context = "\\n\\nRecuerdos especiales de nosotros:\\n"
                    for chunk in romantic_chunks[:2]:
                        messages = chunk['messages_in_chunk'][:2]
                        for msg in messages:
                            if msg.get('content') and len(msg['content']) > 20:
                                romantic_context += f"- {msg['content'][:80]}...\\n"
            except:
                pass
        
        system_prompt = f"""Eres Juan Diego hablándole a Karem después de completar el quiz sobre su historia juntos.

RESULTADOS DEL QUIZ:
- Respondió {correct_answers} de {total_questions} preguntas correctamente
- Porcentaje: {(correct_answers/total_questions)*100:.0f}%

{romantic_context}

TAREA: Crear un mensaje final emotivo que lleve a la revelación de la ubicación especial.

INSTRUCCIONES:
1. Celebra sus resultados de manera cariñosa
2. Reflexiona sobre su historia juntos
3. Crea expectativa sobre "algo especial" que Juan Diego quiere decirle
4. Prepara el terreno para revelar una ubicación
5. Máximo 200 palabras
6. Tono: emocionado, romántico, significativo
7. NUNCA uses emojis
7. NO menciones la ubicación aún, solo que hay "algo importante"

Genera un mensaje que la emocione y prepare para la sorpresa final:"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Karem completó el quiz con {correct_answers}/{total_questions} respuestas correctas. Genera el mensaje final antes de revelar la ubicación especial."}
            ],
            max_tokens=250,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ Error generando mensaje de completación: {e}")
        
        # Fallback emotivo
        correct_answers = session_info.get('correct_answers', 0)
        total_questions = session_info.get('total_questions', 7)
        
        if correct_answers == total_questions:
            return f"¡Increíble, mi amor! Respondiste perfectamente las {total_questions} preguntas. 💕\\n\\nRealmente conoces nuestra historia y eso me llena de felicidad. Cada respuesta me recordó por qué te amo tanto.\\n\\nAhora... hay algo muy especial que quiero mostrarte. Un lugar que significa mucho para nosotros. ❤️"
        else:
            return f"¡Excelente, mi vida! {correct_answers} de {total_questions} respuestas correctas. 💕\\n\\nMe encanta ver cuánto recuerdas de nosotros. Cada momento que hemos vivido juntos ha sido especial.\\n\\nTengo algo importante que mostrarte... un lugar especial donde quiero estar contigo. ❤️"