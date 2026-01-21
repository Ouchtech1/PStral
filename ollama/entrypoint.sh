#!/bin/bash
# =============================================================================
# Pstral - Ollama Entrypoint Script
# =============================================================================
# Starts Ollama server and automatically pulls the model if not present
# Designed for VPS deployment without GPU (CPU-only inference)
# =============================================================================

set -e

MODEL="${OLLAMA_MODEL:-ministral:3b}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "=== Pstral Ollama Entrypoint ==="
echo "Model: $MODEL"
echo "Starting Ollama server..."

# Start Ollama server in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama server to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama server is ready!"
        break
    fi
    
    if [ $i -eq $MAX_RETRIES ]; then
        echo "ERROR: Ollama server failed to start after $MAX_RETRIES attempts"
        exit 1
    fi
    
    echo "Attempt $i/$MAX_RETRIES - waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

# Check if model exists, pull if not
echo "Checking if model '$MODEL' is available..."
if ollama list | grep -q "$MODEL"; then
    echo "Model '$MODEL' already downloaded."
else
    echo "Model '$MODEL' not found. Downloading..."
    echo "This may take several minutes depending on your connection speed..."
    ollama pull "$MODEL"
    echo "Model '$MODEL' downloaded successfully!"
fi

# Verify model is working
echo "Verifying model..."
if ollama list | grep -q "$MODEL"; then
    echo "Model verification successful!"
else
    echo "ERROR: Model verification failed!"
    exit 1
fi

echo "=== Ollama is ready to serve requests ==="
echo "Model: $MODEL"
echo "Endpoint: http://localhost:11434"

# Keep the container running by waiting for Ollama process
wait $OLLAMA_PID

