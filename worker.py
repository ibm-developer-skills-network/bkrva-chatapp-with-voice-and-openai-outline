import os
import io
import tempfile
from transformers import pipeline
from langchain_ollama import ChatOllama
from gtts import gTTS

# Initialize Whisper pipeline for Speech-to-Text
print("Loading Whisper model...")
whisper_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny.en",
    chunk_length_s=30,
)
print("Whisper model loaded successfully")

# Initialize Ollama client for LLM processing
# Use host.docker.internal for Docker, localhost for local development
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

ollama_client = ChatOllama(
    model="llama3.2",
    base_url=OLLAMA_BASE_URL,
    temperature=0.0,
    max_tokens=4000,
)
print(f"Ollama client initialized with base URL: {OLLAMA_BASE_URL}")


def speech_to_text(audio_binary):
    """
    Convert speech audio to text using Whisper model.
    
    Args:
        audio_binary: Binary audio data from the request
        
    Returns:
        str: Transcribed text from the audio
    """
    try:
        # Create a temporary file to store the audio binary
        # Whisper pipeline requires a file path, not binary data directly
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_audio.write(audio_binary)
            temp_audio_path = temp_audio.name
        
        # Transcribe the audio using Whisper
        print(f"Transcribing audio file: {temp_audio_path}")
        result = whisper_pipeline(temp_audio_path, batch_size=8)
        text = result["text"]
        
        # Clean up temporary file
        os.unlink(temp_audio_path)
        
        print(f"Recognized text: {text}")
        return text
        
    except Exception as e:
        print(f"Error in speech_to_text: {e}")
        # Clean up temp file if it exists
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        return "Error transcribing audio"


def text_to_speech(text, voice="com"):
    """
    Convert text to speech using Google Text-to-Speech (gTTS).
    
    Args:
        text: Text to convert to speech
        voice: Voice parameter voice parameter now represents TLD (accent variant)
                Examples: 'com' (US), 'co.uk' (UK), 'com.au' (AU)
        
    Returns:
        bytes: Audio data in MP3 format
    """
    try:
        # Default to US English if empty or "default"
        if voice == "" or voice == "default":
            voice = "com"

        print(f"Converting text to speech with voice '{voice}': {text[:50]}...")
        
        # Initialize gTTS with the text
        # It uses Google's default English language model
        tts = gTTS(text=text, lang='en', tld=voice, slow=False)
        
        # Save audio to bytes buffer in memory
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        # Read the bytes and return
        audio_content = audio_bytes.read()
        print(f"Text-to-speech conversion successful, audio size: {len(audio_content)} bytes")
        
        return audio_content
        
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return b""  # Return empty bytes on error


def openai_process_message(user_message):
    """
    Process user message using Ollama LLM (replacing OpenAI).
    
    Args:
        user_message: User's input message
        
    Returns:
        str: LLM's response text
    """
    try:
        # Set the system prompt
        prompt = "Act like a personal assistant. You can respond to questions, translate sentences, summarize news, and give recommendations."
        
        print(f"Processing message with Ollama: {user_message}")
        
        # Call Ollama using LangChain's ChatOllama
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Invoke the model
        response = ollama_client.invoke(messages)
        
        # Extract the response text
        # ChatOllama returns an AIMessage object, we need .content
        response_text = response.content
        
        print(f"Ollama response: {response_text[:100]}...")
        return response_text
        
    except Exception as e:
        print(f"Error in openai_process_message: {e}")
        return f"Sorry, I encountered an error processing your message: {str(e)}"
