import os
import json
import pickle
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from uploads.resume_parser import extract_resume_features

UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'data.json'
SCORES_FILE = 'scores.json'
MODEL_PATH = 'models/ann_model.pkl'

def load_training_data():
    if not os.path.exists(SCORES_FILE) or not os.path.exists(DATA_FILE):
        return [], []

    with open(SCORES_FILE, 'r') as f:
        scores = json.load(f)

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    X, y = [], []

    for uid, score in scores.items():
        if not isinstance(score, (int, float)):
            continue  # skip null or non-numeric HR scores

        info = data.get(uid, {})
        if isinstance(info, dict):
            filename = info.get('filename', f"{uid}.txt")
        elif isinstance(info, str):
            filename = info
        else:
            continue

        ext = filename.split('.')[-1]
        resume_path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.exists(resume_path):
            features = extract_resume_features(resume_path)
            if features:
                X.append([
                    features['skills_match'],
                    features['experience_years'],
                    features['education_level']
                ])
                y.append(score)

    return X, y

def train_ann_model():
    X, y = load_training_data()
    if not X or not y:
        print("No training data available.")
        return

    # Handle case when only one sample exists
    if len(X) < 2:
        X_train, y_train = X, y
        X_test, y_test = X, y
        print("Not enough samples to split — training on all data.")
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = MLPRegressor(hidden_layer_sizes=(8, 8), max_iter=1000, random_state=1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model trained. Validation MSE: {mse:.2f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == '__main__':
    train_ann_model()
