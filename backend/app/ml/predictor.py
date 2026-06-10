import os
import warnings
# Ignore unpickling/scikit-learn warning due to compiler version mismatch
warnings.filterwarnings("ignore", category=UserWarning)
import joblib
import numpy as np

# Load assets dynamically based on file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
WEIGHTS_PATH = os.path.join(BASE_DIR, "model_weights.npz")

try:
    scaler = joblib.load(SCALER_PATH)
    weights = np.load(WEIGHTS_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load ML assets: {e}")

# Extract NumPy weights
W1 = weights['w1']
B1 = weights['b1']
BN1_BETA = weights['bn1_beta']
BN1_GAMMA = weights['bn1_gamma']
BN1_MEAN = weights['bn1_mean']
BN1_VAR = weights['bn1_var']

W2 = weights['w2']
B2 = weights['b2']
BN2_BETA = weights['bn2_beta']
BN2_GAMMA = weights['bn2_gamma']
BN2_MEAN = weights['bn2_mean']
BN2_VAR = weights['bn2_var']

W3 = weights['w3']
B3 = weights['b3']

def batch_norm(x, mean, var, gamma, beta, epsilon=1e-3):
    """NumPy implementation of Keras BatchNormalization layer forward pass."""
    return (x - mean) / np.sqrt(var + epsilon) * gamma + beta

def extract_features(username: str, fullname: str, bio_input: str, has_url: bool, is_private: bool, has_pic: bool, posts: int, followers: int, follows: int) -> np.ndarray:
    """Converts user input features to the exact 11 features expected by the model."""
    
    # 1. profile_picture presence
    input_has_pic = 1 if has_pic else 0
    
    # 2. nums/length_username ratio
    user_len = len(username)
    user_nums = sum(c.isdigit() for c in username)
    input_username_ratio = user_nums / user_len if user_len > 0 else 0
    
    # 3. fullname words
    input_fullname_words = len(fullname.strip().split()) if fullname else 0
    
    # 4. nums/length_fullname ratio
    full_len = len(fullname)
    full_nums = sum(c.isdigit() for c in fullname)
    input_fullname_ratio = full_nums / full_len if full_len > 0 else 0
    
    # 5. name==username (0 or 1) binary class
    input_name_equals_user = 1 if username.lower() == fullname.lower() else 0
    
    # 6. description length or bio length
    # Parse bio_input like in the original app: digits = length, text = len(text)
    bio_clean = bio_input.strip()
    if bio_clean.isdigit():
        input_desc_len = int(bio_clean)
    else:
        input_desc_len = len(bio_clean)
    
    # 7. external URL (0 or 1) binary class
    input_has_url = 1 if has_url else 0
    
    # 8. private (0 or 1) binary class
    input_is_private = 1 if is_private else 0
    
    # 9, 10, 11. numerical counts
    input_num_posts = int(posts)
    input_num_followers = int(followers)
    input_num_follows = int(follows)
    
    features = np.array([
        input_has_pic, 
        input_username_ratio, 
        input_fullname_words, 
        input_fullname_ratio,
        input_name_equals_user, 
        input_desc_len, 
        input_has_url, 
        input_is_private, 
        input_num_posts, 
        input_num_followers, 
        input_num_follows
    ])
    
    return features.reshape(1, -1)

def run_prediction(features_mat: np.ndarray) -> tuple[bool, float]:
    """Runs standard scaling and the neural network forward propagation in NumPy."""
    # Step 1: Scale features
    scaled_features = scaler.transform(features_mat)
    
    # Step 2: Layer 1 (Dense -> BatchNorm -> Relu)
    z1 = np.dot(scaled_features, W1) + B1
    bn1 = batch_norm(z1, BN1_MEAN, BN1_VAR, BN1_GAMMA, BN1_BETA)
    a1 = np.maximum(0, bn1)  # ReLU
    
    # Step 3: Layer 2 (Dense -> BatchNorm -> Relu)
    z2 = np.dot(a1, W2) + B2
    bn2 = batch_norm(z2, BN2_MEAN, BN2_VAR, BN2_GAMMA, BN2_BETA)
    a2 = np.maximum(0, bn2)  # ReLU
    
    # Step 4: Output Layer (Dense -> Sigmoid)
    z3 = np.dot(a2, W3) + B3
    prob = 1.0 / (1.0 + np.exp(-z3))  # Sigmoid activation
    
    prob_val = float(prob[0][0])
    is_fake = prob_val > 0.5
    
    return is_fake, prob_val
