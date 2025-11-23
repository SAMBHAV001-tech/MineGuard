import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Path to save trained model
OUTPUT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "rockfall_model.pkl")

# Path to dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "training_data.csv")

def train_and_save_model():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Features and target
    X = df.drop("risk_label", axis=1)
    y = df["risk_label"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train RandomForest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\n📊 Model Evaluation Report:\n")
    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(model, OUTPUT_MODEL_PATH)
    print(f"✅ Model saved at {OUTPUT_MODEL_PATH}")


if __name__ == "__main__":
    train_and_save_model()
