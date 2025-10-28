"""
Script para procesar y subir la transcripción completa a DigitalOcean Spaces
y generar embeddings prioritarios para el sistema RAG
"""
import os
import json
from pathlib import Path
import sys
from datetime import datetime

class TranscriptionProcessor:
    def __init__(self):
        self.spaces_url = os.getenv('SPACES_DATA_URL', 'https://romantic-ai-data.sfo3.digitaloceanspaces.com')
        
    def process_transcription(self, transcription_text):
        """Procesa la transcripción en chunks prioritarios para RAG"""
        
        # Dividir en eventos importantes con fechas
        priority_chunks = []
        
        # Chunk 1: Inicio de la relación (marzo 2025)
        chunk_1 = {
            "id": "transcription_inicio",
            "content": """Historia de Juan Diego y Karem - Inicio (Marzo 2025):
Empezaron a hablar aproximadamente en marzo de 2025 como amigos. Se juntaban con otra amiga, pero Juan Diego se sentía atraído hacia Karem. El primer beso fue un día viernes en una reunión con amigos del trabajo de su compañera. La conoció un miércoles, y después de eso se siguieron besando en reuniones y fiestas.""",
            "metadata": {
                "type": "priority_history",
                "period": "marzo_2025",
                "events": ["primer_encuentro", "primer_beso"],
                "priority_score": 10
            }
        }
        
        # Chunk 2: Primeros gestos románticos (julio 2025)
        chunk_2 = {
            "id": "transcription_flores",
            "content": """Primer regalo de flores (Julio 2025):
La primera vez que Juan Diego le regaló flores fue aproximadamente en julio. Fueron tulipanes amarillos a través de Rosatel. Hubo un problema con la entrega - se confundieron en la fecha y los entregaron un día antes cuando ella no estaba en casa. Juan Diego tuvo que llamar a Rosatel para que recogieran las flores y las entregaran el día correcto. En ese momento, Juan Diego estaba en Cusco por trabajo.""",
            "metadata": {
                "type": "priority_history", 
                "period": "julio_2025",
                "events": ["primer_regalo", "tulipanes_amarillos", "rosatel"],
                "priority_score": 9
            }
        }
        
        # Chunk 3: Oficialización de la relación (agosto 2025)
        chunk_3 = {
            "id": "transcription_noviazgo",
            "content": """Oficialización de la relación (Finales de Agosto 2025):
Aproximadamente el 23 de agosto o finales de agosto, Juan Diego fue a verla. Llegó en auto, le avisó que estaba ahí. Fue muy bonito, fueron a comer (lomo y otras cositas). Pasaron todo el día hablando de la vida, hablando de todo. Fue muy bonito y a Juan Diego le gustó bastante ese día. Ese día ella le contó que la persona con la que había salido antes le había pedido ser su pareja de cierta manera, pero a Juan Diego no le gustó la forma, así que decidió innovar: le compró flores y le hizo una página web especial para pedirle que fuera su novia.""",
            "metadata": {
                "type": "priority_history",
                "period": "agosto_2025", 
                "events": ["oficializacion", "pagina_web", "peticion_noviazgo"],
                "priority_score": 10
            }
        }
        
        # Chunk 4: Viajes juntos (septiembre 2025)
        chunk_4 = {
            "id": "transcription_viajes",
            "content": """Viajes y momentos especiales (Septiembre 2025):
Hicieron viajes juntos. Fueron a Chimbote, donde el primer beso en la playa fue en la tarde de un viernes, estaban abrazados. Dos semanas después vino a Lima, fueron al cine juntos por primera vez en septiembre. También fueron a Trujillo, era la primera vez que ella lo invitaba. Estuvieron en un cuarto, almorzaron, fueron a la playa y se quedaron viendo la playa un ratito, fue muy bonito. Conoció a Cristo (hermano de ella) y le cayó muy bien.""",
            "metadata": {
                "type": "priority_history",
                "period": "septiembre_2025",
                "events": ["chimbote", "primer_beso_playa", "cine_lima", "trujillo", "conocio_cristo"],
                "priority_score": 9
            }
        }
        
        # Chunk 5: Primera vez "te amo" y actualidad (octubre 2025)
        chunk_5 = {
            "id": "transcription_teamo",
            "content": """Primer "te amo" y actualidad (Octubre 2025):
En octubre, los primeros días, ella consiguió trabajo en Barviso. La primera vez que Juan Diego le dijo "te amo" fue el domingo 5 de octubre en la madrugada. Al día siguiente lo hablaron y todo salió bien. Fueron a comer, lo pasaron juntos. Hasta finales de octubre siguen viéndose, cada día la quiere más y la ama más. Es una relación que sigue creciendo con mucho amor.""",
            "metadata": {
                "type": "priority_history",
                "period": "octubre_2025",
                "events": ["trabajo_barviso", "primer_te_amo", "5_octubre", "relacion_actual"],
                "priority_score": 10
            }
        }
        
        priority_chunks.extend([chunk_1, chunk_2, chunk_3, chunk_4, chunk_5])
        
        return priority_chunks
    
    def upload_to_spaces(self, data, filename):
        """Sube datos procesados a DigitalOcean Spaces usando s3cmd"""
        
        # Crear archivo temporal
        temp_file = Path(f"/tmp/{filename}")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Subir usando s3cmd
        try:
            import subprocess
            result = subprocess.run([
                's3cmd', 'put', str(temp_file), 
                f's3://romantic-ai-data/{filename}',
                '--acl-public'
            ], capture_output=True, text=True, check=True)
            
            print(f"✅ Archivo subido exitosamente: {filename}")
            print(f"🌐 URL: {self.spaces_url}/{filename}")
            
            # Limpiar archivo temporal
            temp_file.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error subiendo {filename}: {e}")
            print(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Error general subiendo {filename}: {e}")
            return False

def main():
    """Función principal para procesar y subir la transcripción"""
    
    # Leer la transcripción
    transcription_file = Path("backend/data/historia_completa_transcripcion.txt")
    if not transcription_file.exists():
        print(f"❌ No se encuentra el archivo: {transcription_file}")
        return
    
    with open(transcription_file, 'r', encoding='utf-8') as f:
        transcription_text = f.read()
    
    # Procesar transcripción
    processor = TranscriptionProcessor()
    priority_chunks = processor.process_transcription(transcription_text)
    
    print(f"📚 Procesados {len(priority_chunks)} chunks prioritarios")
    
    # Crear archivo de chunks prioritarios
    priority_data = {
        "type": "priority_transcription",
        "created_at": datetime.now().isoformat(),
        "total_chunks": len(priority_chunks),
        "chunks": priority_chunks,
        "metadata": {
            "description": "Historia completa de Juan Diego y Karem procesada en chunks prioritarios",
            "usage": "Usar como contexto prioritario para generar preguntas personalizadas",
            "priority": "HIGH"
        }
    }
    
    # Subir a Spaces
    success = processor.upload_to_spaces(priority_data, "priority_transcription.json")
    
    if success:
        print("🎉 Transcripción procesada y subida exitosamente!")
        print("💡 Ahora el sistema RAG puede usar estos chunks prioritarios")
        print("📋 Los chunks incluyen:")
        for chunk in priority_chunks:
            events = ", ".join(chunk["metadata"]["events"])
            print(f"  - {chunk['metadata']['period']}: {events}")
    else:
        print("❌ Error procesando la transcripción")

if __name__ == "__main__":
    main()