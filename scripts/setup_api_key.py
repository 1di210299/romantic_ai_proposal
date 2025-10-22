#!/usr/bin/env python3
"""
Helper para configurar la API key de OpenAI de forma interactiva.
"""

import os
from pathlib import Path


def setup_api_key():
    """Ayuda al usuario a configurar su API key."""
    
    print("\n" + "="*70)
    print("🔑 CONFIGURACIÓN DE OPENAI API KEY")
    print("="*70 + "\n")
    
    env_file = Path(".env")
    
    # Verificar si ya existe
    if env_file.exists():
        print("✅ Archivo .env encontrado\n")
        
        with open(env_file, 'r') as f:
            content = f.read()
            
        if 'OPENAI_API_KEY=sk-' in content:
            print("✅ Parece que ya tienes una API key configurada")
            print("\n¿Qué quieres hacer?")
            print("1. Verificar que funcione")
            print("2. Reemplazarla con una nueva")
            print("3. Salir")
            
            choice = input("\nOpción (1/2/3): ").strip()
            
            if choice == "1":
                return verify_api_key()
            elif choice == "2":
                pass  # Continuar al flujo de configuración
            else:
                return
        else:
            print("⚠️  API key no encontrada en .env")
    else:
        print("📝 Creando archivo .env nuevo...\n")
    
    print("📋 PASOS PARA OBTENER TU API KEY:\n")
    print("1. Abre en tu navegador: https://platform.openai.com/api-keys")
    print("2. Inicia sesión o crea una cuenta")
    print("3. Haz clic en 'Create new secret key'")
    print("4. Dale un nombre (ej: 'romantic-ai')")
    print("5. Copia la key (empieza con 'sk-proj-' o 'sk-')")
    print()
    print("⚠️  IMPORTANTE: También necesitas agregar créditos")
    print("   Ve a: https://platform.openai.com/account/billing")
    print("   Agrega al menos $5 USD")
    print()
    
    input("Presiona ENTER cuando tengas tu API key lista...")
    print()
    
    api_key = input("🔑 Pega tu API key aquí: ").strip()
    
    if not api_key:
        print("❌ No ingresaste ninguna key")
        return False
    
    if not (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
        print("⚠️  La key no tiene el formato correcto (debe empezar con 'sk-' o 'sk-proj-')")
        confirm = input("¿Continuar de todos modos? (s/n): ").strip().lower()
        if confirm != 's':
            return False
    
    # Leer el archivo .env actual o crear uno nuevo
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Reemplazar o agregar la API key
        found = False
        for i, line in enumerate(lines):
            if line.startswith('OPENAI_API_KEY='):
                lines[i] = f'OPENAI_API_KEY={api_key}\n'
                found = True
                break
        
        if not found:
            lines.insert(0, f'OPENAI_API_KEY={api_key}\n')
        
        content = ''.join(lines)
    else:
        content = f"""# OpenAI API Configuration
OPENAI_API_KEY={api_key}

# Flask Configuration
FLASK_DEBUG=True
FLASK_ENV=development
SECRET_KEY=dev-secret-key-romantic-ai-2025

# Final Location Configuration
FINAL_LATITUDE=19.4326
FINAL_LONGITUDE=-99.1332
FINAL_ADDRESS=Lugar especial donde estaré esperando
"""
    
    # Guardar
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("\n✅ API key guardada en .env")
    print()
    
    # Verificar que funcione
    return verify_api_key()


def verify_api_key():
    """Verifica que la API key funcione."""
    print("🔍 Verificando conexión con OpenAI...\n")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ API key no encontrada en .env")
            return False
        
        print(f"   Key: {api_key[:20]}...")
        
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("   Haciendo request de prueba...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Responde solo: OK"}
            ],
            max_tokens=5
        )
        
        result = response.choices[0].message.content
        
        print(f"   ✅ Respuesta recibida: {result}")
        print("\n✅ ¡API key funcionando correctamente!\n")
        
        print("🎯 PRÓXIMOS PASOS:")
        print("1. Ejecuta la prueba: python3 scripts/test_openai.py")
        print("2. Si funciona bien, ejecuta el análisis completo")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("💡 Posibles causas:")
        print("   • API key incorrecta")
        print("   • Sin créditos en tu cuenta de OpenAI")
        print("   • Problemas de conexión a internet")
        print()
        print("🔧 Soluciones:")
        print("   1. Verifica tu API key en: https://platform.openai.com/api-keys")
        print("   2. Verifica créditos en: https://platform.openai.com/account/billing")
        print("   3. Intenta generar una nueva API key")
        print()
        
        return False


def main():
    """Función principal."""
    success = setup_api_key()
    
    if success:
        print("="*70)
        print("✅ CONFIGURACIÓN COMPLETADA")
        print("="*70)
        print("\n🚀 Ahora puedes ejecutar:")
        print("   python3 scripts/test_openai.py")
        print()
    else:
        print("="*70)
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print("="*70)
        print("\n🔧 Revisa los errores arriba y vuelve a intentar")
        print()


if __name__ == "__main__":
    main()
