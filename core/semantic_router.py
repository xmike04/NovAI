import chromadb
from chromadb.utils import embedding_functions
import os

class SemanticRouter:
    def __init__(self, persistence_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persistence_path)
        # Default embedding function (all-MiniLM-L6-v2) is used if not specified
        self.collection = self.client.get_or_create_collection(name="intent_registry")
        
    def register_intent(self, intent_name, description, examples=None):
        """
        Registers an intent. 
        We treat the description (and optional examples) as documents for this intent.
        """
        docs = [description]
        ids = [f"{intent_name}_desc"]
        metadatas = [{"intent": intent_name, "type": "description"}]
        
        if examples:
            for i, ex in enumerate(examples):
                docs.append(ex)
                ids.append(f"{intent_name}_ex_{i}")
                metadatas.append({"intent": intent_name, "type": "example"})
        
        # Add to collection (upsert to overwrite if exists)
        self.collection.upsert(
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )

    def route(self, query, threshold=0.4):
        """
        Returns (intent_name, score) or (None, 0.0) if below threshold.
        Low distance = High similarity. Chroma returns distance.
        all-MiniLM-L6-v2 distances usually range 0 (identical) to 1.5+.
        Threshold of 0.4 distance is roughly 0.6 similarity? 
        Actually, let's just return the top match and let Manager decide.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=1
        )
        
        if not results['ids'] or not results['ids'][0]:
            return None, 0.0
            
        # Distance (cosine distance often, or L2)
        # Chroma default is L2. 
        # For L2, 0 is perfect. 
        distance = results['distances'][0][0]
        intent = results['metadatas'][0][0]['intent']
        
        # Convert distance to a "Confidence Score"
        # Rough heuristic: Score = 1 / (1 + distance)
        score = 1 / (1 + distance)
        
        return intent, score
