#!/usr/bin/env python3
"""
Test file upload validation across all endpoints.

Tests:
- Image validation (size, MIME, empty, corrupted)
- Audio validation (size, MIME, empty, corrupted)
- PDF/DOCX validation (size, MIME, empty, magic bytes)
- Chat temporary uploads (image + audio)

Usage:
    python test_upload_validation.py
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Get from login endpoint

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}


def test_image_validation():
    """Test image upload validation."""
    print("\n" + "="*60)
    print("TEST 1: Image Upload Validation")
    print("="*60)
    
    # Test 1a: Valid image
    print("\n1a. Valid image (PNG)...")
    with open("demo_data/screenshot.png", "rb") as f:
        files = {"file": f}
        response = requests.post(
            f"{BASE_URL}/api/upload/image",
            files=files,
            headers=HEADERS,
        )
    if response.status_code == 200:
        print(f"✅ PASS: Image uploaded successfully")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ FAIL: {response.status_code} - {response.json()}")
    
    # Test 1b: Empty file
    print("\n1b. Empty image file...")
    files = {"file": ("empty.png", b"")}
    response = requests.post(
        f"{BASE_URL}/api/upload/image",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 400:
        print(f"✅ PASS: Empty file rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")
    
    # Test 1c: Wrong MIME type
    print("\n1c. Wrong MIME type (text file as image)...")
    files = {"file": ("fake.png", b"This is not an image", "text/plain")}
    response = requests.post(
        f"{BASE_URL}/api/upload/image",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 415:
        print(f"✅ PASS: Wrong MIME type rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 415, got {response.status_code}")
    
    # Test 1d: File too small (< 1KB)
    print("\n1d. File too small (< 1KB)...")
    files = {"file": ("tiny.png", b"x" * 500)}
    response = requests.post(
        f"{BASE_URL}/api/upload/image",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 400:
        print(f"✅ PASS: Too-small file rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")


def test_audio_validation():
    """Test audio upload validation."""
    print("\n" + "="*60)
    print("TEST 2: Audio Upload Validation")
    print("="*60)
    
    # Test 2a: Valid audio
    print("\n2a. Valid audio (MP3)...")
    if Path("demo_data/audio.mp3").exists():
        with open("demo_data/audio.mp3", "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{BASE_URL}/api/audio/upload",
                files=files,
                headers=HEADERS,
            )
        if response.status_code == 200:
            print(f"✅ PASS: Audio uploaded successfully")
        else:
            print(f"❌ FAIL: {response.status_code} - {response.json()}")
    else:
        print("⏭️ SKIP: No test audio file")
    
    # Test 2b: Empty audio
    print("\n2b. Empty audio file...")
    files = {"file": ("empty.mp3", b"")}
    response = requests.post(
        f"{BASE_URL}/api/audio/upload",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 400:
        print(f"✅ PASS: Empty file rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")
    
    # Test 2c: Wrong MIME type
    print("\n2c. Wrong MIME type (text file as audio)...")
    files = {"file": ("fake.mp3", b"This is not audio", "text/plain")}
    response = requests.post(
        f"{BASE_URL}/api/audio/upload",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 415:
        print(f"✅ PASS: Wrong MIME type rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 415, got {response.status_code}")
    
    # Test 2d: File too small (< 10KB)
    print("\n2d. File too small (< 10KB)...")
    files = {"file": ("tiny.mp3", b"x" * 5000)}
    response = requests.post(
        f"{BASE_URL}/api/audio/upload",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 400:
        print(f"✅ PASS: Too-small file rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")


def test_pdf_validation():
    """Test PDF upload validation."""
    print("\n" + "="*60)
    print("TEST 3: PDF Upload Validation")
    print("="*60)
    
    # Test 3a: Valid PDF
    print("\n3a. Valid PDF...")
    if Path("demo_data/document.pdf").exists():
        with open("demo_data/document.pdf", "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{BASE_URL}/api/upload-admin",
                files=files,
                headers=HEADERS,
            )
        if response.status_code == 200:
            print(f"✅ PASS: PDF uploaded successfully")
            print(f"   Chunks: {response.json().get('total_chunks')}")
        else:
            print(f"❌ FAIL: {response.status_code} - {response.json()}")
    else:
        print("⏭️ SKIP: No test PDF file")
    
    # Test 3b: Empty PDF
    print("\n3b. Empty PDF file...")
    files = {"file": ("empty.pdf", b"")}
    response = requests.post(
        f"{BASE_URL}/api/upload-admin",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 400:
        print(f"✅ PASS: Empty file rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")
    
    # Test 3c: Corrupted PDF (wrong magic bytes)
    print("\n3c. Corrupted PDF (wrong magic bytes)...")
    fake_pdf = b"FAKE_PDF_CONTENT" * 100  # Not a valid PDF
    files = {"file": ("fake.pdf", fake_pdf, "application/pdf")}
    response = requests.post(
        f"{BASE_URL}/api/upload-admin",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 400:
        print(f"✅ PASS: Corrupted PDF rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")
    
    # Test 3d: Wrong file type (text as PDF)
    print("\n3d. Wrong file type (unsupported extension)...")
    files = {"file": ("file.txt", b"This is text", "text/plain")}
    response = requests.post(
        f"{BASE_URL}/api/upload-admin",
        files=files,
        headers=HEADERS,
    )
    if response.status_code == 415:
        print(f"✅ PASS: Wrong file type rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 415, got {response.status_code}")


def test_chat_upload_validation():
    """Test chat temporary file upload validation."""
    print("\n" + "="*60)
    print("TEST 4: Chat Temporary Upload Validation")
    print("="*60)
    
    # Test 4a: Chat with valid image
    print("\n4a. Chat with valid image...")
    if Path("demo_data/screenshot.png").exists():
        with open("demo_data/screenshot.png", "rb") as f:
            files = {"image": f}
            data = {
                "message": "What's in this image?",
                "session_id": "test-session-1"
            }
            response = requests.post(
                f"{BASE_URL}/api/chat",
                files=files,
                data=data,
                headers=HEADERS,
            )
        if response.status_code == 200:
            print(f"✅ PASS: Chat with image succeeded")
        else:
            print(f"❌ FAIL: {response.status_code} - {response.json()}")
    else:
        print("⏭️ SKIP: No test image file")
    
    # Test 4b: Chat with invalid image
    print("\n4b. Chat with invalid image (empty)...")
    files = {"image": ("empty.png", b"")}
    data = {
        "message": "What's in this image?",
        "session_id": "test-session-2"
    }
    response = requests.post(
        f"{BASE_URL}/api/chat",
        files=files,
        data=data,
        headers=HEADERS,
    )
    if response.status_code == 400:
        print(f"✅ PASS: Empty image in chat rejected")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")
    
    # Test 4c: Chat with valid audio
    print("\n4c. Chat with valid audio...")
    if Path("demo_data/audio.mp3").exists():
        with open("demo_data/audio.mp3", "rb") as f:
            files = {"audio": f}
            data = {
                "message": "What's in this audio?",
                "session_id": "test-session-3"
            }
            response = requests.post(
                f"{BASE_URL}/api/chat",
                files=files,
                data=data,
                headers=HEADERS,
            )
        if response.status_code == 200:
            print(f"✅ PASS: Chat with audio succeeded")
        else:
            print(f"❌ FAIL: {response.status_code} - {response.json()}")
    else:
        print("⏭️ SKIP: No test audio file")


def main():
    """Run all validation tests."""
    print("\n" + "="*60)
    print("UPLOAD VALIDATION TEST SUITE")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Token: {TOKEN[:20]}..." if TOKEN != "YOUR_AUTH_TOKEN_HERE" else "⚠️ WARNING: Update TOKEN variable")
    
    if TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("\n❌ Please update TOKEN variable with valid auth token")
        return
    
    try:
        test_image_validation()
        test_audio_validation()
        test_pdf_validation()
        test_chat_upload_validation()
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error: Server not running at {BASE_URL}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
