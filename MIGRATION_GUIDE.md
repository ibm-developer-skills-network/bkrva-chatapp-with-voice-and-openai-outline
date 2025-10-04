# Migration Guide: OpenAI/IBM Watson → Ollama/Whisper/gTTS

## 📋 **What Changed**

| Component | Before | After |
|-----------|--------|-------|
| **STT** | IBM Watson HTTP API | 🎤 Transformers Whisper (local) |
| **LLM** | OpenAI GPT-3.5 API | 🤖 Ollama llama3.2 (local) |
| **TTS** | IBM Watson HTTP API | 🔊 Google TTS (gTTS) |

---

## 🚀 **Quick Start**

### **1. Local Development (Recommended First)**

```bash
# Make sure Ollama is running
ollama serve

# Pull the model if you haven't already
ollama pull llama3.2

# Install dependencies
pip install -r requirements.txt

# Test connectivity
python test_connectivity.py

# Run the application
python server.py

# Access at: http://localhost:8000
```

### **2. Docker Deployment**

```bash
# Build the image (takes 5-10 minutes due to Whisper model download)
docker build -t voice-chat-app .

# Run the container
docker run -p 8000:8000 voice-chat-app

# Access at: http://localhost:8000
```

---

## 🔧 **Configuration**

### **Ollama Base URL**

The app uses the `OLLAMA_BASE_URL` environment variable:

- **Local development**: Defaults to `http://localhost:11434`
- **Docker (Mac/Windows)**: Set to `http://host.docker.internal:11434`
- **Docker (Linux)**: Use `--network="host"` or Docker Compose

To override:
```bash
export OLLAMA_BASE_URL="http://your-ollama-server:11434"
python server.py
```

Or in Docker:
```bash
docker run -p 8000:8000 -e OLLAMA_BASE_URL="http://host.docker.internal:11434" voice-chat-app
```

---

## 🧪 **Testing**

### **Run the Test Suite**
```bash
python test_connectivity.py
```

**Expected Output:**
```
🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧
COMPONENT TESTING SUITE
🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧

============================================================
TEST 1: Ollama Connectivity & LLM Processing
============================================================
✅ SUCCESS - Ollama Response: Hello, I am working!

============================================================
TEST 2: Whisper Model Loading
============================================================
✅ SUCCESS - Whisper model loaded successfully

============================================================
TEST 3: gTTS Text-to-Speech
============================================================
✅ SUCCESS - Generated audio: 15234 bytes

============================================================
TEST SUMMARY
============================================================
✅ PASS - Ollama
✅ PASS - Whisper
✅ PASS - gTTS
```

---

## 🐛 **Troubleshooting**

### **Ollama Connection Failed**

**Error:** `Connection refused to localhost:11434`

**Solutions:**
1. Start Ollama: `ollama serve`
2. Verify it's running: `curl http://localhost:11434`
3. Check the model: `ollama list` (should show llama3.2)
4. Pull if missing: `ollama pull llama3.2`

### **Docker: Cannot reach Ollama**

**Error:** `Failed to connect to Ollama`

**Solutions:**
1. **Mac/Windows**: Use `http://host.docker.internal:11434` ✅ (already set in Dockerfile)
2. **Linux**: Run with `docker run --network="host" ...`
3. **Alternative**: Use Docker Compose (see below)

### **Whisper Model Download Slow**

**First Run:** Model downloads (~150MB), takes 1-2 minutes  
**Subsequent Runs:** Uses cached model, loads in ~10 seconds

**Docker:** Model is pre-downloaded during `docker build` ✅

### **gTTS Not Working**

**Error:** `Connection error`

**Solution:** Ensure internet connection (gTTS requires Google's API)

---

## 🐳 **Docker Compose (Advanced)**

For a fully containerized setup with Ollama:

```yaml
# docker-compose.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    command: serve

  voice-chat:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama

volumes:
  ollama-data:
```

**Usage:**
```bash
docker-compose up -d
# Pull model into Ollama container
docker-compose exec ollama ollama pull llama3.2
# Access app at http://localhost:8000
```

---

## 📊 **Performance Notes**

| Component | First Load | Subsequent |
|-----------|-----------|------------|
| **Whisper** | 10-30s | ~1s |
| **Ollama** | 2-5s | 1-2s |
| **gTTS** | 1-3s | 1-3s |

**Total Pipeline:** ~15-40 seconds first run, ~3-6 seconds after warmup

---

## ✅ **Verification Checklist**

Before deploying, confirm:

- [ ] `python test_connectivity.py` passes all tests
- [ ] Ollama is running and llama3.2 is pulled
- [ ] Web interface loads at http://localhost:8000
- [ ] Can record/upload audio
- [ ] Audio transcribes correctly (Whisper)
- [ ] LLM responds appropriately (Ollama)
- [ ] Audio response plays back (gTTS)

---

## 🔄 **Switching Models**

### **Change Ollama Model**

Edit `worker.py`:
```python
ollama_client = ChatOllama(
    model="llama3.2",  # Change to: mistral, llama2, etc.
    base_url=OLLAMA_BASE_URL,
    temperature=0.0,
    max_tokens=4000,
)
```

Don't forget to pull: `ollama pull <model-name>`

### **Change Whisper Model**

Edit `worker.py`:
```python
whisper_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny.en",  # Options: tiny, base, small, medium, large
    chunk_length_s=30,
)
```

**Model sizes:**
- tiny: ~150MB, fastest
- base: ~290MB
- small: ~967MB
- medium: ~3GB, most accurate

---

## 📝 **Files Modified**

1. **worker.py** - Complete rewrite with new services
2. **requirements.txt** - New dependencies
3. **Dockerfile** - Added ffmpeg, pre-download Whisper
4. **test_connectivity.py** - NEW: Test suite

**Files NOT modified:**
- server.py (unchanged, still works)
- static/* (unchanged)
- templates/* (unchanged)

---

## 🎯 **Next Steps**

1. Run `python test_connectivity.py` ✅
2. Test locally with `python server.py` ✅
3. Test in browser at http://localhost:8000 ✅
4. Build Docker image ✅
5. Deploy to production 🚀

---

**Need help?** Check the test output for specific troubleshooting steps!
