#!/bin/sh

# Start Ollama serve in background
ollama serve &

# Wait for it to come up
sleep 5

# Pull our models
ollama pull mistral

# Wait for ollama serve to continue
wait