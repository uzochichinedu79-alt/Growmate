"""
GrowMate - prepare_data.py
"Know your soil. Grow your future."

RUN THIS FIRST.
What it does:
  1. Counts your raw soil images
  2. Resizes + normalizes every image (Equation 3.1)
  3. Creates 3 augmented copies of each image
  4. Splits everything 70% train / 15% val / 15% test
  5. Creates the SQLite crop database

HOW TO RUN:
  python prepare_data.py
"""

import os, json, random, sqlite3
import numpy as np
from PIL import Image, ImageEnhance

# ── SETTINGS ──────────────────────────────────────────────────────────────────
RAW_DIR       = "data/raw"
PROCESSED_DIR = "data/processed"
IMAGE_SIZE    = (224, 224)
SOIL_CLASSES  = ["Sandy", "Clay", "Loamy"]
SEED          = 42
random.seed(SEED)
np.random.seed(SEED)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def count_images():
    print("\n  Counting images in data/raw/...")
    print("  " + "-" * 36)
    total = 0
    counts = {}
    for cls in SOIL_CLASSES:
        p = os.path.join(RAW_DIR, cls)
        if not os.path.exists(p):
            print(f"  {cls:<10}: folder missing - please create data/raw/{cls}/")
            counts[cls] = 0
            continue
        imgs = [f for f in os.listdir(p)
                if f.lower().endswith((".jpg",".jpeg",".png",".bmp",".webp"))]
        counts[cls] = len(imgs)
        print(f"  {cls:<10}: {len(imgs)} images")
        total += len(imgs)
    print(f"  {'TOTAL':<10}: {total} images")
    return counts, total

def preprocess_image(path):
    """
    Load image, resize to 224x224, convert RGB.
    Min-max normalization (Equation 3.1):
        xnorm = (x - xmin) / (xmax - xmin)
    Returns (normalized_array, pil_image)
    """
    img = Image.open(path).convert("RGB")
    img = img.resize(IMAGE_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32)
    xmin, xmax = arr.min(), arr.max()
    if xmax - xmin > 0:
        arr = (arr - xmin) / (xmax - xmin)
    else:
        arr = arr / 255.0
    return arr, img

def augment_image(pil_img):
    """
    Returns 3 augmented copies of the image:
      1. Horizontal flip   - simulates different camera angles
      2. Random rotation   - up to +/-20 degrees
      3. Brightness change - simulates outdoor lighting variation
    """
    return [
        pil_img.transpose(Image.FLIP_LEFT_RIGHT),
        pil_img.rotate(random.uniform(-20, 20), expand=False),
        ImageEnhance.Brightness(pil_img).enhance(random.uniform(0.7, 1.4)),
    ]

def process_all():
    print("\n  Processing and augmenting images...")
    print("  " + "-" * 36)
    summary = {}
    for cls in SOIL_CLASSES:
        src = os.path.join(RAW_DIR, cls)
        dst = os.path.join(PROCESSED_DIR, cls)
        os.makedirs(dst, exist_ok=True)
        if not os.path.exists(src):
            continue
        files = [f for f in os.listdir(src)
                 if f.lower().endswith((".jpg",".jpeg",".png",".bmp",".webp"))]
        saved = 0
        for i, fname in enumerate(files):
            try:
                arr, pil_img = preprocess_image(os.path.join(src, fname))
                # save preprocessed original
                out = Image.fromarray((arr * 255).astype(np.uint8))
                out.save(os.path.join(dst, f"{cls.lower()}_{i:04d}_orig.jpg"))
                saved += 1
                # save 3 augmented versions
                for j, aug in enumerate(augment_image(pil_img)):
                    aug.resize(IMAGE_SIZE, Image.LANCZOS)\
                       .save(os.path.join(dst, f"{cls.lower()}_{i:04d}_aug{j}.jpg"))
                    saved += 1
            except Exception as e:
                print(f"  skipped {fname}: {e}")
        summary[cls] = saved
        print(f"  {cls:<10}: {len(files)} originals -> {saved} total (x4 with augmentation)")
    return summary

def split_dataset():
    print("\n  Splitting dataset 70% / 15% / 15%...")
    print("  " + "-" * 36)
    split = {"train": {}, "val": {}, "test": {}}
    for cls in SOIL_CLASSES:
        p = os.path.join(PROCESSED_DIR, cls)
        if not os.path.exists(p):
            continue
        files = [os.path.join(p, f) for f in os.listdir(p) if f.endswith(".jpg")]
        random.shuffle(files)
        n  = len(files)
        n1 = int(n * 0.70)
        n2 = int(n * 0.15)
        split["train"][cls] = files[:n1]
        split["val"][cls]   = files[n1:n1+n2]
        split["test"][cls]  = files[n1+n2:]
        print(f"  {cls:<10}: {len(split['train'][cls])} train | "
              f"{len(split['val'][cls])} val | {len(split['test'][cls])} test")
    with open("data/dataset_split.json","w") as f:
        json.dump(split, f, indent=2)
    print("  Saved -> data/dataset_split.json")

