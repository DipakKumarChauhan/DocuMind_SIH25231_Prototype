# Embedding Pipeline Issues (BGE-M3)

## Current Problem
- HF router endpoint `https://router.huggingface.co/hf-inference/models/BAAI/bge-m3` is resolving to the `sentence-similarity` pipeline, causing errors like:
  - `SentenceSimilarityPipeline.__call__() missing 1 required positional argument: 'sentences'`
  - `SentenceEmbeddingPipeline.__call__() got an unexpected keyword argument 'transcript'`
- Any code path calling `HFBgeM3Embedder` against the router returns 400s; text/audio/image retrieval and indexing fail.

## Root Cause
- The HF router now defaults `BAAI/bge-m3` to sentence-similarity; it no longer exposes feature-extraction embeddings over that route.

## What Works
- Local SentenceTransformer embedding (e.g., `SentenceTransformer('BAAI/bge-m3')`) or another local model.
- Alternatively, a different API/model that supports feature-extraction.

## Recommended Fix (step-by-step)
1) Switch to local embeddings:
   - Install: `pip install sentence-transformers`
   - Use `SentenceTransformer('BAAI/bge-m3')` (or a smaller model like `intfloat/e5-base`) for embeddings.
2) If you need remote:
   - Use an API that exposes feature-extraction, or host your own.
   - Point `HF_API_URL_BGE` to that feature-extraction endpoint.

## Optional Architecture (was prototyped, now reverted)
- A text embedding orchestrator that chooses local/remote (auto fallback).
- Local embedder via SentenceTransformer.
- Remote embedder wrapper for future API.
- Backward-compat shim so existing `HFBgeM3Embedder()` call sites work without import changes.

## Torch/Transformers Compatibility
- If using newer transformers with sentence-transformers, ensure torch >= 2.2.0 to avoid `torch.utils._pytree` attribute errors.

## Action Items (if re-implementing)
- Decide: local vs remote.
- If local: add `sentence-transformers` dep, implement local embedder + orchestrator, reuse old call sites via shim.
- If remote: set a feature-extraction-capable endpoint and keep `HFBgeM3Embedder` delegating to that.
