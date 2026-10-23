from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from core.config import settings
from google import genai
from openai import AsyncOpenAI
import os
import uuid

class MemoryService:
    _qdrant_client = None

    @staticmethod
    def get_qdrant_client():
        if MemoryService._qdrant_client is None:
            # Persistent storage path for Qdrant local database
            if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
                db_path = "/tmp/qdrant_db"
            else:
                db_path = os.path.join(os.path.dirname(__file__), "..", "qdrant_db")
            MemoryService._qdrant_client = QdrantClient(path=db_path)
        return MemoryService._qdrant_client

    @staticmethod
    async def get_embeddings(text: str) -> list:
        """
        Generate text embeddings using Google GenAI API (preferred) or OpenAI API.
        Returns a list of floats representing the embedding vector.
        """
        if not text:
            return []

        # Try Google GenAI API first
        if getattr(settings, "GEMINI_API_KEY", None) and settings.GEMINI_API_KEY.strip():
            try:
                # Use new google-genai SDK
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                response = await client.aio.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                if response and response.embeddings:
                    return response.embeddings[0].values
            except Exception as e:
                print(f"[MEMORY_SERVICE_WARNING]: Gemini embedding failure: {e}")

        # Try OpenAI API second
        if getattr(settings, "OPENAI_API_KEY", None) and settings.OPENAI_API_KEY.strip():
            try:
                client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                response = await client.embeddings.create(
                    input=[text],
                    model="text-embedding-3-small"
                )
                if response and response.data:
                    return response.data[0].embedding
            except Exception as e:
                print(f"[MEMORY_SERVICE_WARNING]: OpenAI embedding failure: {e}")

        # Fallback dummy embedding if no key is configured
        print("[MEMORY_SERVICE]: No API key configured for embeddings. Using fallback.")
        return [0.0] * 128

    @staticmethod
    async def add_memory(user_id: str, content: str):
        """
        Store a message content along with its vector embedding in Qdrant.
        """
        if not user_id or not content or len(content.strip()) < 5:
            return

        try:
            embedding = await MemoryService.get_embeddings(content)
            if not embedding:
                return

            client = MemoryService.get_qdrant_client()
            collection_name = "shadow_memories"
            
            # Check collection size mismatch or create new
            exists = False
            try:
                info = client.get_collection(collection_name)
                if info.config.params.vectors.size != len(embedding):
                    client.delete_collection(collection_name)
                else:
                    exists = True
            except Exception:
                pass
                
            if not exists:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=len(embedding), distance=Distance.COSINE)
                )

            point_id = str(uuid.uuid4())
            client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={"user_id": user_id, "content": content}
                    )
                ]
            )
            print(f"[MEMORY_SERVICE]: Successfully archived vector memory to Qdrant for user {user_id}")
        except Exception as e:
            print(f"[MEMORY_SERVICE_ERROR]: Failed to store vector memory in Qdrant: {e}")

    @staticmethod
    async def get_relevant_context(user_id: str, query: str, limit: int = 2) -> list:
        """
        Retrieve relevant context from Qdrant using semantic vector similarity.
        """
        if not user_id or not query:
            return []

        try:
            query_vector = await MemoryService.get_embeddings(query)
            if not query_vector:
                return []

            client = MemoryService.get_qdrant_client()
            collection_name = "shadow_memories"
            
            if not client.collection_exists(collection_name):
                return []
                
            if hasattr(client, "query_points"):
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                search_res = client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    query_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
                    limit=limit,
                    score_threshold=0.35
                )
                return [p.payload["content"] for p in search_res.points if p.payload and "content" in p.payload]
            elif hasattr(client, "search"):
                search_result = client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    query_filter={
                        "must": [
                            {
                                "key": "user_id",
                                "match": {
                                    "value": user_id
                                }
                            }
                        ]
                    },
                    limit=limit,
                    score_threshold=0.35
                )
                return [hit.payload["content"] for hit in search_result if hit.payload and "content" in hit.payload]
            return []
        except Exception as e:
            print(f"[MEMORY_SERVICE_ERROR]: Retrieval from Qdrant failed: {e}")
            return []
