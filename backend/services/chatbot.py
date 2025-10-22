"""
OpenAI Chatbot Service for natural conversational responses.
This module integrates OpenAI GPT to create a personalized romantic chatbot.
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class RomanticChatbot:
    """
    Chatbot that maintains context about the relationship and provides
    natural, romantic responses to guide through the quiz.
    """
    
    def __init__(self, relationship_context: Dict):
        """
        Initialize chatbot with relationship context.
        
        Args:
            relationship_context: Dictionary with info about the relationship
                - names: Names of both people
                - important_dates: Key dates in the relationship
                - special_places: Meaningful locations
                - inside_jokes: Shared jokes or phrases
                - conversation_style: How you typically communicate
        """
        self.context = relationship_context
        self.conversation_history = []
        
        # System prompt that defines the chatbot's personality
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with relationship context."""
        return f"""
Eres un chatbot romántico y cariñoso creado especialmente para guiar a {self.context.get('her_name', 'mi amor')} 
a través de un quiz sobre su relación con {self.context.get('his_name', 'su novio')}.

CONTEXTO DE LA RELACIÓN:
{json.dumps(self.context, indent=2, ensure_ascii=False)}

TU PERSONALIDAD:
- Eres cariñoso y romántico, pero no empalagoso
- Usas el mismo estilo de comunicación que {self.context.get('his_name', 'él')} usa normalmente
- Das pistas sutiles cuando ella se equivoca, sin revelar la respuesta directamente
- Celebras cada respuesta correcta con entusiasmo genuino
- Mantienes el misterio sobre la sorpresa final

REGLAS IMPORTANTES:
1. NUNCA reveles la respuesta correcta directamente
2. Si se equivoca, da una pista sutil relacionada con el contexto
3. Después de 2 intentos incorrectos, da una pista más específica
4. Cada respuesta correcta debe llevar a la siguiente pregunta naturalmente
5. Mantén un tono conversacional y natural, como si él estuviera hablando
6. NO uses emojis en exceso (máximo 2-3 por mensaje)
7. Respuestas cortas y directas, no párrafos largos

FLUJO:
- Primera pregunta: Preséntate brevemente y haz la pregunta
- Respuesta incorrecta: Pista amable sin revelar respuesta
- Respuesta correcta: Celebra y conecta con la siguiente pregunta
- Última pregunta: Construye emoción antes de revelar ubicación
"""
    
    def ask_question(
        self,
        question_data: Dict,
        attempt_number: int = 1
    ) -> str:
        """
        Present a question to the user in a conversational way.
        
        Args:
            question_data: Dict with question, context, hints
            attempt_number: How many times user has tried this question
            
        Returns:
            Natural conversational prompt with the question
        """
        question_text = question_data['question']
        context = question_data.get('context', '')
        
        if attempt_number == 1:
            # First time asking
            user_prompt = f"""
Pregunta #{question_data['order']}: {question_text}

Contexto para ti (no menciones esto explícitamente): {context}

Presenta esta pregunta de manera natural y conversacional.
"""
        else:
            # Retry after incorrect answer
            hint_index = min(attempt_number - 2, len(question_data['hints']) - 1)
            hint = question_data['hints'][hint_index] if question_data.get('hints') else None
            
            user_prompt = f"""
La usuaria respondió incorrectamente a: {question_text}

Intento #{attempt_number}

{"Pista para dar: " + hint if hint else "Da una pista basada en el contexto sin revelar la respuesta."}

Responde con una pista amable y alentadora.
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history,
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            bot_message = response.choices[0].message.content.strip()
            
            # Save to history
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": bot_message})
            
            return bot_message
            
        except Exception as e:
            # Fallback if OpenAI fails
            return f"Error connecting to AI: {str(e)}"
    
    def validate_answer(
        self,
        user_answer: str,
        correct_answers: List[str]
    ) -> tuple[bool, float]:
        """
        Use AI to intelligently validate if answer is correct.
        Allows for variations and natural language.
        
        Args:
            user_answer: What the user said
            correct_answers: List of acceptable answer variations
            
        Returns:
            (is_correct, confidence_score)
        """
        validation_prompt = f"""
Respuesta del usuario: "{user_answer}"
Respuestas correctas aceptadas: {correct_answers}

¿La respuesta del usuario es correcta? 
Considera variaciones razonables, errores ortográficos menores, 
y diferentes formas de expresar lo mismo.

Responde SOLO con un JSON:
{{"is_correct": true/false, "confidence": 0.0-1.0}}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un validador preciso de respuestas."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result['is_correct'], result['confidence']
            
        except Exception:
            # Fallback to simple string matching
            user_lower = user_answer.lower().strip()
            for correct in correct_answers:
                if correct.lower().strip() in user_lower or user_lower in correct.lower().strip():
                    return True, 0.8
            return False, 0.0
    
    def celebrate_correct_answer(
        self,
        question_data: Dict,
        is_final: bool = False
    ) -> str:
        """
        Generate celebratory message for correct answer.
        
        Args:
            question_data: The question that was answered correctly
            is_final: Is this the last question?
            
        Returns:
            Celebratory message
        """
        success_msg = question_data.get('success_message', '¡Correcto!')
        
        if is_final:
            prompt = f"""
La usuaria respondió correctamente la ÚLTIMA pregunta del quiz.
Mensaje predefinido: {success_msg}

Crea un mensaje emocionante que:
1. Celebre que completó todo el quiz
2. Construya anticipación para la sorpresa
3. Le diga que ahora verá una ubicación especial
4. Sea romántico pero no cursi

Máximo 3 líneas.
"""
        else:
            prompt = f"""
Respuesta correcta!
Mensaje predefinido: {success_msg}

Celebra brevemente y transiciona natural a la siguiente pregunta.
Máximo 2 líneas.
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception:
            return success_msg


# Example usage
if __name__ == "__main__":
    # Test the chatbot
    test_context = {
        "his_name": "Juan",
        "her_name": "María",
        "relationship_start": "2024-01-15",
        "first_meeting_place": "Cafetería Central",
        "conversation_style": "casual, uses some slang, caring"
    }
    
    chatbot = RomanticChatbot(test_context)
    print("Chatbot initialized successfully!")
