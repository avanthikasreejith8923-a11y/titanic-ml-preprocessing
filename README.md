# 🚢 Titanic — ML Data Preprocessing Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0-orange)
![pandas](https://img.shields.io/badge/pandas-1.4-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

A hands-on project applying core data preprocessing techniques to the
Titanic dataset using `pandas` and `scikit-learn`. 

---

## 📌 Pipeline Overview

```
Raw Data (891 rows, 12 columns)
        │
        ▼
Drop identifier / free-text columns
   (PassengerId, Name, Ticket, Cabin)
        │
        ▼
Feature Engineering
   FamilySize = SibSp + Parch + 1
   IsAlone    = 1 if FamilySize == 1
        │
        ▼
Train / Test Split  (80 / 20, stratified on Survived)
        │
        ▼
ColumnTransformer fit on TRAIN ONLY
   ├── Numeric (Age, Fare, FamilySize)
   │      Impute missing → median
   │      Clip outliers   → IQR rule (custom transformer)
   │      Scale           → StandardScaler
   │
   └── Categorical (Sex, Embarked)
          Impute missing → most frequent
          Encode          → OneHotEncoder
        │
        ▼
Clean, model-ready train/test arrays
```

---

## 🛠️ Key Decisions

| Step | Problem | Decision | Reasoning |
|---|---|---|---|
| Missing `Age` (177 rows) | Numeric, skewed | Median imputation | Robust to outliers, unlike mean |
| Missing `Cabin` (687/891) | 77% empty | Dropped column | No imputation recovers a column this sparse |
| Missing `Embarked` (2 rows) | Categorical | Mode imputation | Fills with the most common port |
| `Fare` outliers (up to £512 vs. avg £32) | Skews scaling | IQR clipping, before scaling | Outliers distort `StandardScaler`'s mean/std |
| `Sex`, `Embarked` | Text categories | `OneHotEncoder(drop="first")` | No natural ordering; avoids dummy-variable trap |
| `SibSp`, `Parch` | Less meaningful alone | Combined into `FamilySize`, `IsAlone` | Captures the same signal more directly |
| Train/test split | Class imbalance risk | `stratify=Survived` | Keeps survival ratio consistent across both sets |

**On data leakage:** all statistics used for imputing, scaling, and
clipping (median, mean/std, IQR bounds) are learned only from the training
set via `fit_transform(X_train)`, then applied to the test set via
`transform(X_test)` — the test set never influences how the data is
processed.

---

## 🧩 Custom Transformer

scikit-learn doesn't ship a built-in "clip outliers by IQR" step, so this
project includes a small custom `IQRClipper` transformer that follows the
same `fit` / `transform` contract as `StandardScaler` and `SimpleImputer`,
so it works inside the same `Pipeline`.

---

## 📊 Before → After

| Metric | Raw Data | After Preprocessing |
|---|---|---|
| Rows | 891 | 891 |
| Columns | 12 | 8 |
| Missing values | 866 | 0 |
| Text/categorical columns | 5 | 0 |
| Fare outliers | 116 | 0 (clipped, not removed) |

---

## 📂 Project Structure

```
titanic-ml-preprocessing/
├── src/
│   └── preprocessing.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ▶️ How to Run

```bash
git clone https://github.com/avanthikasreejith8923-a11y/titanic-ml-preprocessing.git
cd titanic-ml-preprocessing
pip install -r requirements.txt
python src/preprocessing.py
```

**Output:**
```
Raw shape: (891, 12)
Shape after feature engineering: (891, 8)
Train shape: (712, 7) Test shape: (179, 7)
Processed train shape: (712, 8)
Processed test shape: (179, 8)
```

---

## 🛠️ Tech Stack

- **Python 3.10**
- **pandas** — data loading and cleaning
- **numpy** — IQR calculations
- **scikit-learn** — `Pipeline`, `ColumnTransformer`, `SimpleImputer`,
  `StandardScaler`, `OneHotEncoder`, `train_test_split`
- **joblib** — saving the fitted pipeline
