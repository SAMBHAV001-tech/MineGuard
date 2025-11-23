import numpy as np
import joblib
import os
import traceback

# Path to trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "rockfall_model.pkl")

# Try loading the model
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Loaded model from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Failed to load model. Please train using train_model.py.\nError: {e}")
    model = None


def predict(features: dict):
    """
    Predicts rockfall risk from given features.
    Required keys:
      rainfall, temperature, slope, wind_speed, displacement_rate, vibration
    """

    # --- Check model ---
    if model is None:
        raise RuntimeError("Model not loaded. Please train first using train_model.py")

    # --- Check feature completeness ---
    required_keys = [
        "rainfall",
        "temperature",
        "slope",
        "wind_speed",
        "displacement_rate",
        "vibration",
    ]

    missing = [key for key in required_keys if key not in features]
    if missing:
        raise ValueError(f"Missing input features: {', '.join(missing)}")

    try:
        # --- Convert to numeric safely ---
        input_vec = np.array([[
            float(features["rainfall"]),
            float(features["temperature"]),
            float(features["slope"]),
            float(features["wind_speed"]),
            float(features["displacement_rate"]),
            float(features["vibration"]),
        ]])

        # --- Predict ---
        prob = float(model.predict_proba(input_vec)[0][1])
        label = int(prob > 0.5)

        # --- Return structured response ---
        result = {
            "risk": "high" if prob > 0.7 else ("medium" if prob > 0.4 else "low"),
            "probability": round(prob, 3),
            "rockfall_predicted": label
        }

        print("✅ Prediction computed successfully:", result)
        return result

    except Exception as e:
        print("❌ Error during prediction:")
        traceback.print_exc()
        raise RuntimeError(f"Prediction failed due to invalid input or model error: {e}")


# Manual test (only runs when executed directly)
if __name__ == "__main__":
    sample_features = {
        "rainfall": 35,
        "temperature": 24,
        "slope": 38,
        "wind_speed": 6,
        "displacement_rate": 0.09,
        "vibration": 2.1,
    }

    try:
        result = predict(sample_features)
        print("🔮 Prediction result:", result)
    except Exception as e:
        print(f"⚠️ Test failed: {e}")
