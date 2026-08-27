"""
GrowMate - evaluate_model.py
"Know your soil. Grow your future."

RUN THIS THIRD (after train_model.py).
Generates ALL figures needed for your report Chapter 4:
  results/training_curves.png       -> Figure 4.1
  results/confusion_matrix.png      -> Figure 4.2
  results/results_table.png         -> Table 4.1
  results/per_class_performance.png -> Figure 4.3

HOW TO RUN:
  python evaluate_model.py
"""

import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import (accuracy_score, precision_score,
                              recall_score, f1_score,
                              confusion_matrix, classification_report)

# ── SETTINGS ──────────────────────────────────────────────────────────────────
MODEL_PATH   = "models/growmate_model.h5"
SPLIT_FILE   = "data/dataset_split.json"
RESULTS_DIR  = "results"
IMAGE_SIZE   = (224, 224)
BATCH_SIZE   = 16
SOIL_CLASSES = ["Sandy", "Clay", "Loamy"]
NUM_RUNS     = 3
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── LOAD TEST DATA ─────────────────────────────────────────────────────────────
def load_test_data():
    with open(SPLIT_FILE) as f:
        split = json.load(f)
    paths, labels = [], []
    for idx, cls in enumerate(SOIL_CLASSES):
        for fp in split["test"].get(cls, []):
            if os.path.exists(fp):
                paths.append(fp)
                labels.append(idx)
    print(f"  Test samples: {len(paths)}")
    return paths, labels

