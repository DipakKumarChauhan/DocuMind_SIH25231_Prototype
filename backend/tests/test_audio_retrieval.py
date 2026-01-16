#!/usr/bin/env python3
"""
Test script for audio retrieval functionality.
Tests: Upload → Transcription → Indexing → Search

Usage:
    python test_audio_retrieval.py
"""

import requests
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTg0YmY5OC0wZWJiLTRiZmYtYjBhZC0zZDA5ZjJmODA0M2MiLCJleHAiOjE3Njg5OTY2MTR9.1EKqu0jJOMFiek_dHY4-fk-2buQa8350QqqaobuLX5Y"  # Replace with actual token

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def test_1_upload_audio():
    """Test 1: Upload audio file"""
    print("\n" + "="*60)
    print("TEST 1: Upload Audio File")
    print("="*60)
    
    # You need a sample audio file
    audio_path = Path("test_audio.mp3")  # Update path
    
    if not audio_path.exists():
        print("❌ SKIP: No test audio file found")
        print(f"   Create a test file at: {audio_path}")
        return None
    
    files = {"file": open(audio_path, "rb")}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.post(
        f"{BASE_URL}/api/audio/upload",
        files=files,
        headers=headers,
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful")
        print(f"   Audio URL: {data['audio_url']}")
        print(f"   File ID: {data['file_id']}")
        print(f"   Status: {data['status']}")
        
        if data['status'] == 'processing':
            print("   ⏳ Waiting 10s for background processing...")
            time.sleep(10)
        
        return data
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_2_text_to_audio_search():
    """Test 2: Search audio using text query"""
    print("\n" + "="*60)
    print("TEST 2: Text → Audio Search")
    print("="*60)
    
    queries = [
        "machine learning",
        "quantum computing",
        "neural networks",
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        
        response = requests.post(
            f"{BASE_URL}/api/search/audio/text_to_audio",
            json={"query": query, "top_k": 3},
            headers=HEADERS,
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                print(f"   ✅ Found {len(results)} results:")
                for i, r in enumerate(results, 1):
                    print(f"      {i}. Score: {r['score']:.4f}")
                    print(f"         Transcript: {r['transcript'][:100]}...")
                    print(f"         Audio: {r['audio_url'][:60]}...")
            else:
                print("   ⚠️  No results found (or all filtered by threshold)")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            print(f"      Response: {response.text}")


def test_3_audio_to_audio_search():
    """Test 3: Search similar audio using audio query"""
    print("\n" + "="*60)
    print("TEST 3: Audio → Audio Search")
    print("="*60)
    
    audio_path = Path("test_audio.mp3")
    
    if not audio_path.exists():
        print("❌ SKIP: No test audio file found")
        return
    
    files = {"file": open(audio_path, "rb")}
    data = {"top_k": 3}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.post(
        f"{BASE_URL}/api/search/audio/audio_to_audio",
        files=files,
        data=data,
        headers=headers,
    )
    
    if response.status_code == 200:
        result = response.json()
        results = result.get("results", [])
        
        if results:
            print(f"✅ Found {len(results)} similar audio files:")
            for i, r in enumerate(results, 1):
                print(f"   {i}. Score: {r['score']:.4f}")
                print(f"      Transcript: {r['transcript'][:80]}...")
        else:
            print("⚠️  No results found")
    else:
        print(f"❌ Search failed: {response.status_code}")
        print(f"   Response: {response.text}")


def test_4_audio_to_text_search():
    """Test 4: Search text documents using audio query"""
    print("\n" + "="*60)
    print("TEST 4: Audio → Text Search")
    print("="*60)
    
    audio_path = Path("test_audio.mp3")
    
    if not audio_path.exists():
        print("❌ SKIP: No test audio file found")
        return
    
    files = {"file": open(audio_path, "rb")}
    data = {"top_k": 3}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.post(
        f"{BASE_URL}/api/search/audio/audio_to_text",
        files=files,
        data=data,
        headers=headers,
    )
    
    if response.status_code == 200:
        result = response.json()
        results = result.get("results", [])
        
        if results:
            print(f"✅ Found {len(results)} text documents:")
            for i, r in enumerate(results, 1):
                print(f"   {i}. Score: {r['score']:.4f}")
                print(f"      File: {r['filename']} (page {r['page']})")
                print(f"      Text: {r['text'][:80]}...")
        else:
            print("⚠️  No results found")
    else:
        print(f"❌ Search failed: {response.status_code}")
        print(f"   Response: {response.text}")


def test_5_check_collection():
    """Test 5: Check audio collection stats"""
    print("\n" + "="*60)
    print("TEST 5: Check Audio Collection")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/health/qdrant",
        headers=HEADERS,
    )
    
    if response.status_code == 200:
        data = response.json()
        collections = data.get("collections", [])
        
        if "audio_collection" in collections:
            print("✅ audio_collection exists")
        else:
            print("❌ audio_collection NOT found")
            print("   Available collections:", collections)
    else:
        print(f"❌ Health check failed: {response.status_code}")


def main():
    print("\n" + "🎵"*30)
    print("    AUDIO RETRIEVAL TEST SUITE")
    print("🎵"*30)
    
    # Check token
    if TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("\n❌ ERROR: Please set your JWT token in the script")
        print("   1. Login via /api/auth/login")
        print("   2. Copy the access_token")
        print("   3. Update TOKEN variable in this script")
        return
    
    # Run tests
    test_5_check_collection()
    test_1_upload_audio()
    test_2_text_to_audio_search()
    test_3_audio_to_audio_search()
    test_4_audio_to_text_search()
    
    print("\n" + "="*60)
    print("✅ Test suite completed")
    print("="*60)


if __name__ == "__main__":
    main()
