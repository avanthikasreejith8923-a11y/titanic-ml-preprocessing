"""
Titanic ML Data Preprocessing Pipeline
----------------------------------------
A leakage-safe preprocessing pipeline: split happens BEFORE any statistic
(median, mean, std, IQR bounds, mode) is calculated, so the test set never
influences how the data is cleaned, encoded, or scaled.
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ---------------------------------------------------------------------------
# Custom transformer: clip outliers using the IQR rule.
# sklearn has no built-in "clip by IQR" step, so we write one that follows
# the same fit/transform contract as every other sklearn transformer.
# Bounds are learned only from whatever data is passed to .fit() (train set).
# ---------------------------------------------------------------------------
class IQRClipper(BaseEstimator, TransformerMixin):
    def __init__(self, factor=1.5):
        self.factor = factor

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        q1 = np.percentile(X, 25, axis=0)
        q3 = np.percentile(X, 75, axis=0)
        iqr = q3 - q1
        self.lower_ = q1 - self.factor * iqr
        self.upper_ = q3 + self.factor * iqr
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        return np.clip(X, self.lower_, self.upper_)


def load_data(url="https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"):
    return pd.read_csv(url)


def engineer_features(df):
    """Row-wise operations only — safe to run before the train/test split
    because nothing here depends on a column-wide statistic."""
    df = df.drop(columns=["PassengerId", "Name", "Ticket", "Cabin"])
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)
    df = df.drop(columns=["SibSp", "Parch"])
    return df


def build_preprocessor():
    numeric_features = ["Age", "Fare", "FamilySize"]
    categorical_features = ["Sex", "Embarked"]

    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("outlier_clip", IQRClipper(factor=1.5)),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(drop="first", handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_pipeline, numeric_features),
        ("cat", categorical_pipeline, categorical_features),
    ], remainder="passthrough")  # Pclass, IsAlone pass through unchanged

    return preprocessor


def main():
    df = load_data()
    print("Raw shape:", df.shape)

    df = engineer_features(df)
    print("Shape after feature engineering:", df.shape)

    X = df.drop(columns=["Survived"])
    y = df["Survived"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("Train shape:", X_train.shape, "Test shape:", X_test.shape)

    preprocessor = build_preprocessor()

    # Fit on TRAIN ONLY. All medians, means, stds, IQR bounds, and modes
    # are learned exclusively from X_train.
    X_train_processed = preprocessor.fit_transform(X_train)
    # Test data is only ever transformed, never used to fit anything.
    X_test_processed = preprocessor.transform(X_test)

    print("Processed train shape:", X_train_processed.shape)
    print("Processed test shape:", X_test_processed.shape)

    # Save processed arrays for the next stage (model training)
    np.save("X_train_processed.npy", X_train_processed)
    np.save("X_test_processed.npy", X_test_processed)
    y_train.to_csv("y_train.csv", index=False)
    y_test.to_csv("y_test.csv", index=False)

    # Save the fitted pipeline itself — this lets you preprocess brand-new
    # incoming data later using the exact same fitted statistics, without
    # retraining the preprocessor.
    joblib.dump(preprocessor, "preprocessor.joblib")

    print("\nSaved: X_train_processed.npy, X_test_processed.npy, "
          "y_train.csv, y_test.csv, preprocessor.joblib")


if __name__ == "__main__":
    main()
