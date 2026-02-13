class MemoryManager:
    def __init__(self):
        # Placeholder for ChromaDB or FAISS
        self.memory = []

    def save_context(self, user_input, assistant_response):
        self.memory.append({"user": user_input, "assistant": assistant_response})

    def retrieve_context(self):
        if not self.memory:
            return None
        return self.memory[-1]
