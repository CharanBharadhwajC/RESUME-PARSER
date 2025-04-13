import re
from models.ann_model import load_ann_model
from uploads.resume_parser import extract_text_from_file
from nlp_utils import extract_keywords_from_text, load_job_description

# Load job description keywords once
job_keywords = extract_keywords_from_text(load_job_description())

def extract_features_from_resume(resume_path):
    """
    Extracts ANN-specific features: [skills_match_count, experience_years, education_level_score]
    """
    text = extract_text_from_file(resume_path).lower()

    # --- Skills Count ---
    matched_keywords = [kw for kw in job_keywords if kw in text]
    skill_match_count = len(matched_keywords)

    # --- Experience Detection ---
    exp_matches = re.findall(r'(\d+)\+?\s*[-]?\s*years?', text)
    experience = max([int(x) for x in exp_matches], default=0)

    # --- Education Scoring ---
    if 'phd' in text or 'doctorate' in text:
        education_score = 3
    elif 'master' in text:
        education_score = 2
    elif 'bachelor' in text:
        education_score = 1
    else:
        education_score = 0

    return [skill_match_count, experience, education_score]

def predict_ann_score_from_resume(resume_path):
    """
    Predicts score (0–10) using ANN model based on extracted features.
    """
    features = extract_features_from_resume(resume_path)
    print(f"[DEBUG] ANN Features: {features}")  # Optional debug

    model = load_ann_model()
    if model is None:
        print("[ERROR] ANN model not loaded. Returning fallback score 0.")
        return 0

    score = model.predict([features])[0]
    
    # Clamp the score between 0 and 10
    clamped_score = max(0, min(10, round(float(score), 2)))
    return clamped_score
