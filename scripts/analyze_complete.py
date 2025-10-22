"""
Analizador COMPLETO de conversación de Instagram.
Procesa: Mensajes de texto (JSON), Imágenes (metadatos + Vision AI), Audios (Whisper transcription).

Este script te dará un análisis profundo de tu relación basado en TODA la data disponible.
"""

import json
import os
from datetime import datetime
from collections import Counter
from typing import Dict, List, Tuple
import re
from pathlib import Path

# Para análisis de imágenes
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️  PIL/Pillow no disponible. Instala con: pip install Pillow")

# Para OpenAI (Vision + Whisper)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI no disponible. Instala con: pip install openai")


class RelationshipAnalyzer:
    """Analizador completo de relación con soporte para texto, imágenes y audio."""
    
    def __init__(self, conversation_path: str, openai_api_key: str = None):
        """
        Initialize analyzer.
        
        Args:
            conversation_path: Ruta a la carpeta karemramos_XXXX
            openai_api_key: API key de OpenAI (opcional, para análisis avanzado)
        """
        self.conversation_path = Path(conversation_path)
        self.openai_client = None
        
        if openai_api_key and OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        self.analysis_results = {
            "messages": {},
            "images": {},
            "audios": {},
            "summary": {}
        }
    
    # ============= ANÁLISIS DE MENSAJES (JSON) =============
    
    def analyze_messages(self, max_messages: int = None) -> Dict:
        """
        Analiza todos los archivos message_*.json.
        
        Args:
            max_messages: Limitar análisis a N mensajes (None = todos)
        
        Returns:
            Diccionario con análisis de mensajes
        """
        print("\n" + "="*70)
        print("📨 ANALIZANDO MENSAJES DE TEXTO")
        print("="*70)
        
        all_messages = []
        message_files = sorted(self.conversation_path.glob("message_*.json"))
        
        for msg_file in message_files:
            print(f"   Cargando {msg_file.name}...")
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = data.get('messages', [])
                all_messages.extend(messages)
        
        if max_messages:
            all_messages = all_messages[:max_messages]
        
        print(f"✓ Total de mensajes cargados: {len(all_messages)}")
        
        # Separar por remitente
        juan_msgs = [m for m in all_messages if 'Juan Diego' in m.get('sender_name', '')]
        karem_msgs = [m for m in all_messages if 'Karem' in m.get('sender_name', '')]
        
        # Análisis temporal
        dates = []
        for msg in all_messages:
            if msg.get('timestamp_ms'):
                dt = datetime.fromtimestamp(msg['timestamp_ms'] / 1000)
                dates.append(dt)
        
        first_date = min(dates) if dates else None
        last_date = max(dates) if dates else None
        
        # Extraer contenido de texto
        text_messages = [m for m in all_messages if m.get('content')]
        all_text = " ".join([m['content'] for m in text_messages])
        
        # Buscar ubicaciones mencionadas
        location_keywords = [
            'café', 'cafetería', 'restaurante', 'parque', 'plaza',
            'cine', 'centro', 'mall', 'casa', 'depa', 'departamento',
            'bar', 'playa', 'montaña', 'universidad', 'trabajo',
            'gimnasio', 'hospital', 'aeropuerto', 'terminal'
        ]
        
        location_mentions = []
        for msg in text_messages:
            content_lower = msg.get('content', '').lower()
            for keyword in location_keywords:
                if keyword in content_lower:
                    location_mentions.append({
                        'date': datetime.fromtimestamp(msg['timestamp_ms'] / 1000).strftime('%Y-%m-%d'),
                        'sender': msg['sender_name'],
                        'keyword': keyword,
                        'context': msg['content'][:150]
                    })
        
        # Buscar fechas importantes mencionadas
        date_pattern = r'\b\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b'
        date_mentions = []
        
        for msg in text_messages:
            content = msg.get('content', '')
            matches = re.findall(date_pattern, content, re.IGNORECASE)
            if matches:
                date_mentions.append({
                    'date': datetime.fromtimestamp(msg['timestamp_ms'] / 1000).strftime('%Y-%m-%d'),
                    'sender': msg['sender_name'],
                    'mention': content
                })
        
        # Palabras más frecuentes
        words = re.findall(r'\b\w+\b', all_text.lower())
        # Filtrar palabras comunes en español
        stop_words = {'que', 'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 
                     'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'es', 'lo', 
                     'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha',
                     'si', 'me', 'te', 'mi', 'tu', 'yo', 'ti', 'eso', 'si', 'bien'}
        
        filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
        word_freq = Counter(filtered_words)
        common_words = word_freq.most_common(30)
        
        # Buscar apodos cariñosos
        affection_patterns = [
            r'\b(amor|amorcito|mi amor|bb|bebe|bebé|nena|nene|cielo|vida|corazón)\b',
            r'\b(hermosa|hermoso|linda|lindo|preciosa|precioso|reina|rey)\b',
            r'\b(mi vida|mi cielo|mi todo|gordita|gordito|flaca|flaco)\b'
        ]
        
        nicknames = []
        for msg in text_messages:
            content = msg.get('content', '').lower()
            for pattern in affection_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                nicknames.extend(matches)
        
        nickname_freq = Counter(nicknames)
        
        print(f"✓ Mensajes de Juan: {len(juan_msgs)}")
        print(f"✓ Mensajes de Karem: {len(karem_msgs)}")
        print(f"✓ Ubicaciones mencionadas: {len(location_mentions)}")
        print(f"✓ Fechas importantes: {len(date_mentions)}")
        print(f"✓ Apodos encontrados: {len(nickname_freq)}")
        
        self.analysis_results['messages'] = {
            'total_messages': len(all_messages),
            'juan_messages': len(juan_msgs),
            'karem_messages': len(karem_msgs),
            'first_message_date': first_date.isoformat() if first_date else None,
            'last_message_date': last_date.isoformat() if last_date else None,
            'conversation_days': (last_date - first_date).days if (first_date and last_date) else 0,
            'location_mentions': location_mentions[:50],
            'date_mentions': date_mentions[:30],
            'common_words': common_words,
            'nicknames': dict(nickname_freq.most_common(10)),
            'sample_juan_messages': [m.get('content', '') for m in juan_msgs[:10] if m.get('content')],
            'sample_karem_messages': [m.get('content', '') for m in karem_msgs[:10] if m.get('content')]
        }
        
        return self.analysis_results['messages']
    
    # ============= ANÁLISIS DE IMÁGENES =============
    
    def analyze_images(self, max_images: int = 50, use_vision_api: bool = False) -> Dict:
        """
        Analiza metadatos de imágenes y opcionalmente usa Vision API.
        
        Args:
            max_images: Número máximo de imágenes a analizar
            use_vision_api: Si True, usa OpenAI Vision para análisis profundo
        
        Returns:
            Diccionario con análisis de imágenes
        """
        print("\n" + "="*70)
        print("🖼️  ANALIZANDO IMÁGENES")
        print("="*70)
        
        photos_dir = self.conversation_path / "photos"
        
        if not photos_dir.exists():
            print("✗ No se encontró carpeta de fotos")
            return {}
        
        image_files = list(photos_dir.glob("*.jpg")) + list(photos_dir.glob("*.png"))
        total_images = len(image_files)
        
        print(f"✓ Total de imágenes encontradas: {total_images}")
        print(f"   Analizando primeras {min(max_images, total_images)} imágenes...")
        
        if not PILLOW_AVAILABLE:
            print("⚠️  Análisis de imágenes limitado sin Pillow")
            return {'total_images': total_images, 'analyzed': 0}
        
        image_analysis = []
        
        for i, img_file in enumerate(image_files[:max_images]):
            try:
                with Image.open(img_file) as img:
                    # Extraer metadatos EXIF
                    exif_data = {}
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            exif_data[tag] = str(value)
                    
                    img_info = {
                        'filename': img_file.name,
                        'size': img.size,
                        'format': img.format,
                        'mode': img.mode,
                        'date_taken': exif_data.get('DateTime', None),
                        'gps_info': exif_data.get('GPSInfo', None)
                    }
                    
                    # Análisis con Vision API (opcional, costoso)
                    if use_vision_api and self.openai_client and i < 10:  # Solo primeras 10
                        print(f"   Analizando {img_file.name} con Vision AI...")
                        vision_result = self._analyze_image_with_vision(img_file)
                        img_info['vision_analysis'] = vision_result
                    
                    image_analysis.append(img_info)
                
                if (i + 1) % 10 == 0:
                    print(f"   Procesadas {i + 1}/{min(max_images, total_images)} imágenes...")
            
            except Exception as e:
                print(f"   ✗ Error procesando {img_file.name}: {e}")
        
        print(f"✓ Análisis de imágenes completado: {len(image_analysis)} procesadas")
        
        self.analysis_results['images'] = {
            'total_images': total_images,
            'analyzed_images': len(image_analysis),
            'images_with_dates': sum(1 for img in image_analysis if img.get('date_taken')),
            'images_with_gps': sum(1 for img in image_analysis if img.get('gps_info')),
            'image_details': image_analysis
        }
        
        return self.analysis_results['images']
    
    def _analyze_image_with_vision(self, image_path: Path) -> str:
        """Analiza imagen con OpenAI Vision API."""
        try:
            import base64
            
            with open(image_path, 'rb') as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe brevemente esta imagen en español: ¿Qué se ve? ¿Dónde podría ser? ¿Qué actividad?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }],
                max_tokens=100
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    # ============= ANÁLISIS DE AUDIOS =============
    
    def analyze_audios(self, max_audios: int = 20, transcribe: bool = False) -> Dict:
        """
        Analiza archivos de audio y opcionalmente transcribe con Whisper.
        
        Args:
            max_audios: Número máximo de audios a procesar
            transcribe: Si True, transcribe audios con Whisper API (COSTOSO)
        
        Returns:
            Diccionario con análisis de audios
        """
        print("\n" + "="*70)
        print("🎤 ANALIZANDO AUDIOS")
        print("="*70)
        
        audio_dir = self.conversation_path / "audio"
        
        if not audio_dir.exists():
            print("✗ No se encontró carpeta de audios")
            return {}
        
        audio_files = list(audio_dir.glob("*.mp4")) + list(audio_dir.glob("*.m4a"))
        total_audios = len(audio_files)
        
        print(f"✓ Total de audios encontrados: {total_audios}")
        print(f"   Analizando primeros {min(max_audios, total_audios)} audios...")
        
        audio_analysis = []
        transcriptions = []
        
        for i, audio_file in enumerate(audio_files[:max_audios]):
            try:
                file_stats = audio_file.stat()
                
                audio_info = {
                    'filename': audio_file.name,
                    'size_kb': round(file_stats.st_size / 1024, 2),
                    'modified_date': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                }
                
                # Transcripción con Whisper (opcional, MUY costoso con 4903 audios)
                if transcribe and self.openai_client and i < 5:  # Solo primeros 5
                    print(f"   Transcribiendo {audio_file.name}...")
                    transcription = self._transcribe_audio(audio_file)
                    audio_info['transcription'] = transcription
                    transcriptions.append(transcription)
                
                audio_analysis.append(audio_info)
                
                if (i + 1) % 10 == 0:
                    print(f"   Procesados {i + 1}/{min(max_audios, total_audios)} audios...")
            
            except Exception as e:
                print(f"   ✗ Error procesando {audio_file.name}: {e}")
        
        print(f"✓ Análisis de audios completado: {len(audio_analysis)} procesados")
        
        self.analysis_results['audios'] = {
            'total_audios': total_audios,
            'analyzed_audios': len(audio_analysis),
            'total_size_mb': round(sum(a['size_kb'] for a in audio_analysis) / 1024, 2),
            'transcriptions_count': len(transcriptions),
            'audio_details': audio_analysis,
            'sample_transcriptions': transcriptions[:10]
        }
        
        return self.analysis_results['audios']
    
    def _transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio con Whisper API."""
        try:
            with open(audio_path, 'rb') as audio_file:
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            
            return transcription.text
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    # ============= GENERACIÓN DE RESUMEN Y SUGERENCIAS =============
    
    def generate_summary(self) -> Dict:
        """Genera resumen completo y sugerencias de preguntas."""
        print("\n" + "="*70)
        print("📊 GENERANDO RESUMEN Y SUGERENCIAS")
        print("="*70)
        
        messages = self.analysis_results.get('messages', {})
        images = self.analysis_results.get('images', {})
        audios = self.analysis_results.get('audios', {})
        
        # Sugerencias de preguntas basadas en el análisis
        suggestions = []
        
        # De ubicaciones
        if messages.get('location_mentions'):
            top_locations = Counter([loc['keyword'] for loc in messages['location_mentions']])
            for location, count in top_locations.most_common(3):
                suggestions.append({
                    'type': 'location',
                    'question': f"¿Recuerdas la primera vez que fuimos a [{location}]?",
                    'source': 'text_analysis',
                    'confidence': 'high' if count > 5 else 'medium'
                })
        
        # De fechas
        if messages.get('date_mentions'):
            suggestions.append({
                'type': 'date',
                'question': "¿Qué día nos conocimos por primera vez?",
                'source': 'text_analysis',
                'confidence': 'high'
            })
        
        # De apodos
        if messages.get('nicknames'):
            top_nickname = list(messages['nicknames'].keys())[0]
            suggestions.append({
                'type': 'nickname',
                'question': f"¿Cuál es mi apodo favorito para ti?",
                'hint': f"Relacionado con '{top_nickname}'",
                'source': 'text_analysis',
                'confidence': 'high'
            })
        
        # De imágenes
        if images.get('images_with_dates', 0) > 0:
            suggestions.append({
                'type': 'memory',
                'question': "¿Recuerdas nuestra primera foto juntos?",
                'source': 'image_analysis',
                'confidence': 'medium'
            })
        
        # De audios
        if audios.get('total_audios', 0) > 100:
            suggestions.append({
                'type': 'audio_memory',
                'question': "¿Qué fue lo primero que te dije en un audio?",
                'source': 'audio_analysis',
                'confidence': 'medium'
            })
        
        summary = {
            'relationship_stats': {
                'total_messages': messages.get('total_messages', 0),
                'total_images': images.get('total_images', 0),
                'total_audios': audios.get('total_audios', 0),
                'conversation_span_days': messages.get('conversation_days', 0),
                'first_interaction': messages.get('first_message_date'),
                'juan_participation': f"{messages.get('juan_messages', 0) / max(messages.get('total_messages', 1), 1) * 100:.1f}%",
                'karem_participation': f"{messages.get('karem_messages', 0) / max(messages.get('total_messages', 1), 1) * 100:.1f}%"
            },
            'content_richness': {
                'unique_locations': len(set(loc['keyword'] for loc in messages.get('location_mentions', []))),
                'important_dates_mentioned': len(messages.get('date_mentions', [])),
                'affection_terms_used': len(messages.get('nicknames', {})),
                'photos_with_metadata': images.get('images_with_dates', 0),
                'estimated_audio_hours': round(audios.get('total_size_mb', 0) / 10, 1)  # Estimado
            },
            'quiz_suggestions': suggestions,
            'recommended_questions_count': len(suggestions)
        }
        
        self.analysis_results['summary'] = summary
        
        print(f"✓ Resumen generado con {len(suggestions)} sugerencias de preguntas")
        
        return summary
    
    def save_results(self, output_file: str = "data/complete_relationship_analysis.json"):
        """Guarda todos los resultados del análisis."""
        print(f"\n💾 Guardando resultados en {output_file}...")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        output_data = {
            'generated_at': datetime.now().isoformat(),
            'analysis_version': '2.0_complete',
            'source': 'Instagram DM + Photos + Audios',
            'results': self.analysis_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, indent=2, fp=f, ensure_ascii=False)
        
        print(f"✓ Resultados guardados exitosamente")


def main():
    """Función principal de ejecución."""
    print("\n" + "="*70)
    print("💕 ROMANTIC AI - ANALIZADOR COMPLETO DE RELACIÓN")
    print("   (Mensajes + Imágenes + Audios)")
    print("="*70 + "\n")
    
    # Configuración
    conversation_path = "karemramos_1184297046409691"
    
    if not os.path.exists(conversation_path):
        print(f"✗ Error: No se encontró la carpeta {conversation_path}")
        print("\nAsegúrate de estar en: romantic_ai_proposal/")
        return
    
    # Preguntar por OpenAI API key
    print("🔑 Configuración de OpenAI API:")
    print("   Necesaria para: Vision API (análisis de fotos) y Whisper (transcripción audios)")
    use_openai = input("\n¿Tienes OpenAI API key y quieres usarla? (s/n): ").strip().lower() == 's'
    
    api_key = None
    if use_openai:
        api_key = input("Ingresa tu API key (o déjalo vacío para usar variable de entorno): ").strip()
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
    
    # Inicializar analizador
    analyzer = RelationshipAnalyzer(conversation_path, api_key)
    
    # PASO 1: Analizar mensajes de texto
    print("\n" + "-"*70)
    input("Presiona ENTER para analizar MENSAJES DE TEXTO...")
    analyzer.analyze_messages(max_messages=None)  # Todos los mensajes
    
    # PASO 2: Analizar imágenes
    print("\n" + "-"*70)
    use_vision = False
    if use_openai and api_key:
        use_vision = input("¿Analizar fotos con Vision AI? (s/n, costará ~$0.50-$1): ").strip().lower() == 's'
    
    input("\nPresiona ENTER para analizar IMÁGENES...")
    analyzer.analyze_images(max_images=50, use_vision_api=use_vision)
    
    # PASO 3: Analizar audios
    print("\n" + "-"*70)
    use_whisper = False
    if use_openai and api_key:
        print("⚠️  ADVERTENCIA: Transcribir 4903 audios costaría ~$200-300 USD")
        use_whisper = input("¿Transcribir algunos audios con Whisper? (s/n): ").strip().lower() == 's'
    
    input("\nPresiona ENTER para analizar AUDIOS...")
    analyzer.analyze_audios(max_audios=100, transcribe=use_whisper)
    
    # PASO 4: Generar resumen
    print("\n" + "-"*70)
    input("Presiona ENTER para GENERAR RESUMEN FINAL...")
    summary = analyzer.generate_summary()
    
    # PASO 5: Guardar resultados
    analyzer.save_results()
    
    # Mostrar resumen final
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70)
    
    stats = summary['relationship_stats']
    content = summary['content_richness']
    
    print(f"\n📊 ESTADÍSTICAS DE LA RELACIÓN:")
    print(f"   💬 Total de mensajes: {stats['total_messages']:,}")
    print(f"   🖼️  Total de fotos: {stats['total_images']}")
    print(f"   🎤 Total de audios: {stats['total_audios']}")
    print(f"   📅 Días de conversación: {stats['conversation_span_days']}")
    print(f"   🗓️  Primera interacción: {stats['first_interaction']}")
    
    print(f"\n💝 RIQUEZA DEL CONTENIDO:")
    print(f"   📍 Lugares únicos mencionados: {content['unique_locations']}")
    print(f"   🗓️  Fechas importantes: {content['important_dates_mentioned']}")
    print(f"   💕 Términos de cariño usados: {content['affection_terms_used']}")
    print(f"   📸 Fotos con metadatos: {content['photos_with_metadata']}")
    print(f"   ⏱️  Horas estimadas de audio: {content['estimated_audio_hours']}")
    
    print(f"\n💡 SUGERENCIAS GENERADAS:")
    print(f"   🎯 Total de preguntas sugeridas: {summary['recommended_questions_count']}")
    
    for i, suggestion in enumerate(summary['quiz_suggestions'][:5], 1):
        print(f"   {i}. [{suggestion['type']}] {suggestion['question']}")
    
    print(f"\n📄 Resultados completos guardados en: data/complete_relationship_analysis.json")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa data/complete_relationship_analysis.json")
    print("2. Usa las sugerencias para crear tus preguntas en data/questions.json")
    print("3. Personaliza el contexto del chatbot")
    print("4. ¡Prueba el sistema completo!\n")


if __name__ == "__main__":
    main()
