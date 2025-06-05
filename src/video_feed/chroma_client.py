import chromadb
from chromadb.config import Settings

# Initialize Chroma client
client = chromadb.HttpClient(host="localhost", port=8000)
collection_name = "video_screen_feed"

try:
    collection = client.get_collection(collection_name)
except:
    collection = client.create_collection(collection_name)

# --- SAVE embedding ---
def save_embedding(id: str, embedding: list[float], metadata: dict = None):
    collection.add(
        ids=[id],
        embeddings=[embedding],
        documents=[""],  # optional text field
        metadatas=[metadata or {}]
    )
    print(f"Saved frame {id} to Chroma.")

# --- QUERY embedding ---
def query_embedding(embedding: list[float], n_results: int = 5):
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    return results
