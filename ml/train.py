import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

# 1. Setup Absolute Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cleaned_data_path = os.path.join(BASE_DIR, "dataset", "cleaned_dataset.csv")
model_output_path = os.path.join(BASE_DIR, "ml", "saved_model.pkl")

# 2. Load Cleaned Dataset
df = pd.read_csv(cleaned_data_path)

# 3. Define Features (X) and Target (y)
X = df.drop(columns=['irrigation_needed'])
y = df['irrigation_needed']

# 4. Stratified Train-Test Split (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Define Candidate Models (Random Forest listed first for tie-breaking preference)
models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5)
}

best_model = None
best_f1 = -1.0
best_model_name = ""

print("\n================ MODEL EVALUATION & COMPARISON ================\n")

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    cm = confusion_matrix(y_test, preds)
    
    print(f"--- {name} ---")
    print(f"Accuracy : {acc * 100:.2f}%")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("-" * 45 + "\n")
    
    # Select best model (Random Forest wins ties due to ordering)
    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_model_name = name

print(f"Selected Champion Model: {best_model_name} (F1-Score: {best_f1:.4f})")

# 6. Save Trained Artifact
joblib.dump(best_model, model_output_path)
print(f"Model saved successfully as: {model_output_path}")