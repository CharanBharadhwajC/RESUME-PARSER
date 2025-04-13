import os
import pickle

def load_ann_model():
    model_path = 'models/ann_model.pkl'
    if not os.path.exists(model_path) or os.path.getsize(model_path) == 0:
        print("[ERROR] ANN model file missing or empty.")
        return None  # or raise an error, or return a mock object
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model