def build_crop_database():
    print("\n  Building crop agronomy database...")
    print("  " + "-" * 36)
    db = "data/growmate_crops.db"
    conn = sqlite3.connect(db)
    cur  = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS crop_agronomy")
    cur.execute("""
        CREATE TABLE crop_agronomy (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name      TEXT NOT NULL,
            local_name     TEXT,
            soil_type      TEXT NOT NULL,
            min_temp       REAL NOT NULL,
            max_temp       REAL NOT NULL,
            min_rainfall   REAL NOT NULL,
            max_rainfall   REAL NOT NULL,
            npk_nitrogen   TEXT NOT NULL,
            npk_phosphorus TEXT NOT NULL,
            npk_potassium  TEXT NOT NULL,
            grow_days      INTEGER,
            description    TEXT
        )
    """)
    # (name, local, soil, minT, maxT, minR, maxR, N, P, K, days, desc)
    crops = [
        ("Cassava","Ege",  "Sandy",22,35,500, 2400,"Low",   "Low",   "Medium",270,
         "Drought-tolerant staple. Great for sandy soils with moderate potassium."),
        ("Cassava","Ege",  "Loamy",22,35,500, 2400,"Medium","Low",   "Medium",240,
         "Excellent yield in loamy soils. Matures faster with good drainage."),
        ("Yam",   "Isu",  "Loamy",25,35,1000,2000,"High",  "Medium","High",  240,
         "High-value crop. Thrives in deep, well-drained loamy soils."),
        ("Yam",   "Isu",  "Clay", 25,35,1000,2000,"Medium","Medium","Medium",270,
         "Can grow in clay but needs good drainage to prevent root rot."),
        ("Maize","Agbado","Loamy",18,32,500, 1200,"High",  "Medium","Medium",90,
         "Fast-growing food crop. Needs nitrogen-rich loamy soils."),
        ("Maize","Agbado","Sandy",18,32,500, 1200,"High",  "Low",   "Low",   100,
         "Can grow in sandy soil but requires extra nitrogen fertiliser."),
        ("Maize","Agbado","Clay", 18,30,600, 1400,"Medium","Medium","Low",   110,
         "Moderate yield in clay. Ensure drainage to avoid waterlogging."),
        ("Cowpea","Ewa",  "Sandy",24,35,400, 1200,"Low",   "Low",   "Low",   75,
         "Excellent for poor sandy soils. Fixes atmospheric nitrogen."),
        ("Cowpea","Ewa",  "Loamy",24,35,400, 1200,"Low",   "Medium","Low",   70,
         "Good yield in loamy soils. Ideal rotation crop after maize."),
        ("Groundnut","Epa","Sandy",22,33,400,1000,"Low",   "Medium","Low",   120,
         "Well-suited to sandy, well-drained soils. Important cash crop."),
        ("Groundnut","Epa","Loamy",22,33,400,1000,"Low",   "High",  "Low",   110,
         "High yield in loamy soils with good phosphorus availability."),
        ("Sorghum","Oka", "Clay", 25,40,300, 1200,"Medium","Low",   "Low",   120,
         "Drought-hardy grain. Thrives in heavy clay soils."),
        ("Sorghum","Oka", "Sandy",25,40,300, 1000,"Low",   "Low",   "Low",   130,
         "Tolerates poor sandy soils with minimal inputs."),
    ]
    cur.executemany("""
        INSERT INTO crop_agronomy
        (crop_name,local_name,soil_type,min_temp,max_temp,min_rainfall,
         max_rainfall,npk_nitrogen,npk_phosphorus,npk_potassium,grow_days,description)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, crops)
    conn.commit()
    conn.close()
    print(f"  Database saved -> {db}")
    print(f"  {len(crops)} crop-soil combinations loaded")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Data Preparation")
    print("  Know your soil. Grow your future.")
    print("=" * 50)

    os.makedirs("data/raw/Sandy", exist_ok=True)
    os.makedirs("data/raw/Clay",  exist_ok=True)
    os.makedirs("data/raw/Loamy", exist_ok=True)
    os.makedirs(PROCESSED_DIR,    exist_ok=True)

    counts, total = count_images()

    if total == 0:
        print("\n  ERROR: No images found.")
        print("  Please add soil images to:")
        print("    data/raw/Sandy/")
        print("    data/raw/Clay/")
        print("    data/raw/Loamy/")
        print("\n  Dataset: https://www.kaggle.com/datasets/prasanshasatpathy/soil-types")
        exit(1)

    process_all()
    split_dataset()
    build_crop_database()

    print("\n" + "=" * 50)
    print("  Data preparation complete!")
    print("  Next step: python train_model.py")
    print("=" * 50)