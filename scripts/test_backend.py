#!/usr/bin/env python3
"""
Script de prueba para el backend.
Prueba todos los endpoints del API.
"""

import requests
import json
import time
import os

# Configuración
PORT = os.getenv('PORT', '5001')
BASE_URL = f"http://localhost:{PORT}/api"

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_separator():
    print("\n" + "="*70)

def test_health():
    """Prueba el endpoint de health check."""
    print_separator()
    print("🏥 TEST 1: Health Check")
    print_separator()
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✅ Status: {data['status']}")
            print(f"✅ Service: {data['service']}")
            print(f"✅ Version: {data['version']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("\n💡 Asegúrate de que el backend esté corriendo:")
        print("   cd backend")
        print("   python3 app.py")
        return False

def test_start_quiz():
    """Prueba el inicio de quiz (genera preguntas con OpenAI)."""
    print_separator()
    print("🚀 TEST 2: Iniciar Quiz (Genera preguntas con OpenAI)")
    print_separator()
    print("⚠️  NOTA: Esto hará una llamada a OpenAI (~$0.03-0.05)")
    print()
    
    confirm = input("¿Continuar con la prueba? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Prueba cancelada")
        return None
    
    print("\n🤖 Iniciando quiz y generando preguntas...")
    print("   (Esto puede tomar 10-30 segundos)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/start-quiz",
            json={"user_name": "Karem"},
            timeout=60  # Timeout de 60 segundos
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Quiz iniciado exitosamente!")
            print(f"✅ Session ID: {data['session_id'][:16]}...")
            print(f"✅ Total preguntas: {data['total_questions']}")
            print(f"\n📝 Mensaje de bienvenida:")
            print(f"   {data['message'][:200]}...")
            
            return data['session_id']
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
    except requests.Timeout:
        print(f"❌ Timeout: La generación de preguntas tomó demasiado tiempo")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_chat(session_id, message):
    """Prueba el endpoint de chat."""
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "session_id": session_id,
                "message": message
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def interactive_chat(session_id):
    """Chat interactivo con el bot."""
    print_separator()
    print("💬 TEST 3: Chat Interactivo")
    print_separator()
    print("Chatea con el bot. Escribe 'salir' para terminar.")
    print()
    
    # Primer mensaje: empezar
    print("Tú: sí")
    response = test_chat(session_id, "sí")
    
    if response:
        print(f"\nBot: {response['message']}")
        print(f"Pregunta {response['current_question']}/{response['total_questions']}")
    
    # Chat interactivo
    while True:
        print()
        user_input = input("Tú: ").strip()
        
        if user_input.lower() in ['salir', 'exit', 'quit']:
            print("👋 Saliendo del chat...")
            break
        
        if not user_input:
            continue
        
        response = test_chat(session_id, user_input)
        
        if response:
            print(f"\nBot: {response['message']}")
            
            if response.get('is_correct') == True:
                print("✅ ¡Respuesta correcta!")
            elif response.get('is_correct') == False:
                print("❌ Respuesta incorrecta")
            
            if not response.get('completed'):
                print(f"Pregunta {response.get('current_question')}/{response.get('total_questions')}")
            else:
                print("\n🎉 ¡Quiz completado!")
                break

def test_location(session_id):
    """Prueba obtener la ubicación final."""
    print_separator()
    print("📍 TEST 4: Obtener Ubicación Final")
    print_separator()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/get-location",
            json={"session_id": session_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ubicación revelada:")
            print(f"   Latitud: {data.get('latitude')}")
            print(f"   Longitud: {data.get('longitude')}")
            print(f"   Dirección: {data.get('address')}")
            print(f"\n📝 Mensaje:")
            print(f"   {data.get('message')}")
            return True
        elif response.status_code == 403:
            print(f"⚠️  Aún no se completaron todas las preguntas")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal."""
    print("\n" + "="*70)
    print("💕 ROMANTIC AI PROPOSAL - PRUEBA DE BACKEND")
    print("="*70)
    print()
    print("Este script probará que el backend funcione correctamente:")
    print("1. Health check")
    print("2. Generar preguntas con OpenAI")
    print("3. Chat interactivo")
    print("4. Ubicación final")
    print()
    
    # Test 1: Health
    if not test_health():
        return
    
    time.sleep(1)
    
    # Test 2: Start quiz (genera preguntas)
    session_id = test_start_quiz()
    
    if not session_id:
        print("\n❌ No se pudo iniciar el quiz")
        return
    
    time.sleep(1)
    
    # Test 3: Chat interactivo
    interactive_chat(session_id)
    
    # Test 4: Location (opcional)
    print()
    if input("¿Probar obtener ubicación? (s/n): ").strip().lower() == 's':
        test_location(session_id)
    
    print_separator()
    print("✅ PRUEBAS COMPLETADAS")
    print_separator()
    print()
    print("🎯 Próximos pasos:")
    print("   1. Si todo funcionó, el backend está listo")
    print("   2. Ahora necesitas crear el frontend")
    print("   3. O puedes probar con Postman/curl")
    print()

if __name__ == "__main__":
    main()
