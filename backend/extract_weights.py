import h5py
import numpy as np

h5_path = "instagram_fake_detector_ANN (1).h5"
out_path = "backend/model_weights.npz"

print(f"Extracting weights from {h5_path}...")
with h5py.File(h5_path, 'r') as f:
    # Layer 1 Dense
    w1 = f['model_weights/dense/sequential/dense/kernel'][:]
    b1 = f['model_weights/dense/sequential/dense/bias'][:]
    
    # Layer 1 BatchNorm
    bn1_beta = f['model_weights/batch_normalization/sequential/batch_normalization/beta'][:]
    bn1_gamma = f['model_weights/batch_normalization/sequential/batch_normalization/gamma'][:]
    bn1_mean = f['model_weights/batch_normalization/sequential/batch_normalization/moving_mean'][:]
    bn1_var = f['model_weights/batch_normalization/sequential/batch_normalization/moving_variance'][:]
    
    # Layer 2 Dense
    w2 = f['model_weights/dense_1/sequential/dense_1/kernel'][:]
    b2 = f['model_weights/dense_1/sequential/dense_1/bias'][:]
    
    # Layer 2 BatchNorm
    bn2_beta = f['model_weights/batch_normalization_1/sequential/batch_normalization_1/beta'][:]
    bn2_gamma = f['model_weights/batch_normalization_1/sequential/batch_normalization_1/gamma'][:]
    bn2_mean = f['model_weights/batch_normalization_1/sequential/batch_normalization_1/moving_mean'][:]
    bn2_var = f['model_weights/batch_normalization_1/sequential/batch_normalization_1/moving_variance'][:]
    
    # Output Dense
    w3 = f['model_weights/dense_2/sequential/dense_2/kernel'][:]
    b3 = f['model_weights/dense_2/sequential/dense_2/bias'][:]

# Save to npz file
np.savez(
    out_path,
    w1=w1, b1=b1,
    bn1_beta=bn1_beta, bn1_gamma=bn1_gamma, bn1_mean=bn1_mean, bn1_var=bn1_var,
    w2=w2, b2=b2,
    bn2_beta=bn2_beta, bn2_gamma=bn2_gamma, bn2_mean=bn2_mean, bn2_var=bn2_var,
    w3=w3, b3=b3
)

print(f"Successfully saved weights to {out_path}!")

# Verify loading works
data = np.load(out_path)
print("Keys in saved npz:", list(data.keys()))
for key in data.keys():
    print(f"  {key}: shape {data[key].shape}")
