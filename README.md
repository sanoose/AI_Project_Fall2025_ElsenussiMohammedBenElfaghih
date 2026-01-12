# Bilingual Sentiment Analysis (EN/AR) — BERT + FastAPI + Vue

This repository contains a bilingual sentiment analysis system that supports **English** and **Arabic**. Two fine-tuned Transformer models are served through a unified FastAPI endpoint, and a Vue-based UI is provided for interaction.

## Repository Structure
- `backend/` : FastAPI service + training scripts + saved models
- `frontEnd/` : Vue.js client application

## Features
- English sentiment model (BERT) and Arabic sentiment model (AraBERT)
- Unified API endpoint: `POST /predict`
- Optional probability output: `probs` via `return_probs`
- Optional token-level explanation output: `explain` via `return_explain` (includes `score` and `contribution`)
- Automatic language detection when `lang` is omitted
- Mixed Arabic/English input is rejected with a clear error message
- CORS enabled for Vite dev server origins

---

## Backend (FastAPI)

### Prerequisites
- Python 3.10+ (recommended)
- (Optional) NVIDIA GPU + CUDA for faster inference/training

### Setup
```bash
cd backend

python -m venv .your_venv_name
# Windows:
.your_venv_name\Scripts\activate
# Linux/Mac:
source .your_venv_name/bin/activate

pip install -U pip
pip install -r requirements.txt



### Train Models (one-time)
The following scripts will fine-tune and save the models to:
- `backend/models/en` (English)
- `backend/models/ar` (Arabic)
 
python train_en.py
python train_ar.py

### Run the API 
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload



### Frontend (Vue)
### Setup & Run
#node js 20+ is required
cd frontEnd
npm install
npm run dev


### Test the API

#Health Check

  GET /health

# Prediction

POST /predict

# Example request body:
{
  "text": "the book is excellent",
  "lang": "en",
  "return_probs": true,
  "return_explain": true,
  "top_k": 10
}
#Example response (structure): 
{
  "label_id": 1,
  "confidence": 0.99,
  "probs": [0.01, 0.99],
  "lang": "en",
  "explain": [
    { "token": "excellent", "score": 0.12, "contribution": 0.12 }
  ]
}

## Notes
- If the model folders under `backend/models/` are not available, the training scripts (`train_en.py`, `train_ar.py`) should be executed first to generate them locally.
- `contribution` is a signed attribution value indicating whether a token supports or opposes the selected target class, while `score = abs(contribution)` is used to rank tokens by influence magnitude.
- The trained model artifacts can be handled in one of two ways:
  - Generated locally (recommended for large files), or
  - Tracked using Git LFS if the models must be stored in the repository.