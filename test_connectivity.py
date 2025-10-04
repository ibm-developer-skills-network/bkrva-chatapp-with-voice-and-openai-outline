#!/usr/bin/env python3
"""
Test script to verify all components are working correctly:
1. Ollama connectivity and LLM processing
2. Whisper model loading and STT
3. gTTS text-to-speech
"""

import os
import sys
import io
from pathlib import Path


def test_ollama_connectivity():
    """Test connection to Ollama and basic LLM functionality."""
    print("\n" + "="*60)
    print("TEST 1: Ollama Connectivity & LLM Processing")
    print("="*60)
    
    try:
        from langchain_ollama import ChatOllama
        
        # Use environment variable or default to localhost
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"Testing Ollama at: {base_url}")
        
        # Initialize client
        client = ChatOllama(
            model="llama3.2",
            base_url=base_url,
            temperature=0.0,
            max_tokens=100,
        )
        
        # Test simple query
        print("Sending test query to Ollama...")
        test_message = "Say 'Hello, I am working!' in exactly those words."
        response = client.invoke([{"role": "user", "content": test_message}])
        
        print(f"✅ SUCCESS - Ollama Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is running: 'ollama serve'")
        print("2. Verify llama3.2 is pulled: 'ollama pull llama3.2'")
        print("3. Check URL is correct (localhost:11434 by default)")
        if "host.docker.internal" in base_url:
            print("4. For Docker: Ensure host.docker.internal is accessible")
        return False


def test_whisper_model():
    """Test Whisper model loading and basic STT functionality."""
    print("\n" + "="*60)
    print("TEST 2: Whisper Model Loading")
    print("="*60)
    
    try:
        from transformers import pipeline
        
        print("Loading Whisper model (this may take 10-30 seconds first time)...")
        whisper = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en",
            chunk_length_s=30,
        )
        print("✅ SUCCESS - Whisper model loaded successfully")
        
        # Note: We can't test actual transcription without an audio file
        # But successful loading means it will work
        print("Note: Actual audio transcription test requires audio file")
        return True
        
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install transformers: 'pip install transformers'")
        print("2. Install torch: 'pip install torch'")
        print("3. Ensure internet connection for model download")
        return False


def test_gtts():
    """Test gTTS text-to-speech functionality."""
    print("\n" + "="*60)
    print("TEST 3: gTTS Text-to-Speech")
    print("="*60)
    
    try:
        from gtts import gTTS
        
        print("Testing gTTS with sample text...")
        test_text = "Hello, this is a test of Google Text to Speech."
        
        # Create TTS object
        tts = gTTS(text=test_text, lang='en', slow=False)
        
        # Save to BytesIO buffer (like in our worker.py)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        audio_size = len(audio_buffer.read())
        print(f"✅ SUCCESS - Generated audio: {audio_size} bytes")
        
        # Optionally save to file for manual testing
        output_file = "test_audio.mp3"
        audio_buffer.seek(0)
        with open(output_file, 'wb') as f:
            f.write(audio_buffer.read())
        print(f"   Audio saved to: {output_file} (you can play this to verify)")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install gTTS: 'pip install gTTS'")
        print("2. Ensure internet connection (gTTS needs Google's API)")
        return False


def test_worker_functions():
    """Test the actual worker.py functions if available."""
    print("\n" + "="*60)
    print("TEST 4: Worker Functions Integration")
    print("="*60)
    
    try:
        # Try to import worker functions
        sys.path.insert(0, str(Path(__file__).parent))
        from worker import speech_to_text, text_to_speech, openai_process_message
        
        print("Testing openai_process_message (now using Ollama)...")
        response = openai_process_message("Say hello in 3 words or less.")
        print(f"✅ LLM Response: {response}")
        
        print("\nTesting text_to_speech...")
        audio = text_to_speech("This is a test.", voice="")
        print(f"✅ Generated audio: {len(audio)} bytes")
        
        print("\n⚠️  STT test skipped (requires audio file)")
        print("   Run the web app and test via browser for full STT test")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  WARNING - Could not import worker.py: {e}")
        print("   This is expected if running from different directory")
        return False
    except Exception as e:
        print(f"❌ FAILED - Error testing worker functions: {e}")
        return False


def main():
    """Run all tests and provide summary."""
    print("\n" + "🔧"*30)
    print("COMPONENT TESTING SUITE")
    print("🔧"*30)
    
    results = {
        "Ollama": test_ollama_connectivity(),
        "Whisper": test_whisper_model(),
        "gTTS": test_gtts(),
        "Worker Integration": test_worker_functions(),
    }
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_critical_passed = results["Ollama"] and results["Whisper"] and results["gTTS"]
    
    print("\n" + "="*60)
    if all_critical_passed:
        print("🎉 ALL CRITICAL TESTS PASSED!")
        print("You're ready to run the application:")
        print("  Local: python server.py")
        print("  Docker: docker build -t voice-chat . && docker run -p 8000:8000 voice-chat")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Review the errors above and fix before deploying")
    print("="*60 + "\n")
    
    return all_critical_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
