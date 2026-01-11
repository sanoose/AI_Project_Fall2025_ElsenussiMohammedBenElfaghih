import os
from typing import Optional

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification



BASE_DIR = os.path.dirname(__file__)
EN_DIR = os.path.join(BASE_DIR, "models", "en")
AR_DIR = os.path.join(BASE_DIR, "models", "ar")

app = FastAPI(title="Sentiment API (EN/AR)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=  [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    ]   , 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = None

en_tokenizer = None
en_model = None

ar_tokenizer = None
ar_model = None


class PredictRequest(BaseModel):
    text: str
    lang: Optional[str] = None  # "en" | "ar" | None (auto)
    return_probs: bool = False
    return_explain: Optional[bool] = False
    top_k: Optional[int] = 10

def detect_lang_simple(text: str) -> str:
    ar = 0
    en = 0

    for ch in text:
        code = ord(ch)
#  unicode betweens 
        is_ar = (
            (0x0600 <= code <= 0x06FF)
            or (0x0750 <= code <= 0x077F)
            or (0x08A0 <= code <= 0x08FF)
            or (0xFB50 <= code <= 0xFDFF)
            or (0xFE70 <= code <= 0xFEFF)
        )
        is_en = (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A)

        if is_ar:
            ar += 1
        elif is_en:
            en += 1

    if ar > 0 and en > 0:
        return "mixed"
    if ar > 0:
        return "ar"
    if en > 0:
        return "en"
    return "unknown"


def predict_with(model, tokenizer, text: str, return_probs: bool):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)   # pt  =  make the results  tensors for pyTourch 
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)



    probs = torch.softmax(outputs.logits, dim=-1)[0].detach().cpu().tolist()
    pred_id = int(torch.argmax(outputs.logits, dim=-1).item())  # 0/1

    resp = {
        "label_id": pred_id,            # <-- المطلوب
        "confidence": float(probs[pred_id]),
    }
    if return_probs:
        resp["probs"] = probs
    return resp
 
def explain_with(model, tokenizer, text: str, target_id: int, top_k: int = 10):
    model.eval()

    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    input_ids = inputs["input_ids"]
    attention_mask = inputs.get("attention_mask")


    emb_layer = model.get_input_embeddings()
    embeds = emb_layer(input_ids).detach().clone().requires_grad_(True)

    outputs = model(inputs_embeds=embeds, attention_mask=attention_mask)
    logit = outputs.logits[0, int(target_id)]

    model.zero_grad()

    grads = torch.autograd.grad(
        outputs=logit,
        inputs=embeds,
        retain_graph=False,
        create_graph=False,
        allow_unused=False
    )[0]  

    contrib = (grads * embeds).sum(dim=-1)[0]  
    importance = contrib.abs()         

    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].detach().cpu().tolist())
    special = set(getattr(tokenizer, "all_special_tokens", []))

    items = []
    for i, tok in enumerate(tokens):
        if tok in special:
            continue
        if attention_mask is not None and int(attention_mask[0, i].item()) == 0:
            continue

        items.append({
            "token": tok,
            "score": float(importance[i].detach().cpu().item()),
            "contribution": float(contrib[i].detach().cpu().item()),
        })
 
    items.sort(key=lambda x: x["score"], reverse=True)
    k = max(1, min(int(top_k or 10), 50))
    return items[:k]


@app.on_event("startup")
def startup():
    global device, en_tokenizer, en_model, ar_tokenizer, ar_model

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not os.path.exists(os.path.join(EN_DIR, "config.json")):
        raise RuntimeError(f"EN model not found at: {EN_DIR}. Run train_en.py first.")
    if not os.path.exists(os.path.join(AR_DIR, "config.json")):
        # يمكن تركه اختياريًا، لكن الأفضل يكون موجود قبل تشغيل API متعدد اللغات
        raise RuntimeError(f"AR model not found at: {AR_DIR}. Run train_ar.py first.")

    en_tokenizer = AutoTokenizer.from_pretrained(EN_DIR)
    en_model = AutoModelForSequenceClassification.from_pretrained(EN_DIR).to(device)
    en_model.eval()

    ar_tokenizer = AutoTokenizer.from_pretrained(AR_DIR)
    ar_model = AutoModelForSequenceClassification.from_pretrained(AR_DIR).to(device)
    ar_model.eval()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "device": str(device),
        "en_dir": EN_DIR,
        "ar_dir": AR_DIR,
    }


# 3) عدّل endpoint /predict (هذا هو التعديل الذي طلبته على دالتك)
@app.post("/predict")
def predict(req: PredictRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    lang = (req.lang or "").lower().strip()
    if lang not in ("", "en", "ar"):
        raise HTTPException(status_code=400, detail="lang must be 'en' or 'ar' or omitted for auto")

    if lang == "":
        lang = detect_lang_simple(text)

    if lang == "mixed":
        raise HTTPException(status_code=400, detail="Mixed Arabic/English text is not supported")
    if lang == "unknown":
        raise HTTPException(status_code=400, detail="Could not detect language")

    if lang == "en":
        out = predict_with(en_model, en_tokenizer, text, bool(req.return_probs))
        out["lang"] = "en"

        if bool(req.return_explain):
            out["explain"] = explain_with(
                en_model, en_tokenizer, text,
                target_id=int(out["label_id"]),
                top_k=int(req.top_k or 10),
            )
        return out

    if lang == "ar":
        out = predict_with(ar_model, ar_tokenizer, text, bool(req.return_probs))
        out["lang"] = "ar"

        if bool(req.return_explain):
            out["explain"] = explain_with(
                ar_model, ar_tokenizer, text,
                target_id=int(out["label_id"]),
                top_k=int(req.top_k or 10),
            )
        return out

    raise HTTPException(status_code=400, detail="Unsupported language")
