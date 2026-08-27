"""
GrowMate - run.py
"Know your soil. Grow your future."

Single launch script. Checks everything is ready then starts the app.

HOW TO RUN:
  python run.py
"""

import os
import sys
import subprocess

# Always work relative to where THIS file lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

print("=" * 50)
print("  Launch Script")
print("  Know your soil. Grow your future.")
print("=" * 50)
print(f"  Working directory: {BASE_DIR}")
print()

# ── CHECKS ────────────────────────────────────────────────────────────────────
all_ok = True

# Model check (not fatal — demo mode handles it)
model_path = os.path.join(BASE_DIR, "models", "growmate_model.h5")
if os.path.exists(model_path):
    print("  [OK] Trained model found")
else:
    print("  [!!] Model not found - app will run in DEMO MODE")
    print("       To train the real model: python train_model.py")

# Database check (fatal)
db_path = os.path.join(BASE_DIR, "data", "growmate_crops.db")
if os.path.exists(db_path):
    print("  [OK] Crop database found")
else:
    print("  [!!] Crop database missing - run prepare_data.py first")
    all_ok = False

# App files check
required_files = [
    "app/Home.py",
    "app/utils.py",
    "app/pages/1_Soil_Analysis.py",
    "app/pages/2_Crop_Recommendation.py",
    "app/pages/3_Cultivation_Calendar.py",
    "app/pages/4_About.py",
]

for rel_path in required_files:
    full_path = os.path.join(BASE_DIR, rel_path)
    if os.path.exists(full_path):
        print(f"  [OK] {rel_path}")
    else:
        print(f"  [!!] Missing: {rel_path}")
        all_ok = False

# ── LAUNCH ────────────────────────────────────────────────────────────────────
if not all_ok:
    print()
    print("  Some required files are missing.")
    print("  Fix the issues above then run: python run.py")
    sys.exit(1)

print()
print("  All checks passed. Launching GrowMate...")
print("  Your browser will open at: http://localhost:8501")
print("  Press Ctrl+C in this terminal to stop the app.")
print("=" * 50)

home_py = os.path.join(BASE_DIR, "app", "Home.py")

# Launch Streamlit app
subprocess.run([sys.executable, "-m", "streamlit", "run", home_py])