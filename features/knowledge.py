from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
from NOVA.core.logger import logger
import os

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    import pypdf
except ImportError:
    pypdf = None

# Single ChromaDB Instance Helper
_chroma_client = None
_chroma_collection = None

def get_knowledge_collection():
    global _chroma_client, _chroma_collection
    if not chromadb:
        return None
    if _chroma_collection:
        return _chroma_collection
    try:
        _chroma_client = chromadb.PersistentClient(path="./chroma_db")
        _chroma_collection = _chroma_client.get_or_create_collection(name="knowledge_base")
        return _chroma_collection
    except Exception as e:
        logger.error(f"ChromaDB Init Error: {e}")
        return None

class KnowledgeIngestionSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "KnowledgeIngestionSkill"
        self.intents = ["ingest_document"]
        self.description = "Use this ONLY when the user explicitly asks to SAVE, MEMORIZE, or ADD a new file to the database. Do NOT use for questions."
        self.slots = {
            "file_path": "Path to document to ingest"
        }

    def execute(self, entities: dict) -> SkillResponse:
        collection = get_knowledge_collection()
        if not collection:
             return SkillResponse(text="Knowledge Base unavailable (ChromaDB missing).", success=False)

        path = entities.get("file_path")
        if not path:
             return SkillResponse(text="Please provide a file path to read.", success=False)
             
        return self._ingest(collection, path)

    def _ingest(self, collection, path):
        if not os.path.exists(path):
             return SkillResponse(text=f"File not found: {path}", success=False)
        
        text = ""
        try:
             ext = path.lower().split('.')[-1]
             if ext == "pdf":
                 if not pypdf:
                     return SkillResponse(text="PDF support missing (pip install pypdf).", success=False)
                 reader = pypdf.PdfReader(path)
                 for page in reader.pages:
                     text += page.extract_text() + "\n"
             else:
                 with open(path, 'r', encoding='utf-8') as f:
                     text = f.read()
                     
             chunks = self._chunk_text(text)
             
             ids = [f"{os.path.basename(path)}_chunk_{i}" for i in range(len(chunks))]
             metadatas = [{"source": path, "chunk_index": i} for i in range(len(chunks))]
             
             collection.upsert(
                 documents=chunks,
                 ids=ids,
                 metadatas=metadatas
             )
             
             return SkillResponse(text=f"Successfully ingested {os.path.basename(path)} ({len(chunks)} chunks).")
             
        except Exception as e:
             return SkillResponse(text=f"Ingestion failed: {e}", success=False)

    def _chunk_text(self, text, chunk_size=500, overlap=50):
        chunks = []
        if not text: return []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

class KnowledgeRetrievalSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "KnowledgeRetrievalSkill"
        self.intents = ["query_knowledge"]
        self.description = "Use this when the user asks a QUESTION about a file or content. e.g. 'What is in requirements.txt?', 'Summarize the document'."
        self.slots = {
            "query": "The question to search for"
        }

    def execute(self, entities: dict) -> SkillResponse:
        collection = get_knowledge_collection()
        if not collection:
             return SkillResponse(text="Knowledge Base unavailable.", success=False)

        query = entities.get("query")
        if not query:
             return SkillResponse(text="What should I search for?", success=False)
             
        return self._query(collection, query)

    def _query(self, collection, query):
        try:
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if not results['documents'] or not results['documents'][0]:
                return SkillResponse(text="I couldn't find any relevant info in my knowledge base.")
                
            docs = results['documents'][0]
            context = "\n\n".join(docs)
            return SkillResponse(text=context, success=True)
            
        except Exception as e:
            return SkillResponse(text=f"Search failed: {e}", success=False)
