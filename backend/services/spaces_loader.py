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
        cache_files = ['rag_embeddings.pkl', 'faiss_index.bin']
        all_messages = []
        
        print(f"📡 Descargando datos desde DigitalOcean Spaces...")
        print(f"🌐 URL base: {self.spaces_url}")
        
        # Primero descargar archivos de cache (embeddings pre-calculados)
        print(f"💾 Descargando cache pre-calculado...")
        cache_dir = Path('cache')
        cache_dir.mkdir(exist_ok=True)
        
        for cache_file in cache_files:
            try:
                cache_url = f"{self.spaces_url}/{cache_file}"
                print(f"📥 Descargando {cache_file}...")
                
                response = requests.get(cache_url, timeout=60)
                response.raise_for_status()
                
                # Guardar en cache directory
                local_cache_file = cache_dir / cache_file
                with open(local_cache_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"  ✅ Cache guardado: {local_cache_file} ({len(response.content) / 1024 / 1024:.1f}MB)")
                
            except Exception as e:
                print(f"  ⚠️ Error descargando cache {cache_file}: {e}")
        
        # Luego descargar archivos JSON
        print(f"📄 Descargando archivos JSON...")
        
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
        
        print(f"🎯 Total de mensajes cargados: {len(all_messages)}")
        return all_messages
    
    def download_priority_transcription(self):
        """Descarga y procesa los chunks prioritarios de la transcripción"""
        try:
            transcription_url = f"{self.spaces_url}/priority_transcription.json"
            print(f"📚 Descargando chunks prioritarios de transcripción...")
            
            response = requests.get(transcription_url, timeout=30)
            response.raise_for_status()
            
            # Guardar en cache local
            cache_file = self.cache_dir / "priority_transcription.json"
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            # Parsear datos prioritarios
            priority_data = json.loads(response.content)
            chunks = priority_data.get('chunks', [])
            
            print(f"  ✅ {len(chunks)} chunks prioritarios cargados")
            
            # Convertir chunks a formato de mensajes para RAG
            priority_messages = []
            for chunk in chunks:
                priority_message = {
                    'content': chunk['content'],
                    'timestamp_ms': 0,  # Prioridad máxima
                    'sender_name': 'PRIORITY_HISTORY',
                    'type': 'priority_chunk',
                    'metadata': chunk['metadata'],
                    'priority_score': chunk['metadata'].get('priority_score', 10)
                }
                priority_messages.append(priority_message)
            
            print(f"🚀 Chunks prioritarios listos para RAG")
            return priority_messages
            
        except Exception as e:
            print(f"❌ Error cargando chunks prioritarios: {e}")
            return []
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