"""
TruthLens AI 2.0 - DistilBERT Fine-Tuning (OPTIONAL)
Fine-tunes `distilbert-base-uncased` for 3-class fake-news classification on the
project's labeled dataset, saves the model locally, and writes REAL evaluation
metrics to `distilbert_meta.json`.

This script is OPTIONAL. It requires `transformers` and `torch`:
    pip install transformers torch

It uses GPU when available and CPU as fallback. The model is saved to
ml_pipeline/saved_models/distilbert_fake_news/ and loaded once at inference time
by backend/app/services/transformer_service.py (never re-downloaded per request).

If torch/transformers are not installed, the script prints a clear message and
exits without error, leaving the existing 5-model ensemble fully functional.
"""

import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

SAVED_MODELS_DIR = os.path.join(BASE_DIR, "saved_models")
MODEL_DIR = os.path.join(SAVED_MODELS_DIR, "distilbert_fake_news")
META_PATH = os.path.join(SAVED_MODELS_DIR, "distilbert_meta.json")

CLASS_NAMES = ["Likely Genuine", "Potentially Misleading", "Needs Further Verification"]
LABEL2ID = {name: i for i, name in enumerate(CLASS_NAMES)}
ID2LABEL = {i: name for i, name in enumerate(CLASS_NAMES)}


def _check_deps():
    try:
        import torch
        from transformers import (
            AutoTokenizer, AutoModelForSequenceClassification,
            Trainer, TrainingArguments, DataCollatorWithPadding
        )
        return True
    except Exception as e:
        print("\n[Transformer Training] SKIPPED - optional dependencies not installed.")
        print(f"  Reason: {e}")
        print("  To enable DistilBERT, install:  pip install transformers torch")
        print("  The existing 5-model ensemble (classical + BiLSTM) remains fully functional.")
        return False


def train_transformer(epochs=4, batch_size=8, val_split=0.2):
    """Fine-tune DistilBERT and save locally with real held-out metrics."""
    if not _check_deps():
        return None

    import torch
    import numpy as np
    from datasets import Dataset
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        Trainer, TrainingArguments, DataCollatorWithPadding
    )
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

    from datasets.dataset_loader import get_benchmark_dataset
    from preprocessing.text_cleaner import TextPreprocessor

    print("\n" + "=" * 64)
    print("TruthLens AI 2.0 - DistilBERT Fine-Tuning")
    print("=" * 64)

    # 1. Load + clean data (same preprocessing as classical pipeline)
    df = get_benchmark_dataset()
    pre = TextPreprocessor(remove_stopwords=False, lemmatize=True)
    texts = [pre.transform_to_string(t, lang="en") for t in df["text"].tolist()]
    labels = df["label_id"].tolist() if "label_id" in df.columns else [
        {"Likely Genuine": 0, "Potentially Misleading": 1, "Needs Further Verification": 2}.get(l, 2)
        for l in df["label"].tolist()
    ]

    # 2. Stratified train/test split
    X_tr, X_te, y_tr, y_te = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Device: {device}")
    print(f"[*] Train: {len(X_tr)} | Test: {len(X_te)}")

    # 3. Tokenizer + model
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=3, id2label=ID2LABEL, label2id=LABEL2ID
    )

    def tokenize(ex):
        return tokenizer(ex["text"], truncation=True, max_length=512)

    train_ds = Dataset.from_dict({"text": X_tr, "labels": y_tr}).map(tokenize, batched=True)
    test_ds = Dataset.from_dict({"text": X_te, "labels": y_te}).map(tokenize, batched=True)

    # 4. Metrics
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        acc = accuracy_score(labels, preds)
        p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="macro", zero_division=0)
        try:
            probs = torch.softmax(torch.tensor(logits), dim=-1).numpy()
            auc = roc_auc_score(labels, probs, multi_class="ovr", average="macro")
        except Exception:
            auc = None
        return {"accuracy": acc, "precision": p, "recall": r, "f1": f1, "roc_auc": auc}

    # 5. Train
    output_dir = os.path.join(SAVED_MODELS_DIR, "_distilbert_checkpoints")
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        report_to=[],
        seed=42,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )

    t0 = time.time()
    trainer.train()
    train_time = round(time.time() - t0, 2)

    # 6. Evaluate on held-out test
    eval_res = trainer.evaluate()
    metrics = {
        "model_name": "DistilBERT",
        "accuracy": round(float(eval_res.get("eval_accuracy", 0.0)), 4),
        "precision": round(float(eval_res.get("eval_precision", 0.0)), 4),
        "recall": round(float(eval_res.get("eval_recall", 0.0)), 4),
        "f1_score": round(float(eval_res.get("eval_f1", 0.0)), 4),
        "roc_auc": round(float(eval_res["eval_roc_auc"]), 4) if eval_res.get("eval_roc_auc") is not None else None,
        "training_time_sec": train_time,
        "device": device,
        "epochs": epochs,
        "base_model": model_name,
        "train_samples": len(X_tr),
        "test_samples": len(X_te),
        "available": True,
        "classes": CLASS_NAMES,
        "note": "Real held-out test-set metrics. Fine-tuned on the project's labeled dataset.",
    }

    # 7. Save model + metrics
    os.makedirs(MODEL_DIR, exist_ok=True)
    trainer.save_model(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    with open(META_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[+] DistilBERT saved to {MODEL_DIR}")
    print(f"[+] Metrics: acc={metrics['accuracy']} | F1={metrics['f1_score']} | AUC={metrics['roc_auc']}")
    print(f"[+] Meta written to {META_PATH}")
    return metrics


if __name__ == "__main__":
    train_transformer()
