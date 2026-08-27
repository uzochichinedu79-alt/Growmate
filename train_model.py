"""
GrowMate - train_model.py
"Know your soil. Grow your future."

RUN THIS SECOND (after prepare_data.py).
What it does:
  1. Loads your processed images from the dataset split
  2. Builds MobileNetV2 with a custom classification head
  3. Trains it with early stopping and learning rate scheduling
  4. Saves the best model to models/growmate_model.h5
  5. Saves training curve graphs to results/

HOW TO RUN:
  python train_model.py

Training takes 15-40 minutes depending on your laptop.
If you get a memory error, change BATCH_SIZE from 16 to 8.
"""

import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications import MobileNetV2
from sklearn.utils import class_weight

# ── SETTINGS ──────────────────────────────────────────────────────────────────
SPLIT_FILE  = "data/dataset_split.json"
MODEL_DIR   = "models"
MODEL_PATH  = "models/growmate_model.h5"
LABELS_PATH = "models/class_labels.json"
RESULTS_DIR = "results"
IMAGE_SIZE  = (224, 224)
BATCH_SIZE  = 16        # change to 8 if you get memory errors
EPOCHS      = 30
LR          = 0.0001
SOIL_CLASSES= ["Sandy","Clay","Loamy"]
SEED        = 42

