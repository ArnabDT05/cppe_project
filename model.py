"""
model.py
--------
Trains a Random Forest classifier to predict telecom call drops.

Features  : signal_strength, time_hour
Target    : call_drop  (1 = dropped, 0 = completed)
Split     : 80% training / 20% testing  (stratified)
Classifier: RandomForestClassifier (scikit-learn)

Output
------
Accuracy score and a detailed classification report printed to console.
"""

import pandas as pd
from sklearn.model_selection  import train_test_split
from sklearn.ensemble         import RandomForestClassifier
from sklearn.metrics          import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ------------------------------------------------------------------
# 1. Load Data
# ------------------------------------------------------------------
DATA_FILE = "telecom_data.csv"

print("=" * 55)
print("  CALL DROP PREDICTION — Random Forest Model")
print("=" * 55)

df = pd.read_csv(DATA_FILE)
print(f"\n✔ Loaded '{DATA_FILE}'  →  {len(df)} rows\n")

# ------------------------------------------------------------------
# 2. Define Features and Target
# ------------------------------------------------------------------
FEATURES = ["signal_strength", "time_hour"]   # input variables
TARGET   = "call_drop"                         # what we are predicting

X = df[FEATURES]   # feature matrix  (1000 × 2)
y = df[TARGET]     # target vector   (1000,)

print(f"  Features : {FEATURES}")
print(f"  Target   : '{TARGET}'")
print(f"  Class distribution → 0 (completed): {(y == 0).sum()}  |  1 (dropped): {(y == 1).sum()}")

# ------------------------------------------------------------------
# 3. Train / Test Split  (80 % train, 20 % test)
# ------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,      # 20 % goes to test set
    random_state=42,     # reproducibility
    stratify=y,          # keep class ratio the same in both splits
)

print(f"\n  Training samples : {len(X_train)}  (80 %)")
print(f"  Testing  samples : {len(X_test)}   (20 %)")

# ------------------------------------------------------------------
# 4. Train RandomForestClassifier
# ------------------------------------------------------------------
print("\n─" * 28)
print("Training RandomForestClassifier …")
print("─" * 28)

model = RandomForestClassifier(
    n_estimators=100,        # number of decision trees in the forest
    max_depth=6,             # limit tree depth to avoid overfitting
    class_weight="balanced", # compensate for any class imbalance
    random_state=42,
    n_jobs=-1,               # use all available CPU cores
)

model.fit(X_train, y_train)  # learn from training data
print("  ✔ Model trained successfully.")

# ------------------------------------------------------------------
# 5. Predict on Test Data
# ------------------------------------------------------------------
y_pred = model.predict(X_test)

# ------------------------------------------------------------------
# 6. Print Accuracy Score
# ------------------------------------------------------------------
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "=" * 55)
print(f"  ★  Model Accuracy : {accuracy * 100:.2f}%")
print("=" * 55)

# ------------------------------------------------------------------
# 7. Detailed Evaluation
# ------------------------------------------------------------------
print("\n── Confusion Matrix ──────────────────────────────────")
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
print(f"""
          Predicted 0   Predicted 1
  Actual 0   {tn:>5}  (TN)   {fp:>5}  (FP)
  Actual 1   {fn:>5}  (FN)   {tp:>5}  (TP)
""")

print("── Classification Report ─────────────────────────────")
print(classification_report(
    y_test, y_pred,
    target_names=["Completed (0)", "Dropped (1)"],
))

# ------------------------------------------------------------------
# 8. Feature Importance
# ------------------------------------------------------------------
print("── Feature Importances ───────────────────────────────")
for feat, imp in zip(FEATURES, model.feature_importances_):
    bar = "█" * int(imp * 50)
    print(f"  {feat:<20} {imp:.4f}  {bar}")

print("\n✔ Done. Model training and evaluation complete.\n")

# ------------------------------------------------------------------
# 9. Real-Time Call Drop Prediction (Sample Input)
# ------------------------------------------------------------------
print("=" * 55)
print("  REAL-TIME CALL DROP PREDICTION — Sample Input")
print("=" * 55)

# Define the sample call to evaluate
sample_signal    = -100   # dBm  (weak signal — below -95 threshold)
sample_time_hour =   18   # 6 PM  (evening peak hour)

# Wrap the sample into a DataFrame so sklearn accepts it
sample_input = pd.DataFrame(
    [[sample_signal, sample_time_hour]],
    columns=FEATURES,          # must match training feature names exactly
)

# Predict class label (0 or 1) and probability for each class
prediction   = model.predict(sample_input)[0]
probability  = model.predict_proba(sample_input)[0]   # [P(0), P(1)]

drop_prob    = probability[1] * 100    # probability of call DROP  (class 1)
complete_prob = probability[0] * 100   # probability of COMPLETED  (class 0)

# ── Print the verdict ─────────────────────────────────────
print(f"""
  Input
  ─────────────────────────────────────
  Signal Strength : {sample_signal} dBm
  Time Hour       : {sample_time_hour}:00

  Prediction
  ─────────────────────────────────────
  Will the call drop?  →  {"⚠️  YES — CALL WILL DROP" if prediction == 1 else "✅  NO — CALL WILL COMPLETE"}

  Confidence
  ─────────────────────────────────────
  Drop probability     : {drop_prob:.1f}%  {"█" * int(drop_prob / 5)}
  Complete probability : {complete_prob:.1f}%  {"█" * int(complete_prob / 5)}
""")

print("=" * 55)

# ------------------------------------------------------------------
# 10. Save Model for API
# ------------------------------------------------------------------
import joblib
joblib.dump(model, "rf_model.pkl")
print("✔ Model saved successfully to 'rf_model.pkl'.")

