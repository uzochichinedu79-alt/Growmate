# 🌱 GrowMate
### *Know your soil. Grow your future.*

AI-powered soil analysis and smart cultivation planning for smallholder
farmers in West Africa. Final Year Project — Landmark University, Omu-Aran.

---

## What GrowMate does

Upload a soil photo → get instant soil texture classification, NPK
nutrient estimates, ranked crop recommendations based on live weather,
and a 12-week cultivation calendar you can export as PDF or CSV.

---

## Project structure

```
GrowMate/
├── prepare_data.py          # Step 1: process images + build crop DB
├── train_model.py           # Step 2: train CNN model
├── evaluate_model.py        # Step 3: generate report figures
├── dataset_figures.py       # Step 3b: dataset analysis figures
├── run.py                   # Launch script (recommended)
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── config.toml          # GrowMate green theme
│
├── data/
│   ├── raw/Sandy/           ← put your Sandy images here
│   ├── raw/Clay/            ← put your Clay images here
│   ├── raw/Loamy/           ← put your Loamy images here
│   ├── processed/           (auto-generated)
│   ├── dataset_split.json   (auto-generated)
│   └── growmate_crops.db    (auto-generated)
│
├── models/
│   ├── growmate_model.h5    (auto-generated after training)
│   └── class_labels.json   (auto-generated after training)
│
├── results/                 (all report figures saved here)
│
└── app/
    ├── Home.py
    ├── utils.py             # shared CSS + helpers
    └── pages/
        ├── 1_Soil_Analysis.py
        ├── 2_Crop_Recommendation.py
        ├── 3_Cultivation_Calendar.py
        └── 4_About.py
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get soil dataset
https://www.kaggle.com/datasets/prasanshasatpathy/soil-types

Put images into:
- `data/raw/Sandy/`
- `data/raw/Clay/`
- `data/raw/Loamy/`

Aim for 100-125 images per class.

### 3. Get weather API key (free)
https://openweathermap.org/api

Open `app/pages/2_Crop_Recommendation.py` and replace:
```python
WEATHER_KEY = "YOUR_API_KEY_HERE"
```

---

## Run order

```bash
python prepare_data.py      # process images, build DB
python train_model.py       # train model (15-40 mins)
python evaluate_model.py    # generate report figures
python dataset_figures.py   # generate dataset figures
python run.py               # launch app
```

App opens at: http://localhost:8501

---

## Performance targets

| Metric    | Target |
|-----------|--------|
| Accuracy  | >= 70% |
| Precision | >= 65% |
| Recall    | >= 65% |
| F1-Score  | >= 65% |

---

## Crop scoring formula (Equation 3.4)

```
S = 0.40 * Cs + 0.30 * Ct + 0.30 * Cr
```
Cs = soil compatibility, Ct = temperature suitability, Cr = rainfall suitability

---

*GrowMate v1.0 | Landmark University | "Know your soil. Grow your future."*