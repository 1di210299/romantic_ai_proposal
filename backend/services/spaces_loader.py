"""
DigitalOcean Spaces data loader
Descarga archivos JSON desde DigitalOcean Spaces
"""
import os
import json
import requests
from pathlib import Path
import time

class SpacesDataLoader:
    def __init__(self, spaces_url=None):
        # URL del Space (será configurada via environment variable)
        self.spaces_url = spaces_url or os.getenv('SPACES_DATA_URL', 'https://romantic-ai-data.nyc3.digitaloceanspaces.com')
        self.cache_dir = Path('data_cache')
        self.cache_dir.mkdir(exist_ok=True)
        
    def download_conversation_files(self):
        """Descarga todos los archivos de conversación desde Spaces"""
        files = ['message_1.json', 'message_2.json', 'message_3.json', 'message_4.json']
        all_messages = []
        
        print(f"📡 Descargando datos desde DigitalOcean Spaces...")
        print(f"🌐 URL base: {self.spaces_url}")
        
        for filename in files:
            try:
                # URL completa del archivo
                file_url = f"{self.spaces_url}/{filename}"
                print(f"📥 Descargando {filename}...")
                
                # Descargar archivo
                response = requests.get(file_url, timeout=30)
                response.raise_for_status()
                
                # Guardar en cache local
                cache_file = self.cache_dir / filename
                with open(cache_file, 'wb') as f:
                    f.write(response.content)
                
                # Parsear JSON y extraer mensajes
                data = json.loads(response.content)
                messages = data.get('messages', [])
                all_messages.extend(messages)
                
                print(f"  ✅ {len(messages)} mensajes desde {filename}")
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error descargando {filename}: {e}")
                
                # Intentar usar cache local si existe
                cache_file = self.cache_dir / filename
                if cache_file.exists():
                    print(f"  🔄 Usando cache local: {filename}")
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            messages = data.get('messages', [])
                            all_messages.extend(messages)
                            print(f"    ✅ {len(messages)} mensajes desde cache")
                    except Exception as cache_error:
                        print(f"    ❌ Error leyendo cache: {cache_error}")
                        
            except Exception as e:
                print(f"  ❌ Error procesando {filename}: {e}")
        
        print(f"📊 Total mensajes cargados desde Spaces: {len(all_messages)}")
        return all_messages
    
    def test_connection(self):
        """Prueba la conexión a Spaces"""
        try:
            test_url = f"{self.spaces_url}/message_1.json"
            response = requests.head(test_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Conexión a Spaces exitosa")
                return True
            else:
                print(f"❌ Spaces responde {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error conectando a Spaces: {e}")
            return False

def load_messages_from_spaces():
    """Función helper para cargar mensajes desde Spaces"""
    loader = SpacesDataLoader()
    
    # Probar conexión primero
    if not loader.test_connection():
        print("⚠️  Spaces no disponible, usando método fallback...")
        return []
    
    return loader.download_conversation_files()