#!/usr/bin/env python3
"""
Quick unit test for audio retrieval components (no API needed).
Tests individual functions in isolation.
"""

import sys
sys.path.insert(0, '/home/dipak/SIH-25321_MVP/backend')

def test_whisper():
    """Test Whisper transcription"""
    print("\n" + "="*60)
    print("TEST: Whisper Model Loading")
    print("="*60)
    
    try:
        from app.asr.local_whisper import _get_model
        import os
        
        # Just test if Whisper model loads (no network needed)
        print("Loading Whisper model...")
        model = _get_model()
        
        print(f"✅ Whisper model loaded successfully")
        print(f"   Model type: {type(model).__name__}")
        print(f"   Model is ready for transcription")
        
        # Check if base.pt exists in cache
        cache_dir = os.path.join("/home/dipak/SIH-25321_MVP/model_cache", "whisper")
        if os.path.exists(cache_dir):
            files = os.listdir(cache_dir)
            print(f"   Cached files: {files}")
        
        print(f"\n   ℹ️  To test with actual audio:")
        print(f"      1. Upload audio via /api/audio/upload")
        print(f"      2. Or run: python -c \"from app.asr.orchestrator import transcribe_audio; print(transcribe_audio('your_audio_url'))\"")
        
        return True
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        print(f"   This is OK if Whisper isn't installed yet")
        return False


def test_embedder():
    """Test BGE-m3 embedder"""
    print("\n" + "="*60)
    print("TEST: BGE-m3 Embedder")
    print("="*60)
    
    try:
        from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
        
        embedder = HFBgeM3Embedder()
        
        test_text = "This is a test transcript about machine learning"
        vector = embedder.embed_query(test_text)
        
        print(f"✅ Embedding successful")
        print(f"   Text: {test_text}")
        print(f"   Dimension: {len(vector)}")
        print(f"   Sample values: {vector[:3]}")
        
        # Check normalization
        import math
        norm = math.sqrt(sum(x*x for x in vector))
        print(f"   L2 norm: {norm:.6f} (should be ~1.0)")
        
        return True
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return False


def test_qdrant_connection():
    """Test Qdrant connection"""
    print("\n" + "="*60)
    print("TEST: Qdrant Connection")
    print("="*60)
    
    try:
        from app.db.qdrant_client import get_qdrant_client
        
        client = get_qdrant_client()
        collections = client.get_collections()
        
        print(f"✅ Qdrant connected")
        print(f"   Collections: {[c.name for c in collections.collections]}")
        
        # Check if audio_collection exists
        audio_exists = any(c.name == "audio_collection" for c in collections.collections)
        if audio_exists:
            # Get collection info
            info = client.get_collection("audio_collection")
            print(f"   audio_collection:")
            print(f"     - Points: {info.points_count}")
            print(f"     - Vectors: {list(info.config.params.vectors.keys())}")
        else:
            print("   ⚠️  audio_collection not found (needs creation)")
        
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False


def test_audio_indexer():
    """Test audio indexing (dry run)"""
    print("\n" + "="*60)
    print("TEST: Audio Indexer")
    print("="*60)
    
    try:
        from app.ingestion.audio_indexer import index_audio
        from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
        
        # Create test data
        test_transcript = "This is a test transcript about quantum computing and machine learning"
        test_audio_url = "https://example.com/test.mp3"
        test_owner_id = "test-user-123"
        test_file_id = "test-file-456"
        
        print(f"Testing indexing with:")
        print(f"   Transcript: {test_transcript}")
        print(f"   Owner: {test_owner_id}")
        
        # Test embedding generation (without actually indexing)
        embedder = HFBgeM3Embedder()
        vector = embedder.embed_query(test_transcript)
        
        print(f"✅ Indexer components work")
        print(f"   Generated {len(vector)}-dim vector")
        print(f"   Would index to audio_collection")
        
        # To actually index (uncomment if you want):
        # index_audio(test_audio_url, test_owner_id, test_file_id, test_transcript)
        # print("   ✅ Indexed successfully")
        
        return True
    except Exception as e:
        print(f"❌ Indexer test failed: {e}")
        return False


def test_text_to_audio_retriever():
    """Test text→audio retrieval logic"""
    print("\n" + "="*60)
    print("TEST: Text → Audio Retrieval")
    print("="*60)
    
    try:
        from app.retrieval.text_to_audio_retriever import retrieve_audio_from_text
        
        test_query = "machine learning tutorial"
        test_owner_id = "test-user-123"
        
        print(f"Query: '{test_query}'")
        print(f"Owner: {test_owner_id}")
        
        results = retrieve_audio_from_text(
            query=test_query,
            owner_id=test_owner_id,
            top_k=3,
        )
        
        if results:
            print(f"✅ Retrieved {len(results)} results:")
            for i, r in enumerate(results, 1):
                print(f"   {i}. Score: {r.get('score', 0):.4f}")
                transcript = r.get('transcript', '')[:60]
                print(f"      Transcript: {transcript}...")
        else:
            print("✅ Retrieval works (no results - expected if DB empty)")
        
        return True
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "🔬"*30)
    print("    AUDIO RETRIEVAL UNIT TESTS")
    print("🔬"*30)
    
    results = {
        "Whisper": test_whisper(),
        "Embedder": test_embedder(),
        "Qdrant": test_qdrant_connection(),
        "Indexer": test_audio_indexer(),
        "Retrieval": test_text_to_audio_retriever(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Audio retrieval is working.")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
