import os
import uuid
import json
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for, Response
from werkzeug.utils import secure_filename
from fuzzy_logic import calculate_fuzzy_score
from uploads.ann_predictor import predict_ann_score_from_resume

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
SCORES_FILE = 'scores.json'
FUZZY_FILE = 'fuzzy_scores.json'
ANN_FILE = 'ann_scores.json'

HR_PASSCODE = "hr"
ADMIN_PASSCODE = "admin"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

scores = load_json(SCORES_FILE)
fuzzy_scores = load_json(FUZZY_FILE)
ann_scores = load_json(ANN_FILE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user')
def user_page():
    return render_template('user.html')

@app.route('/hr', methods=['GET', 'POST'])
def hr_dashboard():
    if request.method == 'POST':
        return redirect(url_for('hr_dashboard'))

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

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']
    if file:
        uid = uuid.uuid4().hex[:8]
        filename = secure_filename(uid + os.path.splitext(file.filename)[1])
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        fuzzy = calculate_fuzzy_score(file_path)
        fuzzy_scores[uid] = fuzzy
        with open(FUZZY_FILE, 'w') as f:
            json.dump(fuzzy_scores, f)

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
    if uid in scores:
        return jsonify({'error': 'Resume already scored. Cannot delete.'}), 403

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
    if uid not in fuzzy_scores and uid not in ann_scores and uid not in scores:
        return jsonify({'error': 'Invalid user ID'}), 404
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

@app.route('/export-csv')
def export_csv():
    try:
        with open(SCORES_FILE, 'r') as f:
            scores_data = json.load(f)
    except FileNotFoundError:
        return "No scores found!", 404

    def generate():
        data = [['User ID', 'Manual Score', 'Fuzzy Score', 'ANN Score']]
        for user_id in scores_data:
            data.append([
                user_id,
                scores_data.get(user_id, 'N/A'),
                fuzzy_scores.get(user_id, '0'),
                ann_scores.get(user_id, '0')
            ])
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv', headers={
        "Content-Disposition": "attachment; filename=resume_scores.csv"
    })

@app.route('/hr-login', methods=['GET', 'POST'])
def hr_login():
    if request.method == 'POST':
        passcode = request.form.get('passcode')
        if passcode == HR_PASSCODE:
            return redirect(url_for('hr_dashboard'))
        else:
            return render_template('hr_login.html', error="Incorrect HR passcode!")
    return render_template('hr_login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        passcode = request.form.get('passcode')
        if passcode == ADMIN_PASSCODE:
            return redirect(url_for('admin_page'))
        else:
            return render_template('admin_login.html', error="Incorrect Admin passcode!")
    return render_template('admin_login.html')

if __name__ == '__main__':
    app.run(debug=True)
