#!/usr/bin/env python3
"""
Script de PRUEBA SIMPLE para analizar mensajes con OpenAI.
Analiza solo 500 mensajes para probar rápido y barato (~$0.10).
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar rutas al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.openai_analyzer import OpenAIMessageAnalyzer


def test_openai_connection():
    """Prueba la conexión con OpenAI."""
    print("\n🔍 Probando conexión con OpenAI...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY no encontrada")
        print("\n📝 Para obtener tu API key:")
        print("   1. Ve a: https://platform.openai.com/api-keys")
        print("   2. Crea una cuenta o inicia sesión")
        print("   3. Crea una nueva API key")
        print("   4. Copia la key y pégala en el archivo .env")
        print("\n📄 Edita el archivo: .env")
        print("   OPENAI_API_KEY=tu-key-aqui")
        return False
    
    print(f"✅ API key encontrada: {api_key[:20]}...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Prueba simple
        print("   Probando API con request simple...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Di 'hola' en español"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"   Respuesta de OpenAI: {result}")
        print("✅ Conexión exitosa!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando con OpenAI: {e}")
        print("\n💡 Verifica que:")
        print("   1. Tu API key sea correcta")
        print("   2. Tengas créditos en tu cuenta de OpenAI")
        print("   3. La key no esté revocada")
        return False


def run_test_analysis():
    """Ejecuta análisis de prueba con pocos mensajes."""
    print("\n" + "="*70)
    print("🧪 ANÁLISIS DE PRUEBA CON OPENAI")
    print("   Analizando solo 500 mensajes (rápido y económico)")
    print("="*70 + "\n")
    
    # Verificar conexión primero
    if not test_openai_connection():
        return
    
    conversation_path = "karemramos_1184297046409691"
    
    if not os.path.exists(conversation_path):
        print(f"❌ Error: Carpeta {conversation_path} no encontrada")
        return
    
    print("⚙️  CONFIGURACIÓN DE PRUEBA:")
    print("   📊 Mensajes: 500 (muestra)")
    print("   📦 Chunk size: 100")
    print("   💰 Costo estimado: ~$0.05 - $0.15")
    print()
    
    confirm = input("¿Ejecutar prueba? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Prueba cancelada")
        return
    
    try:
        # Inicializar analizador
        api_key = os.getenv('OPENAI_API_KEY')
        analyzer = OpenAIMessageAnalyzer(api_key)
        
        # Ejecutar análisis de prueba
        result = analyzer.analyze_complete(
            conversation_path=conversation_path,
            max_messages=500,  # Solo 500 mensajes para prueba
            chunk_size=100
        )
        
        if not result:
            return
        
        # Guardar resultados
        test_output = "data/test_openai_analysis.json"
        analyzer.save_results(result, test_output)
        
        # Exportar preguntas
        if result.get('questions'):
            test_questions = "data/test_questions_generated.json"
            analyzer.export_questions_to_template(result['questions'], test_questions)
        
        # Mostrar resumen
        print("\n" + "="*70)
        print("📊 RESUMEN DE LA PRUEBA")
        print("="*70)
        
        metadata = result['metadata']
        insights = result['insights']
        questions = result.get('questions', [])
        
        print(f"\n⏱️  PROCESAMIENTO:")
        print(f"   Tiempo: {metadata['processing_time_seconds']} segundos")
        print(f"   Mensajes: {metadata['total_messages_analyzed']:,}")
        print(f"   Tokens: {metadata['total_tokens_used']:,}")
        print(f"   💰 Costo: ${metadata['estimated_cost_usd']}")
        
        print(f"\n🔍 INSIGHTS:")
        print(f"   Lugares: {len(insights.get('lugares', []))}")
        print(f"   Apodos: {len(insights.get('apodos', []))}")
        print(f"   Actividades: {len(insights.get('actividades', []))}")
        print(f"   Momentos especiales: {len(insights.get('momentos_especiales', []))}")
        
        if insights.get('lugares'):
            print(f"\n📍 LUGARES ENCONTRADOS:")
            for lugar in insights['lugares'][:5]:
                print(f"   • {lugar}")
        
        if insights.get('apodos'):
            print(f"\n💕 APODOS:")
            for apodo in insights['apodos'][:5]:
                print(f"   • {apodo}")
        
        print(f"\n💡 PREGUNTAS GENERADAS: {len(questions)}")
        for i, q in enumerate(questions[:3], 1):
            print(f"\n   {i}. {q.get('question', '')}")
            print(f"      Dificultad: {q.get('difficulty', 'N/A').upper()}")
        
        print("\n" + "="*70)
        print("✅ PRUEBA COMPLETADA")
        print("="*70)
        
        print(f"\n📄 ARCHIVOS DE PRUEBA GENERADOS:")
        print(f"   1. {test_output}")
        print(f"   2. {test_questions}")
        
        print(f"\n🎯 Si los resultados se ven bien:")
        print(f"   1. Ejecuta el análisis completo: python3 scripts/run_openai_analysis.py")
        print(f"   2. O aumenta max_messages en este script")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("💕 ROMANTIC AI - PRUEBA DE ANÁLISIS CON OPENAI")
    print("="*70)
    
    run_test_analysis()


if __name__ == "__main__":
    main()
