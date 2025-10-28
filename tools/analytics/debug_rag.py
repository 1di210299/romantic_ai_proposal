#!/usr/bin/env python3
"""
Debug script para verificar que el sistema RAG esté funcionando correctamente
y generando preguntas basadas en datos reales
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_rag_question_generation():
    """Prueba la generación de preguntas con RAG"""
    
    print("🔍 Debugging RAG Question Generation")
    print("=" * 60)
    
    try:
        # Importar dependencias
        from app import generate_single_question_with_openai, rag_service
        from services.rag_service import get_rag_service
        from openai import OpenAI
        import json
        
        # Verificar OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("❌ OpenAI API key no encontrada")
            return False
        
        openai_client = OpenAI(api_key=openai_api_key)
        print(f"✅ OpenAI client configurado")
        
        # Verificar RAG service
        if not rag_service:
            print("❌ RAG service no inicializado")
            return False
        
        print(f"✅ RAG service inicializado")
        
        # Verificar datos en RAG
        if hasattr(rag_service, 'chunk_texts'):
            print(f"📊 Total chunks en RAG: {len(rag_service.chunk_texts):,}")
        
        if hasattr(rag_service, 'messages_metadata'):
            print(f"📊 Total metadata chunks: {len(rag_service.messages_metadata):,}")
        
        # Probar búsqueda RAG
        print("\n🔍 Probando búsqueda RAG:")
        test_queries = [
            "momento gracioso risa divertido",
            "viaje vacaciones lugar",
            "amor mi amor loca apodos"
        ]
        
        for query in test_queries:
            try:
                results = rag_service.search(query, k=5)
                print(f"  Query: '{query}' -> {len(results)} resultados")
                
                if results:
                    for i, result in enumerate(results[:2]):  # Solo primeros 2
                        messages_in_chunk = result.get('messages_in_chunk', [])
                        if messages_in_chunk:
                            first_msg = messages_in_chunk[0]
                            content = first_msg.get('content', '')[:100]
                            print(f"    [{i+1}] {content}...")
                        
            except Exception as e:
                print(f"    ❌ Error en query '{query}': {e}")
        
        # Probar generación de pregunta completa
        print("\n🤖 Probando generación de pregunta con OpenAI:")
        
        # Simular datos vacíos para forzar RAG
        test_messages = []
        
        question = generate_single_question_with_openai(
            messages=test_messages,
            question_number=1,
            previous_questions=None
        )
        
        print(f"📋 Pregunta generada:")
        print(f"  Pregunta: {question.get('question', 'N/A')}")
        print(f"  Opciones: {question.get('options', [])}")
        print(f"  Respuestas correctas: {question.get('correct_answers', [])}")
        print(f"  Categoría: {question.get('category', 'N/A')}")
        print(f"  Fuente de datos: {question.get('data_source', 'N/A')}")
        
        # Verificar si es genérica o específica
        generic_questions = [
            "¿Qué es lo que más nos hace reír",
            "¿Cuál es uno de los apodos",
            "¿Cuál es el apodo que más uso"
        ]
        
        is_generic = any(generic in question.get('question', '') for generic in generic_questions)
        
        if is_generic:
            print("⚠️  PROBLEMA: La pregunta parece genérica/hardcodeada")
            print("   Posibles causas:")
            print("   - RAG no encuentra datos relevantes")
            print("   - OpenAI está fallando")
            print("   - Está cayendo en el fallback")
        else:
            print("✅ La pregunta parece específica y basada en datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_rag_search():
    """Prueba búsquedas específicas en RAG"""
    
    print("\n🎯 Probando búsquedas específicas:")
    print("-" * 40)
    
    try:
        from app import rag_service
        
        # Búsquedas específicas que deberían tener resultados
        specific_searches = [
            "amor",
            "loca", 
            "mi amor",
            "te amo",
            "risa",
            "gracioso",
            "divertido"
        ]
        
        for search_term in specific_searches:
            try:
                results = rag_service.search(search_term, k=3)
                print(f"'{search_term}': {len(results)} resultados")
                
                if results:
                    # Mostrar un ejemplo
                    example = results[0]
                    messages = example.get('messages_in_chunk', [])
                    if messages:
                        sample_msg = messages[0].get('content', '')[:80]
                        print(f"  Ejemplo: {sample_msg}...")
                else:
                    print(f"  ❌ Sin resultados para '{search_term}'")
                    
            except Exception as e:
                print(f"  ❌ Error buscando '{search_term}': {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error en búsquedas específicas: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RAG Debug Suite")
    print("=" * 60)
    
    # Test 1: Generación de preguntas
    test1_ok = test_rag_question_generation()
    
    # Test 2: Búsquedas específicas
    test2_ok = test_specific_rag_search()
    
    print("\n" + "=" * 60)
    if test1_ok and test2_ok:
        print("🎉 Debug completado - Revisar resultados arriba")
    else:
        print("❌ Se encontraron problemas - Revisar errores arriba")
    print("=" * 60)