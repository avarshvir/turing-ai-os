import os
import chromadb
from chromadb.config import Settings
import datetime

class TuringMemory:
    def __init__(self):
        """
        Initializes the local Vector Database.
        It stores data directly on your SSD so the AI retains memory across reboots.
        """
        # Define the path where the memory database will live
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_data")
        os.makedirs(self.db_path, exist_ok=True)

        # Initialize the persistent client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Get or create a collection (table) for our sidebar chat history
        self.collection = self.client.get_or_create_collection(
            name="turing_sidebar_memory",
            metadata={"hnsw:space": "cosine"} # Mathematical method for finding similar memories
        )

    def save_memory(self, session_id: str, role: str, text: str):
        """
        Saves a single message (either from User or Turing) into the vector DB.
        """
        if not text.strip():
            return

        # Generate a unique ID for this specific memory
        timestamp = datetime.datetime.now().isoformat()
        memory_id = f"{session_id}_{timestamp}"

        # Insert into the database
        self.collection.add(
            documents=[text],
            metadatas=[{"role": role, "session_id": session_id, "timestamp": timestamp}],
            ids=[memory_id]
        )

    def retrieve_context(self, session_id: str, query: str, limit: int = 5) -> str:
        """
        Searches the database for past messages related to the current query.
        Returns a formatted string to inject into the AI's prompt.
        """
        # Check if the database is empty to prevent query errors
        if self.collection.count() == 0:
            return ""

        # Search the vector database for relevant past context
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={"session_id": session_id} # Only get memories from this specific chat session
        )

        context_string = ""
        if results['documents'] and len(results['documents'][0]) > 0:
            context_string = "\n--- RELEVANT PAST CONTEXT ---\n"
            # Loop through the results and format them
            for idx, doc in enumerate(results['documents'][0]):
                role = results['metadatas'][0][idx]['role']
                context_string += f"{role.upper()}: {doc}\n"
            context_string += "-----------------------------\n"
            
        return context_string

# ==========================================
# TEST THE MEMORY SYSTEM
# ==========================================
if __name__ == "__main__":
    print("Initializing Turing Vector Memory...")
    memory = TuringMemory()
    
    # 1. Save a test memory
    print("Saving test memory to SSD...")
    memory.save_memory("session_01", "user", "My name is Arshvir and I am the lead OS architect.")
    memory.save_memory("session_01", "turing", "Understood. I will remember that you are Arshvir, the OS Architect.")
    
    # 2. Retrieve the context
    print("\nRetrieving memory based on a new question...")
    retrieved_data = memory.retrieve_context("session_01", "What is my name and job?")
    
    print(retrieved_data)
    print("\n[Memory System Test Complete]")