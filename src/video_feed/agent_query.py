import time
from video_feed import video_embedder, chroma_client
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

MAX_SCREEN_TEXT_LEN = 300 

print("=== Reasoning Agent CLI ===")
print("Enter a prompt to query your screen history.")
print("Type 'exit' to quit.\n")

while True:
    agent_prompt = input("Prompt> ").strip()
    if agent_prompt.lower() in {"exit", "quit"}:
        print("Exiting.")
        break

    # --- Embed query ---
    query_embedding = video_embedder.embed_text(agent_prompt)

    # --- Query Chroma ---
    results = chroma_client.query_embedding(query_embedding, n_results=3)

    # --- Build context from results ---
    retrieved_frames = results["ids"][0]
    retrieved_distances = results["distances"][0]
    retrieved_meta = results["metadatas"][0]

    context_strings = []
    for frame_id, meta in zip(retrieved_frames, retrieved_meta):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(meta["timestamp"]))
        caption = meta.get("caption", "No caption")
        screen_text = meta.get("screen_text", "No OCR text")
        screen_text = (screen_text[:MAX_SCREEN_TEXT_LEN] + '...') if len(screen_text) > MAX_SCREEN_TEXT_LEN else screen_text
        monitor_id = meta.get("monitor_id", "Unknown")

        context_strings.append(
            f"Monitor {monitor_id} | Frame {frame_id} at {timestamp}\n"
            f"Caption: {caption}\n"
            f"Screen text: {screen_text}\n"
    )

    context_block = "\n".join(context_strings)

    # --- Send to Ollama LLM (Mixtral) ---
    chat_payload = {
        "model": "mistral",
        "messages": [
            {"role": "system", "content": "You are an assistant that reasons about what was on the user's screen based on retrieved frame context."},
            {"role": "user", "content": f"User prompt: {agent_prompt}\n\nRelevant screen context:\n{context_block}\n\nAnswer the question based on the above."}
        ],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=chat_payload)
    response.raise_for_status()
    reply = response.json()["message"]["content"]

    print(f"\n=== Agent Response ===\n{reply}\n")