os.makedirs(MODEL_DIR,   exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
tf.random.set_seed(SEED)
np.random.seed(SEED)

# ── LOAD SPLIT ────────────────────────────────────────────────────────────────
def load_split():
    print("\n  Loading dataset split...")
    with open(SPLIT_FILE) as f:
        split = json.load(f)

    def flatten(subset):
        paths, labels = [], []
        for idx, cls in enumerate(SOIL_CLASSES):
            for fp in subset.get(cls, []):
                if os.path.exists(fp):
                    paths.append(fp)
                    labels.append(idx)
        return paths, labels

    train_p, train_l = flatten(split["train"])
    val_p,   val_l   = flatten(split["val"])
    test_p,  test_l  = flatten(split["test"])

    print(f"  Train : {len(train_p)} images")
    print(f"  Val   : {len(val_p)} images")
    print(f"  Test  : {len(test_p)} images")
    return (train_p, train_l), (val_p, val_l), (test_p, test_l)

# ── TF DATASET ────────────────────────────────────────────────────────────────
def read_image(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMAGE_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    return img, label

def augment(img, label):
    img = tf.image.random_flip_left_right(img)
    img = tf.image.random_brightness(img, max_delta=0.2)
    img = tf.image.random_contrast(img, lower=0.8, upper=1.2)
    img = tf.image.random_saturation(img, lower=0.8, upper=1.2)
    img = tf.clip_by_value(img, 0.0, 1.0)
    return img, label

def make_ds(paths, labels, training=False):
    ds = tf.data.Dataset.from_tensor_slices(
        (tf.constant(paths), tf.constant(labels, dtype=tf.int32)))
    ds = ds.map(read_image, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.shuffle(500, seed=SEED)\
               .map(augment, num_parallel_calls=tf.data.AUTOTUNE)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# ── BUILD MODEL ───────────────────────────────────────────────────────────────
def build_model():
    """
    MobileNetV2 transfer learning model.

    Architecture (Equation 3.2 - Softmax output):
      MobileNetV2 (ImageNet, top 30 layers unfrozen)
      -> GlobalAveragePooling2D
      -> Dense(256, ReLU) -> BatchNorm -> Dropout(0.4)
      -> Dense(128, ReLU) -> Dropout(0.3)
      -> Dense(3, Softmax)

    Loss: Sparse Categorical Cross-Entropy (Equation 3.3)
    """
    print("\n  Building MobileNetV2 model...")
    base = MobileNetV2(input_shape=(*IMAGE_SIZE, 3),
                       include_top=False, weights="imagenet")
    base.trainable = False

    inp = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x   = base(inp, training=False)
    x   = layers.GlobalAveragePooling2D()(x)
    x   = layers.Dense(256, activation="relu")(x)
    x   = layers.BatchNormalization()(x)
    x   = layers.Dropout(0.4)(x)
    x   = layers.Dense(128, activation="relu")(x)
    x   = layers.Dropout(0.3)(x)
    out = layers.Dense(3,   activation="softmax")(x)

    model = models.Model(inp, out, name="GrowMate_CNN")

    # Unfreeze top 30 layers for fine-tuning
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False

    print(f"  Trainable layers: "
          f"{sum(1 for l in model.layers if l.trainable)} / {len(model.layers)}")
    return model

# ── TRAIN ─────────────────────────────────────────────────────────────────────
def train(model, train_ds, val_ds, train_labels):
    model.compile(
        optimizer=optimizers.Adam(learning_rate=LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    cbs = [
        callbacks.ModelCheckpoint(
            MODEL_PATH, monitor="val_accuracy",
            save_best_only=True, verbose=1),
        callbacks.EarlyStopping(
            monitor="val_accuracy", patience=8,
            restore_best_weights=True, verbose=1),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=4, min_lr=1e-7, verbose=1),
    ]

    cw = class_weight.compute_class_weight(
        "balanced",
        classes=np.unique(train_labels),
        y=train_labels
    )
    cw_dict = dict(enumerate(cw))
    print(f"\n  Class weights: {cw_dict}")
    print(f"  Training for up to {EPOCHS} epochs | batch size {BATCH_SIZE}")
    print("  " + "-" * 44)

    history = model.fit(
        train_ds, validation_data=val_ds,
        epochs=EPOCHS, callbacks=cbs,
        class_weight=cw_dict, verbose=1
    )
    return history

# ── SAVE TRAINING CURVES ──────────────────────────────────────────────────────
def save_curves(history):
    print("\n  Saving training curves...")
    ep   = range(1, len(history.history["accuracy"]) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Model Training History",
                 fontsize=14, fontweight="bold")

    axes[0].plot(ep, history.history["accuracy"],
                 color="#2D6A4F", lw=2, label="Train")
    axes[0].plot(ep, history.history["val_accuracy"],
                 color="#D4A373", lw=2, ls="--", label="Validation")
    axes[0].axhline(0.70, color="#E9C46A", lw=1, ls=":",
                    label="70% target")
    axes[0].set_title("Accuracy", fontweight="bold")
    axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Accuracy")
    axes[0].legend(); axes[0].set_ylim([0,1])
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(ep, history.history["loss"],
                 color="#2D6A4F", lw=2, label="Train")
    axes[1].plot(ep, history.history["val_loss"],
                 color="#D4A373", lw=2, ls="--", label="Validation")
    axes[1].set_title("Loss", fontweight="bold")
    axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Loss")
    axes[1].legend(); axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "training_curves.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print(" Model Training")
    print("  Know your soil. Grow your future.")
    print("=" * 50)

    if not os.path.exists(SPLIT_FILE):
        print("  ERROR: Run prepare_data.py first.")
        exit(1)

    (tp, tl), (vp, vl), (ep_, el) = load_split()

    print("\n  Building TensorFlow datasets...")
    train_ds = make_ds(tp, tl, training=True)
    val_ds   = make_ds(vp, vl)
    test_ds  = make_ds(ep_, el)

    model = build_model()
    model.summary()

    history = train(model, train_ds, val_ds, tl)
    save_curves(history)

    # Save class labels
    lmap = {str(i): c for i, c in enumerate(SOIL_CLASSES)}
    with open(LABELS_PATH, "w") as f:
        json.dump(lmap, f, indent=2)
    print(f"  Saved: {LABELS_PATH}")

    # Quick test
    print("\n  Quick test on test set...")
    loss, acc = model.evaluate(test_ds, verbose=0)
    print(f"  Test accuracy : {acc*100:.2f}%")
    print(f"  Test loss     : {loss:.4f}")
    print(f"  Status        : {'PASS' if acc >= 0.70 else 'BELOW 70% TARGET'}")

    print("\n" + "=" * 50)
    print("  Training complete!")
    print(f"  Model -> {MODEL_PATH}")
    print("  Next step: python evaluate_model.py")
    print("=" * 50)