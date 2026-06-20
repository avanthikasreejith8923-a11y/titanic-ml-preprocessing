# 🚢 Titanic — ML Data Preprocessing Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0-orange)
![pandas](https://img.shields.io/badge/pandas-1.4-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

A leakage-safe data preprocessing pipeline built on the Titanic dataset, using
`scikit-learn`'s `Pipeline` and `ColumnTransformer`. Every statistic used to
clean, encode, or scale the data (median, mode, IQR bounds, mean/std) is
learned **only from the training set**, then applied to the test set —
the test set never influences how the data is processed.

---

## 📌 Pipeline Overview

```
Raw Data (891 rows, 12 columns)
        ↓
Drop identifier/text columns (PassengerId, Name, Ticket, Cabin)
        ↓
Feature Engineering (FamilySize, IsAlone) — row-wise, safe pre-split
        ↓
Train/Test Split (stratified on target, 80/20)
        ↓
Fit ColumnTransformer on TRAIN ONLY:
    - Impute missing Age (median) / Embarked (mode)
    - Clip Fare outliers via IQR (custom transformer)
    - Scale Age, Fare, FamilySize (StandardScaler)
    - One-hot encode Sex, Embarked
        ↓
Transform TRAIN and TEST with the same fitted pipeline
        ↓
Clean, model-ready, leakage-free train/test arrays
```

---

## 🛠️ Why this version is leakage-safe

A common mistake (including in an earlier version of this project) is
computing the median, scaler statistics, or outlier bounds on the **full**
dataset before splitting into train/test. This lets information from the
test set quietly influence preprocessing, which inflates evaluation metrics
later — the model looks better in development than it will ever perform on
truly unseen data.

This version splits **first**, then calls:

```python
preprocessor.fit_transform(X_train)   # learns + applies, train only
preprocessor.transform(X_test)        # applies only, never re-fits
```

so every learned statistic comes exclusively from `X_train`.

---

## 🧩 Custom Transformer: `IQRClipper`

scikit-learn has no built-in "clip outliers by IQR" step, so this project
includes a small custom transformer (`IQRClipper`) that follows the standard
`fit`/`transform` contract, learns its bounds only from the data it's fit on,
and slots directly into a `Pipeline` alongside `SimpleImputer` and
`StandardScaler`.

---

## 📂 Project Structure

```
titanic-ml-preprocessing/
├── src/
│   └── preprocessing.py        # Full pipeline as a Python script
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run

```bash
git clone https://github.com/YOUR_USERNAME/titanic-ml-preprocessing.git
cd titanic-ml-preprocessing
pip install -r requirements.txt
python src/preprocessing.py
```

This will print shape information at each stage and save:
- `X_train_processed.npy`, `X_test_processed.npy`
- `y_train.csv`, `y_test.csv`
- `preprocessor.joblib` — the fitted pipeline, reusable on new incoming data

---

## 🛠️ Tech Stack

- **Python 3.10**
- **pandas** — data loading, cleaning
- **numpy** — IQR calculations
- **scikit-learn** — `Pipeline`, `ColumnTransformer`, `SimpleImputer`,
  `StandardScaler`, `OneHotEncoder`, custom `TransformerMixin`
- **joblib** — persisting the fitted pipeline

---

## 🔭 Next Step

This repo currently covers preprocessing only. The saved
`X_train_processed.npy` / `y_train.csv` files are ready to be fed directly
into a classifier (Logistic Regression, Random Forest, etc.) — that's the
next stage of this project.
