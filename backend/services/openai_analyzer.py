"""
Backend service para analizar mensajes usando OpenAI API.
Procesa chunks de mensajes y genera preguntas personalizadas automáticamente.
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from pathlib import Path
import time


class OpenAIMessageAnalyzer:
    """Analizador que usa OpenAI para procesar mensajes y generar preguntas."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize analyzer with OpenAI.
        
        Args:
            api_key: OpenAI API key (si no se provee, usa variable de entorno)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key no encontrada. Configura OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=self.api_key)
        self.analysis_results = {
            'insights': [],
            'questions': [],
            'timeline': {},
            'relationship_context': {}
        }
    
    def load_messages(self, conversation_path: str) -> List[Dict]:
        """Carga todos los mensajes de la conversación."""
        print("\n📂 Cargando mensajes...")
        
        path = Path(conversation_path)
        all_messages = []
        
        for msg_file in sorted(path.glob("message_*.json")):
            print(f"   Leyendo {msg_file.name}...")
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = data.get('messages', [])
                all_messages.extend(messages)
        
        # Ordenar por timestamp
        all_messages.sort(key=lambda x: x.get('timestamp_ms', 0))
        
        print(f"✅ Total: {len(all_messages):,} mensajes cargados\n")
        return all_messages
    
    def create_message_chunks(self, messages: List[Dict], chunk_size: int = 100) -> List[str]:
        """
        Crea chunks de mensajes en formato texto para OpenAI.
        
        Args:
            messages: Lista de mensajes
            chunk_size: Número de mensajes por chunk
        
        Returns:
            Lista de chunks en formato texto
        """
        print(f"📦 Creando chunks de {chunk_size} mensajes...")
        
        chunks = []
        
        for i in range(0, len(messages), chunk_size):
            chunk_messages = messages[i:i + chunk_size]
            
            # Convertir a formato legible para OpenAI
            chunk_text = self._format_messages_for_ai(chunk_messages)
            chunks.append(chunk_text)
        
        print(f"✅ {len(chunks)} chunks creados\n")
        return chunks
    
    def _format_messages_for_ai(self, messages: List[Dict]) -> str:
        """Formatea mensajes para que sean legibles por OpenAI."""
        formatted = []
        
        for msg in messages:
            sender = msg.get('sender_name', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp_ms', 0)
            
            if content:
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                formatted.append(f"[{date}] {sender}: {content}")
        
        return "\n".join(formatted)
    
    def analyze_chunk_with_openai(self, chunk_text: str, chunk_id: int) -> Dict:
        """
        Analiza un chunk de mensajes usando OpenAI.
        
        Args:
            chunk_text: Texto del chunk
            chunk_id: ID del chunk
        
        Returns:
            Dict con insights del chunk
        """
        print(f"🤖 Analizando chunk {chunk_id + 1} con OpenAI...")
        
        prompt = f"""Analiza esta conversación de una pareja y extrae información relevante para crear un quiz romántico.

CONVERSACIÓN:
{chunk_text}

EXTRAE:
1. Lugares mencionados (cafés, restaurantes, parques, etc.)
2. Fechas o eventos importantes mencionados
3. Apodos cariñosos usados
4. Actividades que hacen juntos
5. Momentos especiales o significativos
6. Cualquier cosa única de su relación

Responde en formato JSON con esta estructura:
{{
    "lugares": ["lista de lugares mencionados"],
    "fechas_eventos": ["eventos importantes mencionados"],
    "apodos": ["apodos cariñosos"],
    "actividades": ["actividades compartidas"],
    "momentos_especiales": ["momentos significativos"],
    "frases_unicas": ["frases o expresiones únicas de ellos"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Más barato y rápido
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en analizar conversaciones de parejas para identificar momentos significativos y crear experiencias personalizadas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result['chunk_id'] = chunk_id
            result['tokens_used'] = response.usage.total_tokens
            
            print(f"   ✓ Chunk {chunk_id + 1} analizado ({result['tokens_used']} tokens)")
            
            return result
            
        except Exception as e:
            print(f"   ✗ Error en chunk {chunk_id + 1}: {e}")
            return {
                'chunk_id': chunk_id,
                'error': str(e),
                'lugares': [],
                'fechas_eventos': [],
                'apodos': [],
                'actividades': [],
                'momentos_especiales': [],
                'frases_unicas': []
            }
    
    def merge_chunk_insights(self, chunk_results: List[Dict]) -> Dict:
        """Combina insights de todos los chunks."""
        print("\n🔄 Combinando insights de todos los chunks...")
        
        merged = {
            'lugares': [],
            'fechas_eventos': [],
            'apodos': [],
            'actividades': [],
            'momentos_especiales': [],
            'frases_unicas': [],
            'total_tokens': 0
        }
        
        for result in chunk_results:
            if 'error' not in result:
                merged['lugares'].extend(result.get('lugares', []))
                merged['fechas_eventos'].extend(result.get('fechas_eventos', []))
                merged['apodos'].extend(result.get('apodos', []))
                merged['actividades'].extend(result.get('actividades', []))
                merged['momentos_especiales'].extend(result.get('momentos_especiales', []))
                merged['frases_unicas'].extend(result.get('frases_unicas', []))
                merged['total_tokens'] += result.get('tokens_used', 0)
        
        # Eliminar duplicados y ordenar por frecuencia
        for key in ['lugares', 'apodos', 'actividades', 'frases_unicas']:
            if merged[key]:
                # Contar frecuencia
                from collections import Counter
                counter = Counter(merged[key])
                # Ordenar por frecuencia
                merged[key] = [item for item, count in counter.most_common()]
        
        print(f"✅ Insights combinados ({merged['total_tokens']} tokens totales)")
        
        return merged
    
    def generate_questions_with_openai(self, insights: Dict, messages_sample: List[Dict]) -> List[Dict]:
        """
        Genera preguntas personalizadas usando OpenAI basadas en los insights.
        
        Args:
            insights: Insights extraídos de los mensajes
            messages_sample: Muestra de mensajes para contexto adicional
        
        Returns:
            Lista de preguntas generadas
        """
        print("\n💡 Generando preguntas personalizadas con OpenAI...")
        
        # Obtener contexto temporal
        first_msg = messages_sample[0] if messages_sample else None
        last_msg = messages_sample[-1] if messages_sample else None
        
        first_date = datetime.fromtimestamp(first_msg['timestamp_ms'] / 1000).strftime('%Y-%m-%d') if first_msg else "desconocida"
        last_date = datetime.fromtimestamp(last_msg['timestamp_ms'] / 1000).strftime('%Y-%m-%d') if last_msg else "desconocida"
        
        prompt = f"""Eres un experto en crear experiencias románticas personalizadas. 

INFORMACIÓN DE LA RELACIÓN:
- Primera conversación: {first_date}
- Última conversación: {last_date}
- Total de mensajes: {len(messages_sample):,}

INSIGHTS EXTRAÍDOS:
{json.dumps(insights, indent=2, ensure_ascii=False)}

MUESTRA DE CONVERSACIONES RECIENTES:
{self._format_messages_for_ai(messages_sample[-50:])}

TAREA:
Genera 7 preguntas personalizadas para un quiz romántico que llevará a una propuesta especial.
Las preguntas deben:
1. Ser específicas de esta relación
2. Variar en dificultad (2 fáciles, 3 medias, 2 difíciles)
3. Tener respuestas basadas en datos reales
4. Incluir 3 pistas progresivas si se equivoca
5. Tener un mensaje de éxito romántico

Responde en formato JSON:
{{
  "questions": [
    {{
      "id": 1,
      "question": "pregunta específica",
      "category": "categoría (lugares/fechas/apodos/momentos/actividades)",
      "difficulty": "easy/medium/hard",
      "correct_answers": ["respuesta correcta", "variación 1", "variación 2"],
      "hints": ["pista 1 sutil", "pista 2 más clara", "pista 3 casi la respuesta"],
      "success_message": "mensaje romántico al acertar",
      "context": "contexto para el chatbot (no se muestra al usuario)",
      "why_important": "por qué esta pregunta es significativa para ellos"
    }}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Modelo más inteligente para preguntas de calidad
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en crear experiencias románticas memorables y personalizadas. Conoces cómo hacer preguntas significativas que conecten emocionalmente."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Un poco más creativo
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            questions = result.get('questions', [])
            tokens_used = response.usage.total_tokens
            
            print(f"✅ {len(questions)} preguntas generadas ({tokens_used} tokens)")
            print(f"💰 Costo aproximado: ${tokens_used * 0.000005:.4f}")
            
            return questions
            
        except Exception as e:
            print(f"✗ Error generando preguntas: {e}")
            return []
    
    def create_chatbot_context(self, insights: Dict, messages_sample: List[Dict]) -> Dict:
        """
        Crea contexto enriquecido para el chatbot usando OpenAI.
        
        Args:
            insights: Insights de la relación
            messages_sample: Muestra de mensajes
        
        Returns:
            Contexto para el chatbot
        """
        print("\n🤖 Generando contexto para el chatbot...")
        
        prompt = f"""Analiza esta relación y crea un contexto personalizado para un chatbot romántico.

INSIGHTS:
{json.dumps(insights, indent=2, ensure_ascii=False)}

MUESTRA DE CONVERSACIONES:
{self._format_messages_for_ai(messages_sample[-100:])}

Crea un perfil de la relación que incluya:
1. Estilo de comunicación de él
2. Temas recurrentes en sus conversaciones
3. Nivel de formalidad/informalidad
4. Emojis o expresiones favoritas
5. Tono general (divertido, serio, cariñoso, etc.)

Responde en JSON:
{{
    "communication_style": "descripción del estilo",
    "recurring_themes": ["tema 1", "tema 2", ...],
    "formality_level": "formal/casual/muy_casual",
    "favorite_expressions": ["expresión 1", "expresión 2", ...],
    "overall_tone": "descripción del tono",
    "relationship_personality": "descripción general de la relación"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de comunicación interpersonal."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            context = json.loads(response.choices[0].message.content)
            tokens_used = response.usage.total_tokens
            
            print(f"✅ Contexto generado ({tokens_used} tokens)")
            
            return context
            
        except Exception as e:
            print(f"✗ Error generando contexto: {e}")
            return {}
    
    def analyze_complete(
        self,
        conversation_path: str,
        max_messages: Optional[int] = None,
        chunk_size: int = 100
    ) -> Dict:
        """
        Ejecuta análisis completo de mensajes con OpenAI.
        
        Args:
            conversation_path: Ruta a la carpeta de mensajes
            max_messages: Límite de mensajes (None = todos)
            chunk_size: Tamaño de cada chunk
        
        Returns:
            Dict con análisis completo
        """
        print("\n" + "="*70)
        print("🚀 ANÁLISIS COMPLETO CON OPENAI")
        print("="*70)
        
        start_time = time.time()
        total_cost = 0
        
        # 1. Cargar mensajes
        all_messages = self.load_messages(conversation_path)
        
        if max_messages:
            print(f"⚠️  Limitando análisis a {max_messages} mensajes")
            all_messages = all_messages[:max_messages]
        
        # 2. Crear chunks
        chunks = self.create_message_chunks(all_messages, chunk_size)
        
        print(f"📊 Se analizarán {len(chunks)} chunks")
        print(f"💰 Costo estimado: ${len(chunks) * 500 * 0.000005:.2f} - ${len(chunks) * 1000 * 0.000005:.2f}\n")
        
        confirm = input("¿Continuar con el análisis? (s/n): ").strip().lower()
        if confirm != 's':
            print("❌ Análisis cancelado")
            return {}
        
        # 3. Analizar chunks con OpenAI
        chunk_results = []
        for i, chunk in enumerate(chunks):
            result = self.analyze_chunk_with_openai(chunk, i)
            chunk_results.append(result)
            
            # Pequeña pausa para no saturar la API
            if i < len(chunks) - 1:
                time.sleep(0.5)
        
        # 4. Combinar insights
        merged_insights = self.merge_chunk_insights(chunk_results)
        
        # 5. Generar preguntas
        questions = self.generate_questions_with_openai(merged_insights, all_messages)
        
        # 6. Crear contexto para chatbot
        chatbot_context = self.create_chatbot_context(merged_insights, all_messages)
        
        # 7. Compilar resultados
        elapsed_time = time.time() - start_time
        
        result = {
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'total_messages_analyzed': len(all_messages),
                'chunks_processed': len(chunks),
                'chunk_size': chunk_size,
                'total_tokens_used': merged_insights['total_tokens'],
                'processing_time_seconds': round(elapsed_time, 2),
                'estimated_cost_usd': round(merged_insights['total_tokens'] * 0.000005, 4)
            },
            'timeline': {
                'first_message': datetime.fromtimestamp(all_messages[0]['timestamp_ms'] / 1000).isoformat(),
                'last_message': datetime.fromtimestamp(all_messages[-1]['timestamp_ms'] / 1000).isoformat(),
                'total_messages': len(all_messages)
            },
            'insights': merged_insights,
            'questions': questions,
            'chatbot_context': chatbot_context
        }
        
        return result
    
    def save_results(self, result: Dict, output_path: str = "data/openai_analysis.json"):
        """Guarda resultados del análisis."""
        print(f"\n💾 Guardando resultados en {output_path}...")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Resultados guardados\n")
    
    def export_questions_to_template(self, questions: List[Dict], output_path: str = "data/questions_generated.json"):
        """Exporta preguntas generadas al formato del template."""
        print(f"\n📝 Exportando preguntas a {output_path}...")
        
        template = {
            "quiz_metadata": {
                "title": "Nuestro Rally del Amor 💕",
                "description": "Un viaje por nuestros momentos especiales",
                "created_by": "Juan Diego Gutierrez",
                "created_for": "Karem Ramos",
                "total_questions": len(questions),
                "generated_with": "OpenAI GPT-4",
                "generated_at": datetime.now().isoformat()
            },
            "questions": questions
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Preguntas exportadas\n")


def print_summary(result: Dict):
    """Imprime resumen del análisis."""
    print("\n" + "="*70)
    print("📊 RESUMEN DEL ANÁLISIS CON OPENAI")
    print("="*70)
    
    metadata = result['metadata']
    insights = result['insights']
    questions = result['questions']
    
    print(f"\n⏱️  PROCESAMIENTO:")
    print(f"   Tiempo: {metadata['processing_time_seconds']} segundos")
    print(f"   Mensajes analizados: {metadata['total_messages_analyzed']:,}")
    print(f"   Chunks procesados: {metadata['chunks_processed']}")
    print(f"   Tokens usados: {metadata['total_tokens_used']:,}")
    print(f"   💰 Costo: ${metadata['estimated_cost_usd']}")
    
    print(f"\n🔍 INSIGHTS DESCUBIERTOS:")
    print(f"   Lugares: {len(insights.get('lugares', []))}")
    print(f"   Eventos/Fechas: {len(insights.get('fechas_eventos', []))}")
    print(f"   Apodos: {len(insights.get('apodos', []))}")
    print(f"   Actividades: {len(insights.get('actividades', []))}")
    print(f"   Momentos especiales: {len(insights.get('momentos_especiales', []))}")
    
    if insights.get('lugares'):
        print(f"\n📍 TOP LUGARES:")
        for i, lugar in enumerate(insights['lugares'][:5], 1):
            print(f"   {i}. {lugar}")
    
    if insights.get('apodos'):
        print(f"\n💕 APODOS:")
        for i, apodo in enumerate(insights['apodos'][:5], 1):
            print(f"   {i}. {apodo}")
    
    print(f"\n💡 PREGUNTAS GENERADAS: {len(questions)}")
    for i, q in enumerate(questions, 1):
        print(f"\n   {i}. [{q.get('difficulty', 'medium').upper()}] {q.get('question', '')}")
        print(f"      Categoría: {q.get('category', '')}")
        print(f"      Respuestas: {', '.join(q.get('correct_answers', [])[:2])}")


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("💕 ROMANTIC AI - ANÁLISIS CON OPENAI")
    print("   Genera preguntas personalizadas automáticamente")
    print("="*70 + "\n")
    
    # Verificar API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY no encontrada")
        print("\n📝 Configura tu API key:")
        print("   export OPENAI_API_KEY='tu-api-key'")
        print("   O créala en el archivo .env\n")
        return
    
    print("✅ API key encontrada\n")
    
    # Configuración
    conversation_path = "karemramos_1184297046409691"
    
    if not os.path.exists(conversation_path):
        print(f"❌ Error: Carpeta {conversation_path} no encontrada")
        return
    
    # Preguntar límite de mensajes
    print("⚙️  CONFIGURACIÓN:")
    print("   Para pruebas rápidas, limita los mensajes a analizar")
    print("   Para análisis completo, deja en blanco\n")
    
    max_msg_input = input("   Máximo de mensajes (ej: 1000, o ENTER para todos): ").strip()
    max_messages = int(max_msg_input) if max_msg_input else None
    
    chunk_input = input("   Tamaño de chunk (default: 100, ENTER): ").strip()
    chunk_size = int(chunk_input) if chunk_input else 100
    
    print()
    
    # Inicializar analizador
    try:
        analyzer = OpenAIMessageAnalyzer(api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    
    # Ejecutar análisis
    result = analyzer.analyze_complete(
        conversation_path=conversation_path,
        max_messages=max_messages,
        chunk_size=chunk_size
    )
    
    if not result:
        return
    
    # Guardar resultados
    analyzer.save_results(result)
    
    # Exportar preguntas
    if result.get('questions'):
        analyzer.export_questions_to_template(result['questions'])
    
    # Mostrar resumen
    print_summary(result)
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70)
    
    print(f"\n📄 ARCHIVOS GENERADOS:")
    print(f"   1. data/openai_analysis.json - Análisis completo")
    print(f"   2. data/questions_generated.json - Preguntas listas para usar")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"   1. Revisa las preguntas generadas")
    print(f"   2. Personaliza si es necesario")
    print(f"   3. Copia a data/questions.json")
    print(f"   4. Configura el backend")
    print(f"   5. ¡Prueba el chatbot!\n")


if __name__ == "__main__":
    main()
