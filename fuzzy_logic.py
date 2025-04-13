import json
from fuzzy_priority import compute_fuzzy_priority
from uploads.resume_parser import extract_resume_features

def load_weights():
    try:
        with open("score_weights.json") as f:
            return json.load(f)
    except:
        return {"skills_weight": 0.33, "experience_weight": 0.33, "education_weight": 0.34}  # fallback

def calculate_fuzzy_score(resume_path):
    features = extract_resume_features(resume_path)
    weights = load_weights()

    skills = features.get('skills_match', 5)
    experience = features.get('experience_years', 5)
    education = features.get('education_level', 5)

    # Weighted average
    score = (
        skills * weights["skills_weight"] +
        experience * weights["experience_weight"] +
        education * weights["education_weight"]
    )

    return round(score, 2)
