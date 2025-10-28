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
        system_prompt = f"""Eres Juan Diego, el novio enamorado de Karem. Estás haciendo un quiz romántico especial como sorpresa.

PERSONALIDAD:
- Eres cariñoso, romántico y juguetón
- Conoces perfectamente su historia juntos
- Usas emojis ocasionalmente pero sin exagerar
- Hablas como un novio real, no como un bot

CONTEXTO ACTUAL:
- Pregunta #{session_info.get('current_question', 1)} de {session_info.get('total_questions', 7)}
- Respuestas correctas hasta ahora: {session_info.get('correct_answers', 0)}

PREGUNTA ACTUAL: {question_info.get('question', '')}
RESPUESTA DEL USUARIO: "{user_answer}"
RESPUESTA {'CORRECTA' if is_correct else 'INCORRECTA'}

{additional_context}

INSTRUCCIONES:
1. Si es CORRECTA: Celebra de manera cariñosa y personal, menciona por qué esa respuesta te hace feliz
2. Si es INCORRECTA: Sé comprensivo pero dile cuál era la respuesta correcta de manera dulce
3. Mantén el tono romántico pero natural
4. Haz referencia a recuerdos específicos cuando sea posible
5. Máximo 150 palabras
6. NO menciones que eres un AI o chatbot

Responde como Juan Diego hablaría realmente:"""

        user_prompt = f"La respuesta de Karem fue: '{user_answer}'. {'Estuvo correcta' if is_correct else 'No estuvo correcta'}. Responde de manera cariñosa y personal."

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
                "¡Exacto, mi amor! 💕 Sabía que lo recordarías.",
                "¡Sí! Me encanta que recuerdes eso. ❤️",
                "¡Correcto, bebé! Esos momentos son especiales para mí también.",
                "¡Perfecto! Me hace feliz que tengas presente eso. 😊"
            ]
        else:
            correct_answer = question_info.get('correct_answers', ['la respuesta correcta'])[0]
            fallbacks = [
                f"No exactamente, amor. La respuesta era: {correct_answer} 💕",
                f"Casi, mi vida. En realidad era: {correct_answer} ❤️",
                f"No mi cielo, pero no te preocupes. Era: {correct_answer} 😊"
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
        
        system_prompt = f"""Eres Juan Diego haciendo un quiz romántico a tu novia Karem.

CONTEXTO:
- Van en la pregunta #{question_number} de {total_questions}
- Respuestas correctas: {session_info.get('correct_answers', 0)}

TAREA: Crear una transición natural y cariñosa hacia la siguiente pregunta.

INSTRUCCIONES:
1. Máximo 50 palabras
2. Tono cariñoso pero no empalagoso
3. Menciona el número de pregunta de manera natural
4. NO reveles la respuesta
5. Mantén la emoción del quiz

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
        
        system_prompt = f"""Eres Juan Diego terminando un quiz romántico especial para tu novia Karem.

RESULTADOS DEL QUIZ:
- Respondió {correct_answers} de {total_questions} preguntas correctamente
- Porcentaje: {(correct_answers/total_questions)*100:.0f}%

{romantic_context}

TAREA: Crear un mensaje final emotivo y romántico que lleve a la revelación de la ubicación especial.

INSTRUCCIONES:
1. Celebra sus resultados de manera cariñosa
2. Reflexiona sobre su historia juntos
3. Crea expectativa sobre "algo especial" que quieres decirle
4. Prepara el terreno para revelar una ubicación
5. Máximo 200 palabras
6. Tono: emocionado, romántico, significativo
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