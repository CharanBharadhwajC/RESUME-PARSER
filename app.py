import os
import uuid
import json
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from fuzzy_logic import calculate_fuzzy_score
from uploads.ann_predictor import predict_ann_score_from_resume

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
SCORES_FILE = 'scores.json'
FUZZY_FILE = 'fuzzy_scores.json'
ANN_FILE = 'ann_scores.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load or create score dictionaries
def load_json(path):
    return json.load(open(path)) if os.path.exists(path) else {}

scores = load_json(SCORES_FILE)
fuzzy_scores = load_json(FUZZY_FILE)
ann_scores = load_json(ANN_FILE)

@app.route('/')
def index():
    return 'Welcome to the Resume Screening System!'

@app.route('/user')
def user_page():
    return render_template('user.html')

@app.route('/hr')
def hr_dashboard():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
            file_id = filename.split('.')[0]
            files.append({
                'id': file_id,
                'filename': filename,
                'score': scores.get(file_id, 'Not yet scored'),
                'suggested_score': fuzzy_scores.get(file_id, '0'),
                'ann_score': ann_scores.get(file_id, '0')
            })
    return render_template('hr.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']
    if file:
        uid = uuid.uuid4().hex[:8]
        filename = secure_filename(uid + os.path.splitext(file.filename)[1])
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Fuzzy logic score
        fuzzy = calculate_fuzzy_score(file_path)
        fuzzy_scores[uid] = fuzzy
        with open(FUZZY_FILE, 'w') as f:
            json.dump(fuzzy_scores, f)

        # ANN score using real features
        ann = predict_ann_score_from_resume(file_path)
        ann_scores[uid] = ann
        with open(ANN_FILE, 'w') as f:
            json.dump(ann_scores, f)

        return jsonify({'uid': uid})
    return 'No file uploaded', 400

@app.route('/download/<uid>')
def download(uid):
    for fname in os.listdir(UPLOAD_FOLDER):
        if fname.startswith(uid):
            return send_from_directory(UPLOAD_FOLDER, fname, as_attachment=True)
    return 'File not found', 404

@app.route('/delete/<uid>', methods=['DELETE'])
def delete(uid):
    deleted = False
    for fname in os.listdir(UPLOAD_FOLDER):
        if fname.startswith(uid):
            os.remove(os.path.join(UPLOAD_FOLDER, fname))
            deleted = True
            break

    for db, path in [(scores, SCORES_FILE), (fuzzy_scores, FUZZY_FILE), (ann_scores, ANN_FILE)]:
        db.pop(uid, None)
        with open(path, 'w') as f:
            json.dump(db, f)

    return ('', 204) if deleted else ('File not found', 404)

@app.route('/getscore/<uid>')
def get_score(uid):
    return jsonify({
        'score': scores.get(uid, 'Not yet scored'),
        'suggested': fuzzy_scores.get(uid, '0'),
        'ann': ann_scores.get(uid, '0')
    })

@app.route('/submitscore/<uid>', methods=['POST'])
def submit_score(uid):
    data = request.get_json()
    score = data.get('score')
    if score is not None:
        scores[uid] = score
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores, f)
        return jsonify({'message': 'Score submitted successfully'})
    return 'Invalid score', 400

if __name__ == '__main__':
    app.run(debug=True)

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[Warning] {path} is empty or corrupted. Resetting.")
            return {}
    return {}
