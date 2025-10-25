"""
Prompt template for OpenAI question generation.
This file contains the system prompt used to generate quiz questions.
"""

def get_question_generator_prompt(
    top_nicknames: list,
    top_phrases: list,
    top_locations: list,
    examples_text: str,
    last_date: str,
    previous_qs: str,
    question_number: int
) -> str:
    """
    Generate the prompt for OpenAI to create quiz questions.
    
    Args:
        top_nicknames: List of (nickname, count) tuples
        top_phrases: List of (phrase, count) tuples
        top_locations: List of (location, count) tuples
        examples_text: String with message examples
        last_date: Last message date
        previous_qs: String with previous questions
        question_number: Current question number
    
    Returns:
        str: Complete prompt for OpenAI
    """
    
    return f"""Eres un experto en crear preguntas personalizadas sobre relaciones románticas.

DATOS REALES DE LA CONVERSACIÓN:

🏆 TOP APODOS POR FRECUENCIA (usa estos, están verificados):
{chr(10).join([f"  - '{nick}': usado {count} veces" for nick, count in top_nicknames]) if top_nicknames else '  (ninguno encontrado)'}

💕 TOP FRASES ROMÁNTICAS POR FRECUENCIA (usa estas, están verificadas):
{chr(10).join([f"  - '{phrase}': dicha {count} veces" for phrase, count in top_phrases]) if top_phrases else '  (ninguna encontrada)'}

📍 TOP LUGARES MENCIONADOS (usa estos, están verificados):
{chr(10).join([f"  - '{loc}': mencionado {count} veces" for loc, count in top_locations]) if top_locations else '  (ninguno encontrado)'}

📝 EJEMPLOS LITERALES DE MENSAJES (DEBES USAR ESTOS):
{examples_text if examples_text else '(no hay ejemplos disponibles)'}

⚠️ IMPORTANTE: Los datos van hasta {last_date}. NO preguntes sobre "hoy", "ayer" o fechas posteriores.

PREGUNTAS ANTERIORES (NO REPETIR temas ni categorías similares):
{previous_qs}

TAREA:
Genera 1 PREGUNTA GENERAL e INTERESANTE sobre la relación (#{question_number} de 7).

🎯 TIPO DE PREGUNTAS QUE QUEREMOS (VARIADAS Y GENERALES):
- ✅ Momentos divertidos/graciosos que hayan compartido
- ✅ Lugares o viajes que hayan mencionado
- ✅ Comidas, restaurantes o gustos en común
- ✅ Películas, series, música que les guste
- ✅ Planes futuros o sueños juntos
- ✅ Cómo superaron algo difícil
- ✅ Sorpresas o detalles románticos
- ✅ Primeras veces importantes (si están en mensajes)

🚫 EVITAR PREGUNTAS MUY ESPECÍFICAS:
- ❌ "¿Cuántas veces dije 'te quiero'?" (muy específico)
- ❌ "¿Cuál es el apodo exacto que uso?" (ya se preguntó mucho)
- ❌ "¿Qué frase específica te digo?" (muy repetitivo)
- ❌ Preguntas sobre conteos o datos imposibles de recordar

✅ EJEMPLOS DE BUENAS PREGUNTAS GENERALES (si están en los datos):
- "¿Qué es lo que más te divierte de mí según nuestras conversaciones?"
- "¿Cuál fue el lugar más especial que visitamos juntos?"
- "¿Qué película o serie hemos visto juntos?"
- "¿Cuál es nuestro plan más emocionante para el futuro?"
- "¿Qué momento gracioso siempre recordamos?"
- "¿Cuál fue la primera cosa especial que hicimos juntos?"

REGLAS IMPORTANTES:
1. Usa los mensajes de arriba para encontrar temas GENERALES (no detalles específicos)
2. NO repitas categorías de preguntas anteriores (si ya preguntaste sobre apodos, NO hagas otra sobre apodos)
3. Haz preguntas que sean MEMORABLES y divertidas de responder
4. Las respuestas deben ser DIFERENTES a las de preguntas anteriores
5. La pregunta debe tener 4 opciones variadas (1 correcta + 3 creíbles)

PROCESO:
1. 📋 Revisa los "EJEMPLOS LITERALES DE MENSAJES" 
2. 🔍 Identifica un TEMA GENERAL interesante (viajes, comida, momentos divertidos, etc.)
3. ✍️ Crea una pregunta AMPLIA sobre ese tema
4. ✅ Verifica que NO sea similar a preguntas anteriores

EJEMPLOS DE BUENAS PREGUNTAS (GENERALES):
✅ "¿Qué lugar especial hemos visitado juntos?" (si hay lugares mencionados)
✅ "¿Cuál es una de nuestras películas favoritas?" (si mencionan películas)
✅ "¿Qué plan tenemos para el futuro?" (si hablan de planes)
✅ "¿Qué momento divertido siempre recordamos?" (si hay anécdotas graciosas)

EJEMPLOS INVÁLIDOS (MUY ESPECÍFICOS):
❌ "¿Cuántas veces exactamente te dije 'te quiero'?" → Muy específico
❌ "¿Cuál es el apodo exacto?" → Ya se preguntó antes
❌ "¿Qué frase uso siempre?" → Muy repetitivo

Responde SOLO en formato JSON válido:
{{
  "question": "Pregunta GENERAL e INTERESANTE basada en los mensajes de arriba",
  "category": "momentos_divertidos/viajes/gustos/planes_futuros/entretenimiento/general",
  "difficulty": "medium",
  "correct_answers": ["respuesta principal", "variación 1", "variación 2"],
  "options": [
    "Respuesta correcta basada en los mensajes",
    "Opción incorrecta creíble",
    "Opción incorrecta creíble", 
    "Opción incorrecta creíble"
  ],
  "hints": [
    "Pista 1: Contexto general",
    "Pista 2: Detalle más específico",
    "Pista 3: Casi revelar la respuesta"
  ],
  "success_message": "¡Sí! [Confirma la respuesta de forma cariñosa y personal]",
  "data_source": "Basado en ejemplos de mensajes donde se menciona [tema general]"
}}

⚠️ VALIDACIÓN FINAL:
- ¿Es una pregunta GENERAL y VARIADA? → Si es muy específica, cámbiala
- ¿Es DIFERENTE a las preguntas anteriores? → Si es similar, elige otro tema
- ¿Está basada en los mensajes? → Si no, ajústala
- ¿Es MEMORABLE y divertida? → Si es aburrida, hazla más interesante

SOLO responde con el JSON, sin explicaciones adicionales."""
