import textract
import re
from collections import Counter

def extract_text_from_file(file_path):
    try:
        text = textract.process(file_path).decode('utf-8')
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_resume_features(file_path):
    text = extract_text_from_file(file_path).lower()  # Case-insensitive

    # Keywords to match
    keywords = [
        'python', 'machine learning', 'deep learning', 'flask',
        'django', 'nlp', 'git', 'sql', 'cloud', 'api'
    ]
    
    # Count word frequency
    word_list = re.findall(r'\w+', text)  # Extract words only (ignores punctuation)
    word_freq = Counter(word_list)

    # Weighted skill match based on keyword frequency
    total_weight = sum(word_freq[key] for key in keywords if key in word_freq)
    max_possible_weight = len(keywords) * 5  # Assume max 5 points per keyword
    skills_match = min((total_weight / max_possible_weight) * 10, 10)

    # Extract years of experience
    exp_matches = re.findall(r'(\d+)\+?\s*(?:year|years)', text)
    experience_years = max([int(x) for x in exp_matches], default=0)
    experience_score = min(experience_years, 10)

    # Education scoring
    education_level = 3  # Default level
    if 'phd' in text:
        education_level = 10
    elif 'master' in text:
        education_level = 7
    elif 'bachelor' in text or 'bsc' in text:
        education_level = 5

    return {
        'skills_match': round(skills_match, 2),
        'experience_years': experience_score,
        'education_level': education_level
    }
