# Audio Retrieval Testing Guide

## 🎯 Quick Testing Methods

### Method 1: Using curl (Recommended for Quick Tests)

#### Step 1: Get JWT Token
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your_email@example.com", "password": "your_password"}'

# Copy the "access_token" from response
export TOKEN="your_access_token_here"
```

#### Step 2: Upload Audio File
```bash
curl -X POST http://localhost:8000/api/audio/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/audio.mp3"

# Response includes:
# - audio_url: The uploaded audio URL
# - file_id: Unique identifier
# - status: "processing" (background transcription)

# Wait 10-20 seconds for background processing to complete
sleep 15
```

#### Step 3: Test Text → Audio Search
```bash
curl -X POST http://localhost:8000/api/search/audio/text_to_audio \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning tutorial",
    "top_k": 5
  }'

# Expected response:
# {
#   "query": "machine learning tutorial",
#   "results": [
#     {
#       "id": "...",
#       "score": 0.42,
#       "audio_url": "https://...",
#       "transcript": "Welcome to this machine learning...",
#       "timestamps": [...]
#     }
#   ]
# }
```

#### Step 4: Test Audio → Audio Search
```bash
curl -X POST http://localhost:8000/api/search/audio/audio_to_audio \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/query_audio.mp3" \
  -F "top_k=5"
```

#### Step 5: Test Audio → Text Search
```bash
curl -X POST http://localhost:8000/api/search/audio/audio_to_text \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/query_audio.mp3" \
  -F "top_k=5"
```

---

### Method 2: Using Python Script

```bash
cd /home/dipak/SIH-25321_MVP/backend

# 1. Update TOKEN in the script
nano test_audio_retrieval.py

# 2. Add a test audio file
# Download or create a test file: test_audio.mp3

# 3. Run tests
python test_audio_retrieval.py
```

---

### Method 3: Using FastAPI Docs (Interactive)

1. **Start server**:
   ```bash
   cd /home/dipak/SIH-25321_MVP/backend
   uvicorn app.main:app --reload
   ```

2. **Open browser**: http://localhost:8000/docs

3. **Authenticate**:
   - Click "Authorize" (top right)
   - Login via `/api/auth/login`
   - Copy `access_token`
   - Enter: `Bearer <your_token>`

4. **Test endpoints**:
   - POST `/api/audio/upload` - Upload audio
   - POST `/api/search/audio/text_to_audio` - Search by text
   - POST `/api/search/audio/audio_to_audio` - Search by audio
   - POST `/api/search/audio/audio_to_text` - Find text from audio

---

## 🧪 What to Test

### 1. **Upload & Indexing**
- ✅ Audio uploads successfully
- ✅ Background processing completes (check after 10-20s)
- ✅ Transcript is generated
- ✅ Audio is indexed in Qdrant

### 2. **Text → Audio Search**
- ✅ Returns relevant audio files
- ✅ Scores are reasonable (0.25-0.50 range)
- ✅ Transcripts match query semantically
- ✅ Low-scoring results are filtered out

### 3. **Audio → Audio Search**
- ✅ Finds similar audio content
- ✅ Query audio is transcribed correctly
- ✅ Results are semantically similar

### 4. **Audio → Text Search**
- ✅ Query audio is transcribed
- ✅ Returns text documents matching transcript
- ✅ Cross-modal search works (audio → text)

---

## 🔍 Expected Score Ranges

| Search Type | Good Score | Explanation |
|------------|-----------|-------------|
| **Text → Audio** | 0.30-0.50 | BGE-m3 1024-dim matching transcripts |
| **Audio → Audio** | 0.35-0.55 | Same transcripts = higher similarity |
| **Audio → Text** | 0.28-0.45 | Cross-collection semantic match |

**Thresholds applied**:
- Text → Audio: 0.25-0.28 (adaptive)
- Audio → Audio: 0.30
- Audio → Text: 0.28

---

## 🐛 Troubleshooting

### Issue: "No results found"

**Causes**:
1. No audio uploaded yet → Upload first
2. Background processing not finished → Wait longer
3. Query doesn't match any transcript → Try different query
4. Scores below threshold → Check raw scores

**Fix**:
```bash
# Check if collection has data
curl http://localhost:8000/health/qdrant

# Should show "audio_collection" in list
```

### Issue: "Transcription failed"

**Causes**:
1. Whisper model not loaded
2. Audio format not supported
3. Audio file corrupted

**Fix**:
```bash
# Check Whisper is working
cd /home/dipak/SIH-25321_MVP/backend
python -c "
from app.asr.local_whisper import transcribe_local
result = transcribe_local('https://audio-url-here')
print(result)
"
```

### Issue: Low scores

**Expected behavior**:
- Short queries: 0.25-0.35 (normal)
- Long queries: 0.30-0.45 (good)
- Poor audio quality → lower transcription quality → lower scores

---

## 📊 Sample Test Data

### Good Test Queries (Text → Audio):
- "introduction to machine learning"
- "quantum computing basics"
- "neural network architecture"
- "data science tutorial"

### Sample Audio Files:
- YouTube lectures (download with yt-dlp)
- Podcast episodes
- Tutorial recordings
- Interview recordings

---

## ✅ Success Criteria

- [x] Audio uploads without errors
- [x] Transcription completes in < 30s for 1-min audio
- [x] Search returns results with scores > 0.25
- [x] Top result is semantically relevant
- [x] All 3 search types work (text→audio, audio→audio, audio→text)

---

## 🚀 Next Steps

1. **Test with real audio**: Record or download sample audio
2. **Check scores**: Verify they're in expected ranges
3. **Try edge cases**: Long audio, noisy audio, music
4. **Monitor performance**: Check Whisper speed, indexing time
5. **Adjust thresholds**: If too strict/lenient, modify in search_audio.py
