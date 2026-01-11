import os
import math
import numpy as np
import torch

from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import accuracy_score, f1_score


# =========================
# Config
# =========================
MODEL_NAME = "aubmindlab/bert-base-arabertv2"
DATASET_NAME = "mohamedadaly/labr"  # LABR dataset on HF :contentReference[oaicite:1]{index=1}

BASE_DIR = os.path.dirname(__file__)
SAVE_DIR = os.path.join(BASE_DIR, "models", "ar")
OUTPUT_DIR = os.path.join(BASE_DIR, "checkpoints_ar")

EPOCHS = 3
LR = 2e-5
TRAIN_BATCH = 8
EVAL_BATCH = 8
SEED = 42

TOTAL_SAMPLES = 50_000  # سيتم تقليصه تلقائيًا لو الداتا أقل بعد فلترة النجوم
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

# FORCE_RETRAIN = False
FORCE_RETRAIN = True


# =========================
# Helpers
# =========================
def model_is_saved(save_dir: str) -> bool:
    return os.path.exists(save_dir) and os.path.exists(os.path.join(save_dir, "config.json"))


def validate_ratios(a, b, c):
    s = a + b + c
    if not math.isclose(s, 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(f"Ratios must sum to 1.0. Got: {s}")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, average="weighted"),
    }


def find_key(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    raise KeyError(f"Could not find any of keys {candidates} in columns: {cols}")


def build_splits_from_total_labr(total_samples: int):
    validate_ratios(TRAIN_RATIO, VAL_RATIO, TEST_RATIO)

    ds = load_dataset(DATASET_NAME)

    # dd = load_dataset("mohamedadaly/labr")
    # full = concatenate_datasets([dd["train"], dd["test"]])
    # print(len(dd["train"]), len(dd["test"]), len(full))  # 11760, 2935, 14695
    # full.to_csv("labr_full_hf.csv")
    # return 2


    # LABR قد يأتي بدون تقسيمات ثابتة؛ نجمع أي splits موجودة
    splits = []
    for name in ds.keys():
        splits.append(ds[name])
    full = concatenate_datasets(splits).shuffle(seed=SEED)

    cols = full.column_names
    text_key = find_key(cols, ["text", "review", "sentence"])
    rating_key = find_key(cols, ["rating", "stars", "rate", "label"])

    # فلترة: نحافظ على 1-2 و 4-5 فقط، ونستبعد 3
    # نجمة ونجمتين سلبي و 4 و 5 ايجابي 
    def keep_row(x):
        r = int(x[rating_key])
        return r in (1, 2, 4, 5)

    full = full.filter(keep_row)

    # تحويل النجوم إلى label 0/1
    def map_label(x):
        r = int(x[rating_key])
        x["labels"] = 0 if r in (1, 2) else 1
        x["text_for_model"] = x[text_key]
        return x

    full = full.map(map_label)

    use_n = min(total_samples, len(full))
    full = full.select(range(use_n))

    test_n = int(use_n * TEST_RATIO)
    val_n = int(use_n * VAL_RATIO)
    train_n = use_n - val_n - test_n

    train_ds = full.select(range(0, train_n))
    val_ds = full.select(range(train_n, train_n + val_n))
    test_ds = full.select(range(train_n + val_n, use_n))

    print(
        f"[AR] TOTAL(after filter)={use_n} -> train={len(train_ds)} ({TRAIN_RATIO:.0%}) "
        f"val={len(val_ds)} ({VAL_RATIO:.0%}) test={len(test_ds)} ({TEST_RATIO:.0%})"
    )
    return train_ds, val_ds, test_ds


def main():
    already_saved = model_is_saved(SAVE_DIR)
    should_train = (not already_saved) or FORCE_RETRAIN

    if already_saved and not should_train:
        print(f"[AR] Found saved model in: {SAVE_DIR} -> Skipping training.")
        tokenizer = AutoTokenizer.from_pretrained(SAVE_DIR)
        model = AutoModelForSequenceClassification.from_pretrained(SAVE_DIR)
    else:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME,
            num_labels=2,
            id2label={0: "NEGATIVE", 1: "POSITIVE"},
            label2id={"NEGATIVE": 0, "POSITIVE": 1},
        )

    train_ds, val_ds, test_ds = build_splits_from_total_labr(TOTAL_SAMPLES)

    def tokenize_fn(batch):
        return tokenizer(batch["text_for_model"], truncation=True)

    # نحذف الأعمدة غير اللازمة ونترك labels
    remove_cols = [c for c in train_ds.column_names if c not in ("labels", "text_for_model")]
    train_ds = train_ds.map(tokenize_fn, batched=True, remove_columns=remove_cols + ["text_for_model"])
    val_ds = val_ds.map(tokenize_fn, batched=True, remove_columns=remove_cols + ["text_for_model"])
    test_ds = test_ds.map(tokenize_fn, batched=True, remove_columns=remove_cols + ["text_for_model"])

    collator = DataCollatorWithPadding(tokenizer=tokenizer)

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=50,
        learning_rate=LR,
        per_device_train_batch_size=TRAIN_BATCH,
        per_device_eval_batch_size=EVAL_BATCH,
        num_train_epochs=EPOCHS,
        weight_decay=0.01,
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",   # how to choose best model
        save_total_limit=2,
        seed=SEED,
        save_safetensors=True,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )

    if should_train:
        trainer.train()
        trainer.model.save_pretrained(SAVE_DIR)
        tokenizer.save_pretrained(SAVE_DIR)
        print(f"[AR] Saved model to: {SAVE_DIR}")

    print("\n[AR] Validation Metrics:")
    print(trainer.evaluate())

    print("\n[AR] Test Metrics:")
    print(trainer.evaluate(eval_dataset=test_ds))


if __name__ == "__main__":
    main()
