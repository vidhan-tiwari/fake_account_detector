import os
import joblib
import numpy as np

# Load assets for NumPy predictor
import app.ml.predictor as predictor

# Try loading TensorFlow/Keras to compare
try:
    from tensorflow.keras.models import load_model
    has_tf = True
except ImportError:
    has_tf = False
    print("TensorFlow not installed. Running NumPy predictions only.")

# Test data points from the Jupyter notebook
all_records = {
    "Person 1": np.array([1, 0.25,  7, 0, 0, 19, 0, 1, 0, 277, 220]), # Real
    "Person 2": np.array([1, 0.17, 22, 0, 0, 37, 0, 1, 7, 343, 308]), # Real
    "Person 3": np.array([1, 0.16, 13, 0, 0, 0,  0, 1, 0, 302, 736]), # Real
    "Person 4": np.array([1, 0.11, 17, 0, 0, 0,  0, 1, 0, 127, 247]), # Real
    "Random 1": np.array([0, 0.05,  6, 0.15, 0, 32, 1, 0, 126, 6000, 7500]) # Fake/Suspicious
}

# Run NumPy Predictions
print("-" * 60)
print(f"{'Test Case':<12} | {'NumPy Prob':<12} | {'Classification'}")
print("-" * 60)
numpy_results = {}
for name, features in all_records.items():
    features_mat = features.reshape(1, -1)
    is_fake, prob = predictor.run_prediction(features_mat)
    numpy_results[name] = prob
    classification = "FAKE" if is_fake else "REAL"
    print(f"{name:<12} | {prob:.8f}   | {classification}")
print("-" * 60)

if has_tf:
    print("\nLoading TensorFlow model to run validation comparison...")
    h5_path = "../instagram_fake_detector_ANN (1).h5"
    if not os.path.exists(h5_path):
        h5_path = "instagram_fake_detector_ANN (1).h5"
        
    keras_model = load_model(h5_path)
    scaler = joblib.load("app/ml/scaler.pkl")
    
    print("-" * 75)
    print(f"{'Test Case':<12} | {'NumPy Prob':<12} | {'Keras Prob':<12} | {'Abs Difference'}")
    print("-" * 75)
    
    mismatches = 0
    for name, features in all_records.items():
        features_mat = features.reshape(1, -1)
        scaled_features = scaler.transform(features_mat)
        
        keras_prob = float(keras_model.predict(scaled_features, verbose=0)[0][0])
        numpy_prob = numpy_results[name]
        diff = abs(keras_prob - numpy_prob)
        
        print(f"{name:<12} | {numpy_prob:.8f}   | {keras_prob:.8f}   | {diff:.8e}")
        
        # Check if the difference is within a reasonable tolerance (e.g. 1e-5)
        if diff > 1e-5:
            mismatches += 1
            
    print("-" * 75)
    if mismatches == 0:
        print(" SUCCESS: NumPy predictions match TensorFlow predictions exactly!")
    else:
        print(f" WARNING: Detected {mismatches} mismatches between NumPy and TensorFlow.")
else:
    print("\nTo validate against Keras, please install tensorflow in this environment.")
