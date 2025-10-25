"""
RAG Service - Retrieval-Augmented Generation para búsqueda semántica en mensajes
Usa OpenAI Embeddings + FAISS para búsqueda vectorial eficiente
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from openai import OpenAI
import faiss

class RAGService:
    """
    Sistema RAG robusto para búsqueda semántica en mensajes de Instagram.
    
    Features:
    - Embeddings con OpenAI text-embedding-3-small (rápido y barato)
    - Vector store con FAISS (búsqueda eficiente en millones de vectores)
    - Cache persistente de embeddings (evita recálculo)
    - Búsqueda híbrida: semántica + filtros temporales/autor
    """
    
    def __init__(self, openai_api_key: str, cache_dir: str = "./cache"):
        self.client = OpenAI(api_key=openai_api_key)
        self.cache_dir = cache_dir
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dim = 1536  # Dimensión de text-embedding-3-small
        
        # Vector store
        self.index: Optional[faiss.IndexFlatL2] = None
        self.messages_metadata: List[Dict] = []
        
        # Cache
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "rag_embeddings.pkl")
        self.index_file = os.path.join(cache_dir, "faiss_index.bin")
        
        print(f"🚀 RAG Service inicializado (modelo: {self.embedding_model})")
    
    def _create_message_chunks(self, messages: List[Dict], chunk_size: int = 5) -> List[Dict]:
        """
        Agrupa mensajes en chunks para mejor contexto.
        En vez de 1 embedding por mensaje, agrupa N mensajes consecutivos.
        """
        chunks = []
        for i in range(0, len(messages), chunk_size):
            chunk_msgs = messages[i:i + chunk_size]
            
            # Combinar mensajes del chunk
            combined_text = []
            for msg in chunk_msgs:
                sender = msg.get('sender_name', 'Unknown')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp_ms', 0)
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d') if timestamp else 'unknown'
                
                combined_text.append(f"[{date}] {sender}: {content}")
            
            # Metadata del chunk
            first_msg = chunk_msgs[0]
            last_msg = chunk_msgs[-1]
            
            chunk_data = {
                'text': '\n'.join(combined_text),
                'chunk_id': i // chunk_size,
                'messages_in_chunk': chunk_msgs,
                'date_range': (
                    datetime.fromtimestamp(first_msg.get('timestamp_ms', 0) / 1000).strftime('%Y-%m-%d'),
                    datetime.fromtimestamp(last_msg.get('timestamp_ms', 0) / 1000).strftime('%Y-%m-%d')
                ),
                'message_count': len(chunk_msgs)
            }
            chunks.append(chunk_data)
        
        print(f"📦 Creados {len(chunks)} chunks de {chunk_size} mensajes cada uno")
        return chunks
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Obtiene embedding de OpenAI para un texto."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000]  # Límite de tokens
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        except Exception as e:
            print(f"❌ Error obteniendo embedding: {e}")
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def _get_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """Obtiene embeddings en batch (más eficiente)."""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_texts = [t[:8000] for t in batch]  # Truncar
            
            try:
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch_texts
                )
                batch_embeddings = [np.array(item.embedding, dtype=np.float32) for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                print(f"  📊 Procesados {i + len(batch)}/{len(texts)} embeddings...")
            except Exception as e:
                print(f"❌ Error en batch {i}: {e}")
                # Fallback: embeddings vacíos
                all_embeddings.extend([np.zeros(self.embedding_dim, dtype=np.float32)] * len(batch))
        
        return np.array(all_embeddings, dtype=np.float32)
    
    def build_index(self, messages: List[Dict], force_rebuild: bool = False):
        """
        Construye el índice FAISS con todos los mensajes.
        Si existe cache, lo carga. Si no, genera embeddings nuevos.
        """
        # Intentar cargar cache
        if not force_rebuild and os.path.exists(self.cache_file) and os.path.exists(self.index_file):
            print("📂 Cargando índice desde cache...")
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.messages_metadata = cache_data['metadata']
                
                self.index = faiss.read_index(self.index_file)
                print(f"✅ Cache cargado: {len(self.messages_metadata)} chunks, {self.index.ntotal} vectores")
                return
            except Exception as e:
                print(f"⚠️ Error cargando cache: {e}. Reconstruyendo...")
        
        # Construir índice desde cero
        print(f"🏗️ Construyendo índice FAISS para {len(messages)} mensajes...")
        
        # 1. Crear chunks de mensajes
        chunks = self._create_message_chunks(messages, chunk_size=5)
        self.messages_metadata = chunks
        
        # 2. Extraer textos para embeddings
        chunk_texts = [chunk['text'] for chunk in chunks]
        
        # 3. Generar embeddings en batch
        print(f"🧮 Generando {len(chunk_texts)} embeddings...")
        embeddings = self._get_embeddings_batch(chunk_texts, batch_size=50)
        
        # 4. Crear índice FAISS
        print(f"🔨 Creando índice FAISS...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings)
        
        # 5. Guardar cache
        print(f"💾 Guardando cache...")
        with open(self.cache_file, 'wb') as f:
            pickle.dump({
                'metadata': self.messages_metadata,
                'created_at': datetime.now().isoformat()
            }, f)
        
        faiss.write_index(self.index, self.index_file)
        
        print(f"✅ Índice construido: {self.index.ntotal} vectores, {len(self.messages_metadata)} chunks")
    
    def search(
        self, 
        query: str, 
        k: int = 10,
        date_range: Optional[Tuple[str, str]] = None,
        sender_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Búsqueda semántica en los mensajes.
        
        Args:
            query: Texto de búsqueda (ej: "momentos románticos", "apodos cariñosos")
            k: Número de resultados a devolver
            date_range: Tupla (fecha_inicio, fecha_fin) para filtrar por fechas
            sender_filter: Nombre del remitente para filtrar
        
        Returns:
            Lista de chunks relevantes con sus mensajes
        """
        if self.index is None:
            raise ValueError("Índice no construido. Llama a build_index() primero.")
        
        # 1. Generar embedding de la query
        query_embedding = self._get_embedding(query).reshape(1, -1)
        
        # 2. Buscar k vecinos más cercanos
        distances, indices = self.index.search(query_embedding, k * 2)  # Buscar más para filtrar
        
        # 3. Recuperar chunks y aplicar filtros
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= len(self.messages_metadata):
                continue
            
            chunk = self.messages_metadata[int(idx)]
            
            # Aplicar filtros
            if date_range:
                chunk_start, chunk_end = chunk['date_range']
                if chunk_end < date_range[0] or chunk_start > date_range[1]:
                    continue
            
            if sender_filter:
                # Verificar si algún mensaje del chunk es del sender
                has_sender = any(
                    msg.get('sender_name') == sender_filter 
                    for msg in chunk['messages_in_chunk']
                )
                if not has_sender:
                    continue
            
            results.append({
                **chunk,
                'similarity_score': float(distance),
                'rank': len(results) + 1
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def search_romantic_moments(self, k: int = 10) -> List[Dict]:
        """Búsqueda especializada de momentos románticos."""
        queries = [
            "te amo te quiero amor cariño",
            "primera vez primer beso aniversario",
            "extraño necesito pensando en ti",
            "siempre juntos para siempre futuro"
        ]
        
        all_results = []
        for query in queries:
            results = self.search(query, k=k // len(queries) + 1)
            all_results.extend(results)
        
        # Eliminar duplicados y ordenar por score
        seen_ids = set()
        unique_results = []
        for r in all_results:
            if r['chunk_id'] not in seen_ids:
                seen_ids.add(r['chunk_id'])
                unique_results.append(r)
        
        unique_results.sort(key=lambda x: x['similarity_score'])
        return unique_results[:k]
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del RAG."""
        if not self.messages_metadata:
            return {}
        
        total_messages = sum(chunk['message_count'] for chunk in self.messages_metadata)
        
        return {
            'total_chunks': len(self.messages_metadata),
            'total_messages': total_messages,
            'total_vectors': self.index.ntotal if self.index else 0,
            'embedding_model': self.embedding_model,
            'embedding_dimension': self.embedding_dim,
            'cache_exists': os.path.exists(self.cache_file),
            'index_size_mb': os.path.getsize(self.index_file) / 1024 / 1024 if os.path.exists(self.index_file) else 0
        }
    
    def extract_romantic_patterns(self) -> Dict:
        """
        Extrae patrones románticos de los mensajes indexados.
        Usa búsqueda semántica para encontrar los más relevantes.
        """
        patterns = {
            'apodos': self.search("apodos cariñosos amor bebé mi vida", k=5),
            'frases_amor': self.search("te amo te quiero te extraño", k=5),
            'lugares_especiales': self.search("parque playa cine restaurante nuestro lugar", k=5),
            'momentos_especiales': self.search("primera vez primer beso aniversario recuerdo especial", k=5),
            'planes_futuro': self.search("futuro juntos siempre casarnos vivir juntos", k=5)
        }
        
        return patterns


# Singleton global
_rag_instance: Optional[RAGService] = None

def get_rag_service(openai_api_key: str) -> RAGService:
    """Obtiene la instancia singleton del RAG service."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService(openai_api_key)
    return _rag_instance
