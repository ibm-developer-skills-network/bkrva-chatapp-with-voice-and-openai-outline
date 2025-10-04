FROM python:3.10

# Install system dependencies
# ffmpeg is required for audio processing with Whisper
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download Whisper model during build (optional but highly recommended)
# This prevents the 10-30 second delay on first request
RUN python -c "from transformers import pipeline; \
    print('Pre-downloading Whisper model...'); \
    pipeline('automatic-speech-recognition', model='openai/whisper-tiny.en'); \
    print('Whisper model cached successfully')"

# Copy application code
COPY . .

# Set environment variables
# Use host.docker.internal to reach Ollama running on host machine (Mac/Windows)
# For Linux, use --network="host" or Docker Compose
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-u", "server.py"]
