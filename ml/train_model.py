"""
AI-Based Financial Fraud Detection - Model Training Script
Run this file FIRST to generate the trained model (fraud_model.pkl)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib
import os

# ─────────────────────────────────────────────────────────────
# STEP 1: Generate Improved Synthetic Dataset (REALISTIC)
# ─────────────────────────────────────────────────────────────
np.random.seed(42)
n_samples = 10000

print("📊 Generating improved synthetic dataset...")

fraud_ratio = 0.02
n_fraud = int(n_samples * fraud_ratio)
n_legit = n_samples - n_fraud

# Legit transactions (more variability)
legit = pd.DataFrame({
    "amount": np.random.exponential(300, n_legit),
    "hour_of_day": np.random.randint(0, 24, n_legit),
    "merchant_category": np.random.randint(0, 10, n_legit),
    "transaction_count_24h": np.random.randint(1, 15, n_legit),
    "distance_from_home_km": np.random.exponential(30, n_legit),
    "is_online": np.random.choice([0,1], size=n_legit, p=[0.6,0.4]),
    "is_fraud": 0
})

# Fraud transactions (NOT perfect patterns now)
fraud = pd.DataFrame({
    "amount": np.random.exponential(800, n_fraud),   # overlap with legit
    "hour_of_day": np.random.randint(0, 24, n_fraud),  # no strict rule
    "merchant_category": np.random.randint(0, 10, n_fraud),
    "transaction_count_24h": np.random.randint(5, 40, n_fraud),
    "distance_from_home_km": np.random.exponential(150, n_fraud),
    "is_online": np.random.choice([0,1], size=n_fraud, p=[0.2,0.8]),
    "is_fraud": 1
})

df = pd.concat([legit, fraud], ignore_index=True)

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"✅ Dataset created: {len(df)} rows | Fraud rate: {df['is_fraud'].mean()*100:.2f}%")
# ─────────────────────────────────────────────────────────────
# STEP 2: Feature Engineering
# ─────────────────────────────────────────────────────────────
FEATURES = ["amount", "hour_of_day", "merchant_category",
            "transaction_count_24h", "distance_from_home_km", "is_online"]

X = df[FEATURES]
y = df["is_fraud"]

# ─────────────────────────────────────────────────────────────
# STEP 3: Train/Test Split FIRST
# ─────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ─────────────────────────────────────────────────────────────
# STEP 4: Apply SMOTE ONLY on training data
# ─────────────────────────────────────────────────────────────
print("\n⚖️ Applying SMOTE on training data...")

smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

print(f"✅ Training samples after SMOTE: {len(X_train)}")
# ─────────────────────────────────────────────────────────────
# STEP 5: Scale Features
# ─────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ─────────────────────────────────────────────────────────────
# STEP 6: Train Random Forest Model
# ─────────────────────────────────────────────────────────────
print("\n🤖 Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=8,
    min_samples_split=5,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train_scaled, y_train)

# ─────────────────────────────────────────────────────────────
# STEP 7: Evaluate Model
# ─────────────────────────────────────────────────────────────
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n📈 Model Performance:")
print(f"   Accuracy: {accuracy * 100:.2f}%")
print(f"\n{classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud'])}")
# Confusion Matrix
from sklearn.metrics import ConfusionMatrixDisplay

ConfusionMatrixDisplay.from_predictions(y_test, y_pred)

# Feature Importance
import matplotlib.pyplot as plt

importance = model.feature_importances_

plt.barh(FEATURES, importance)
plt.title("Feature Importance")
plt.show()

# ─────────────────────────────────────────────────────────────
# STEP 8: Save Model + Scaler
# ─────────────────────────────────────────────────────────────
os.makedirs("../backend", exist_ok=True)
joblib.dump(model, "../backend/fraud_model.pkl")
joblib.dump(scaler, "../backend/scaler.pkl")

print("💾 Model saved → backend/fraud_model.pkl")
print("💾 Scaler saved → backend/scaler.pkl")
print("\n✅ Training complete! Now run: cd ../backend && python app.py")
