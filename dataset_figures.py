"""
GrowMate - dataset_figures.py
"Know your soil. Grow your future."

RUN THIS AFTER prepare_data.py.
Generates dataset analysis figures for Chapter 3 of your report:
  results/dataset_distribution.png  -> Figure 3.x
  results/npk_distribution.png      -> Figure 3.x
  results/sample_grid.png           -> Figure 3.x
  results/augmentation_demo.png     -> Figure 3.x

HOW TO RUN:
  python dataset_figures.py
"""

import os, json, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance

RESULTS_DIR  = "results"
SPLIT_FILE   = "data/dataset_split.json"
SOIL_CLASSES = ["Sandy","Clay","Loamy"]
COLORS       = {"Sandy":"#E9C46A","Clay":"#D4A373","Loamy":"#52B788"}
NPK_EST      = {
    "Sandy":{"N":"Low",   "P":"Low",   "K":"Medium"},
    "Clay": {"N":"Medium","P":"Medium","K":"Medium"},
    "Loamy":{"N":"High",  "P":"Medium","K":"High"},
}
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── 1. DATASET DISTRIBUTION ───────────────────────────────────────────────────
def plot_dataset_distribution():
    if not os.path.exists(SPLIT_FILE):
        print("  Skipping dataset_distribution - run prepare_data.py first")
        return
    with open(SPLIT_FILE) as f:
        split = json.load(f)

    tc = [len(split["train"].get(c,[])) for c in SOIL_CLASSES]
    vc = [len(split["val"].get(c,[]))   for c in SOIL_CLASSES]
    ec = [len(split["test"].get(c,[]))  for c in SOIL_CLASSES]

    x     = np.arange(len(SOIL_CLASSES))
    width = 0.25
    fig, axes = plt.subplots(1, 2, figsize=(14,5))
    fig.suptitle("Dataset Overview",
                 fontsize=14, fontweight="bold")

    ax = axes[0]
    for bars, label, color in [
        (ax.bar(x-width, tc, width, label="Train",      color="#2D6A4F", alpha=0.85), "Train", "#2D6A4F"),
        (ax.bar(x,       vc, width, label="Validation", color="#52B788", alpha=0.85), "Val",   "#52B788"),
        (ax.bar(x+width, ec, width, label="Test",       color="#D4A373", alpha=0.85), "Test",  "#D4A373"),
    ]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, h+1,
                    str(int(h)), ha="center", va="bottom", fontsize=9)
    ax.set_title("Images per class per split", fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(SOIL_CLASSES, fontsize=11)
    ax.set_ylabel("Number of images"); ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    totals = [t+v+e for t,v,e in zip(tc,vc,ec)]
    wedge_colors = [COLORS[c] for c in SOIL_CLASSES]
    _, texts, autotexts = axes[1].pie(
        totals, labels=SOIL_CLASSES, colors=wedge_colors,
        autopct="%1.1f%%", startangle=90,
        textprops={"fontsize":11})
    for at in autotexts:
        at.set_fontweight("bold")
    axes[1].set_title("Total class distribution", fontweight="bold")

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "dataset_distribution.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

# ── 2. NPK DISTRIBUTION ───────────────────────────────────────────────────────
def plot_npk_distribution():
    nutrients = ["Nitrogen (N)","Phosphorus (P)","Potassium (K)"]
    keys      = ["N","P","K"]
    lv        = {"Low":1,"Medium":2,"High":3}
    lc        = {"Low":"#E24B4A","Medium":"#E9C46A","High":"#52B788"}

    fig, axes = plt.subplots(1, 3, figsize=(14,5))
    fig.suptitle("Estimated NPK Levels by Soil Class",
                 fontsize=14, fontweight="bold")

    for ax, nutrient, key in zip(axes, nutrients, keys):
        levels = [NPK_EST[c][key] for c in SOIL_CLASSES]
        vals   = [lv[l] for l in levels]
        bcols  = [lc[l] for l in levels]
        bars   = ax.bar(SOIL_CLASSES, vals, color=bcols,
                        alpha=0.85, edgecolor="white", linewidth=1.5)
        for bar, level in zip(bars, levels):
            ax.text(bar.get_x()+bar.get_width()/2,
                    bar.get_height()/2,
                    level, ha="center", va="center",
                    fontweight="bold", fontsize=12, color="white")
        ax.set_title(nutrient, fontweight="bold", fontsize=12)
        ax.set_yticks([1,2,3])
        ax.set_yticklabels(["Low","Medium","High"])
        ax.set_ylim([0,3.5])
        ax.grid(True, axis="y", alpha=0.3)
        for spine in ["top","right"]:
            ax.spines[spine].set_visible(False)

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "npk_distribution.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

# ── 3. SAMPLE IMAGE GRID ──────────────────────────────────────────────────────
def plot_sample_grid():
    if not os.path.exists(SPLIT_FILE):
        print("  Skipping sample_grid - run prepare_data.py first")
        return
    with open(SPLIT_FILE) as f:
        split = json.load(f)

    fig = plt.figure(figsize=(14,9))
    fig.suptitle("Sample Soil Images by Class",
                 fontsize=14, fontweight="bold")
    found = False
    for row, cls in enumerate(SOIL_CLASSES):
        all_files = (split["train"].get(cls,[]) +
                     split["val"].get(cls,[]) +
                     split["test"].get(cls,[]))
        all_files = [f for f in all_files if os.path.exists(f)]
        samples   = random.sample(all_files, min(4, len(all_files)))
        for col, fpath in enumerate(samples):
            found = True
            ax = fig.add_subplot(3, 4, row*4 + col + 1)
            ax.imshow(Image.open(fpath).convert("RGB"))
            ax.axis("off")
            if col == 0:
                ax.set_ylabel(cls, fontsize=12, fontweight="bold",
                              color=COLORS[cls], rotation=90, labelpad=8)
            if row == 0:
                ax.set_title(f"Sample {col+1}", fontsize=10, color="#555")

    if not found:
        print("  Skipping sample_grid - no processed images found")
        plt.close(); return

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "sample_grid.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

# ── 4. AUGMENTATION DEMO ─────────────────────────────────────────────────────
def plot_augmentation_demo():
    if not os.path.exists(SPLIT_FILE):
        print("  Skipping augmentation_demo - run prepare_data.py first")
        return
    with open(SPLIT_FILE) as f:
        split = json.load(f)

    candidates = []
    for cls in SOIL_CLASSES:
        candidates += [f for f in split["train"].get(cls,[])
                       if os.path.exists(f)]
    if not candidates:
        print("  Skipping augmentation_demo - no images found")
        return

    orig = Image.open(random.choice(candidates)).convert("RGB").resize((224,224))
    augmented = [
        ("Horizontal flip",  orig.transpose(Image.FLIP_LEFT_RIGHT)),
        ("Rotation +15 deg", orig.rotate(15, expand=False)),
        ("Brightness +40%",  ImageEnhance.Brightness(orig).enhance(1.4)),
        ("Brightness -30%",  ImageEnhance.Brightness(orig).enhance(0.7)),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(16,4))
    fig.suptitle(" Data Augmentation Pipeline",
                 fontsize=13, fontweight="bold")

    axes[0].imshow(orig)
    axes[0].set_title("Original", fontweight="bold", color="#2D6A4F")
    axes[0].axis("off")

    for ax, (title, img) in zip(axes[1:], augmented):
        ax.imshow(img); ax.set_title(title, fontsize=10); ax.axis("off")

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "augmentation_demo.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Dataset Figures")
    print("  Know your soil. Grow your future.")
    print("=" * 50)
    print("\n  Generating figures...")
    print("  " + "-" * 44)
    plot_dataset_distribution()
    plot_npk_distribution()
    plot_sample_grid()
    plot_augmentation_demo()
    print("\n" + "=" * 50)
    print("  All figures saved to results/")
    print("  dataset_distribution.png -> Chapter 3 Figure 3.x")
    print("  npk_distribution.png     -> Chapter 3 Figure 3.x")
    print("  sample_grid.png          -> Chapter 3 Figure 3.x")
    print("  augmentation_demo.png    -> Chapter 3 Figure 3.x")
    print("=" * 50)