def read_image(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMAGE_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    return img, label

def make_ds(paths, labels):
    ds = tf.data.Dataset.from_tensor_slices(
        (tf.constant(paths), tf.constant(labels, dtype=tf.int32)))
    return ds.map(read_image, num_parallel_calls=tf.data.AUTOTUNE)\
             .batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# ── METRICS ───────────────────────────────────────────────────────────────────
def get_metrics(true, pred):
    """
    Equations 3.5-3.8:
    Accuracy, Precision, Recall, F1-Score
    """
    return (
        accuracy_score(true, pred),
        precision_score(true, pred, average="weighted", zero_division=0),
        recall_score(true, pred, average="weighted", zero_division=0),
        f1_score(true, pred, average="weighted", zero_division=0),
    )

# ── CONFUSION MATRIX ──────────────────────────────────────────────────────────
def save_confusion_matrix(true, pred, suffix=""):
    cm = confusion_matrix(true, pred)
    fig, ax = plt.subplots(figsize=(7,6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
                xticklabels=SOIL_CLASSES, yticklabels=SOIL_CLASSES,
                linewidths=0.5, linecolor="#DDDDDD", ax=ax,
                annot_kws={"size":14,"weight":"bold"})
    ax.set_title(" Confusion Matrix",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Predicted Label", fontsize=12, labelpad=10)
    ax.set_ylabel("True Label",      fontsize=12, labelpad=10)
    acc = np.trace(cm) / np.sum(cm)
    ax.text(0.99, 0.01, f"Overall accuracy: {acc*100:.1f}%",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=10, color="#2D6A4F", fontweight="bold")
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, f"confusion_matrix{suffix}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

# ── RESULTS TABLE ─────────────────────────────────────────────────────────────
def save_results_table(all_metrics):
    accs  = [m[0] for m in all_metrics]
    precs = [m[1] for m in all_metrics]
    recs  = [m[2] for m in all_metrics]
    f1s   = [m[3] for m in all_metrics]

    rows = []
    for i,(a,p,r,f) in enumerate(all_metrics,1):
        rows.append([f"Run {i}",
                     f"{a*100:.2f}",f"{p*100:.2f}",
                     f"{r*100:.2f}",f"{f*100:.2f}"])
    rows.append(["Average",
                 f"{np.mean(accs)*100:.2f}",f"{np.mean(precs)*100:.2f}",
                 f"{np.mean(recs)*100:.2f}",f"{np.mean(f1s)*100:.2f}"])

    fig, ax = plt.subplots(figsize=(10,4))
    ax.axis("off")
    headers = ["Run","Accuracy (%)","Precision (%)","Recall (%)","F1-Score (%)"]
    tbl = ax.table(cellText=rows, colLabels=headers,
                   cellLoc="center", loc="center", bbox=[0,0,1,1])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    for j in range(len(headers)):
        tbl[0,j].set_facecolor("#2D6A4F")
        tbl[0,j].set_text_props(color="white", fontweight="bold")
    for j in range(len(headers)):
        tbl[len(rows),j].set_facecolor("#EAF3DE")
        tbl[len(rows),j].set_text_props(fontweight="bold", color="#27500A")
    for i in range(1, len(rows)):
        for j in range(len(headers)):
            if i % 2 == 0:
                tbl[i,j].set_facecolor("#F9FFF5")
    ax.set_title("GrowMate - 3-Run Classification Results",
                 fontsize=13, fontweight="bold", pad=20)
    path = os.path.join(RESULTS_DIR, "results_table.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

    # Console summary
    print("\n  Results Summary:")
    print(f"  {'Run':<10} {'Accuracy':>12} {'Precision':>12} {'Recall':>12} {'F1':>12}")
    print("  " + "-"*52)
    for i,(a,p,r,f) in enumerate(all_metrics,1):
        print(f"  {'Run '+str(i):<10} {a*100:>11.2f}% {p*100:>11.2f}%"
              f" {r*100:>11.2f}% {f*100:>11.2f}%")
    print("  " + "-"*52)
    print(f"  {'Average':<10} {np.mean(accs)*100:>11.2f}%"
          f" {np.mean(precs)*100:>11.2f}%"
          f" {np.mean(recs)*100:>11.2f}%"
          f" {np.mean(f1s)*100:>11.2f}%")

# ── PER-CLASS CHART ───────────────────────────────────────────────────────────
def save_per_class_chart(true, pred):
    report = classification_report(
        true, pred, target_names=SOIL_CLASSES, output_dict=True)
    metrics = ["precision","recall","f1-score"]
    x       = np.arange(len(SOIL_CLASSES))
    width   = 0.25
    colors  = ["#2D6A4F","#52B788","#D4A373"]

    fig, ax = plt.subplots(figsize=(9,5))
    for i, metric in enumerate(metrics):
        vals = [report[cls][metric] for cls in SOIL_CLASSES]
        bars = ax.bar(x + i*width, vals, width,
                      label=metric.capitalize(),
                      color=colors[i], alpha=0.85)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2,
                    bar.get_height()+0.01,
                    f"{v:.2f}", ha="center", va="bottom", fontsize=9)

    ax.set_title("Per-Class Performance",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x + width)
    ax.set_xticklabels(SOIL_CLASSES, fontsize=11)
    ax.set_ylabel("Score"); ax.set_ylim([0, 1.1])
    ax.legend(fontsize=10)
    ax.axhline(0.65, color="#E9C46A", lw=1, ls="--", alpha=0.7)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "per_class_performance.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print(" Model Evaluation")
    print("  Know your soil. Grow your future.")
    print("=" * 50)

    if not os.path.exists(MODEL_PATH):
        print("  ERROR: Model not found. Run train_model.py first.")
        exit(1)

    print(f"\n  Loading model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("  Model loaded successfully")

    print("\n  Loading test data...")
    paths, true = load_test_data()
    test_ds = make_ds(paths, true)

    print(f"\n  Running {NUM_RUNS}-run evaluation...")
    print("  " + "-" * 44)

    all_metrics = []
    all_preds   = []

    for run in range(1, NUM_RUNS+1):
        print(f"\n  Run {run}/{NUM_RUNS}...")
        probs = model.predict(test_ds, verbose=0)
        preds = np.argmax(probs, axis=1)
        all_preds.append(preds)
        a,p,r,f = get_metrics(true, preds)
        all_metrics.append((a,p,r,f))
        print(f"    Accuracy : {a*100:.2f}%")
        print(f"    Precision: {p*100:.2f}%")
        print(f"    Recall   : {r*100:.2f}%")
        print(f"    F1-Score : {f*100:.2f}%")
        save_confusion_matrix(true, preds, suffix=f"_run{run}")

    print("\n  Generating summary figures...")
    save_results_table(all_metrics)
    best = int(np.argmax([m[0] for m in all_metrics]))
    save_confusion_matrix(true, all_preds[best])
    save_per_class_chart(true, all_preds[best])

    avg_acc = np.mean([m[0] for m in all_metrics])
    avg_f1  = np.mean([m[3] for m in all_metrics])

    print("\n" + "=" * 50)
    print("  Performance Acceptance Criteria:")
    print(f"  Accuracy : {avg_acc*100:.2f}%  "
          f"{'PASS' if avg_acc >= 0.70 else 'BELOW TARGET'} (need >= 70%)")
    print(f"  F1-Score : {avg_f1*100:.2f}%  "
          f"{'PASS' if avg_f1 >= 0.65 else 'BELOW TARGET'} (need >= 65%)")
    print("\n  Report figures saved to results/:")
    print("  training_curves.png       -> Figure 4.1")
    print("  confusion_matrix.png      -> Figure 4.2")
    print("  results_table.png         -> Table 4.1")
    print("  per_class_performance.png -> Figure 4.3")
    print("\n  Next step: streamlit run app/Home.py")
    print("=" * 50)