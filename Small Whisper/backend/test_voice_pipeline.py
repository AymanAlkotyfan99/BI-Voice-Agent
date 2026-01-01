"""
End-to-End Test for Voice BI Pipeline

This test sends an audio file to the Whisper endpoint and validates
the complete pipeline output:
  - Whisper transcription
  - Reasoning classification
  - Intent extraction
  - SQL generation
  - Chart recommendation
"""
import requests
import json
import os

# Whisper transcription endpoint
WHISPER_URL = "http://127.0.0.1:8000/api/transcribe/"

# Path to audio file (update this to your actual audio file path)
AUDIO_FILE_PATH = r"C:\Users\Ayman\Desktop\Small Whisper\Small Whisper\Recording (3).m4a"

def test_voice_pipeline():
    """Test complete voice-to-insight pipeline"""
    
    print("\n" + "="*60)
    print("🧪 TESTING VOICE BI PIPELINE")
    print("="*60)
    
    # Check if audio file exists
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"❌ Audio file not found: {AUDIO_FILE_PATH}")
        print("⚠️  Please update AUDIO_FILE_PATH in test_voice_pipeline.py")
        return False
    
    print(f"\n📁 Audio file: {AUDIO_FILE_PATH}")
    print(f"🎙️  Sending to: {WHISPER_URL}\n")
    
    try:
        # Send audio file
        with open(AUDIO_FILE_PATH, "rb") as audio_file:
            response = requests.post(
                WHISPER_URL,
                files={"audio": audio_file},
                timeout=120  # 2 minutes timeout for Whisper processing
            )
        
        if response.status_code != 200:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        # ===========================
        # VALIDATE OUTPUTS
        # ===========================
        
        print("="*60)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        
        # 1. Whisper Output
        text = result.get("text")
        print("\n🗣️  WHISPER TRANSCRIPTION:")
        print("-" * 60)
        print(text or "[NO TEXT]")
        
        if not text:
            print("⚠️  Warning: No transcription text received")
        
        # 2. Reasoning Output
        reasoning = result.get("reasoning", {})
        print("\n🧠 REASONING CLASSIFICATION:")
        print("-" * 60)
        print(f"  Question Type: {reasoning.get('question_type')}")
        print(f"  Needs SQL:     {reasoning.get('needs_sql')}")
        print(f"  Needs Chart:   {reasoning.get('needs_chart')}")
        
        if reasoning.get("message"):
            print(f"  Message:       {reasoning.get('message')}")
        
        # 3. LLM Output (SQL + Chart)
        llm = result.get("llm")
        
        if llm:
            print("\n🤖 LLM PIPELINE OUTPUT:")
            print("-" * 60)
            
            # SQL
            sql = llm.get("sql")
            print("\n📊 GENERATED SQL:")
            print(sql or "[NO SQL]")
            
            # Chart
            chart = llm.get("chart", {})
            print("\n📈 CHART RECOMMENDATION:")
            print(json.dumps(chart, indent=2))
            
            # Intent
            intent = llm.get("intent", {})
            print("\n🎯 EXTRACTED INTENT:")
            print(json.dumps({
                "table": intent.get("table"),
                "metrics": intent.get("metrics", []),
                "dimensions": intent.get("dimensions", []),
                "filters": intent.get("filters", [])
            }, indent=2))
            
            # Confidence
            confidence = llm.get("confidence", 0)
            print(f"\n✨ CONFIDENCE SCORE: {confidence:.2%}")
            
            # Columns
            columns = llm.get("columns", [])
            if columns:
                print(f"\n📋 REFERENCED COLUMNS: {', '.join(columns)}")
        
        else:
            print("\n⚠️  LLM stage was skipped (non-analytical question)")
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETED")
        print("="*60)
        
        return True
    
    except requests.exceptions.Timeout:
        print("❌ Request timeout (Whisper processing took too long)")
        return False
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_reasoning_only():
    """Test reasoning endpoint directly with text"""
    
    print("\n" + "="*60)
    print("🧪 TESTING REASONING LAYER ONLY")
    print("="*60)
    
    test_questions = [
        "What is the total sales by customer?",
        "Hello, how are you?",
        "Show me the average order amount per month"
    ]
    
    for question in test_questions:
        print(f"\n📝 Question: {question}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/reasoning/test/",
                json={"text": question},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Type: {result.get('question_type')}")
                print(f"   Needs SQL: {result.get('needs_sql')}")
                print(f"   Needs Chart: {result.get('needs_chart')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def test_intent_only():
    """Test intent extraction endpoint directly"""
    
    print("\n" + "="*60)
    print("🧪 TESTING INTENT EXTRACTION ONLY")
    print("="*60)
    
    question = "Show me total sales by customer"
    print(f"\n📝 Question: {question}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/llm/intent/",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Intent extracted successfully:")
            print(f"SQL:\n{result.get('sql')}")
            print(f"\nChart: {json.dumps(result.get('chart'), indent=2)}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n🚀 STARTING PIPELINE TESTS\n")
    
    # Uncomment the tests you want to run:
    
    # Full pipeline test (requires audio file)
    test_voice_pipeline()
    
    # Individual component tests (don't require audio)
    # test_reasoning_only()
    # test_intent_only()

