import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Pre-defined categories and their corresponding descriptive keywords
# These act as the "documents" we compare the lawyer's description against.
CATEGORIES = {
    "Civil": "divorce settlement family law child custody dispute mediation personal injury",
    "Criminal": "bail arrest murder theft fraud rape defense prosecutor court jail criminal",
    "Corporate": "business merger acquisition tax company startup contract compliance corporate",
    "Employment": "workplace termination salary discrimination harassment employee employer labor",
    "Property": "real estate land rent eviction landlord tenant lease property boundary deeds"
}

def predict_specialization(description):
    """
    Predicts the lawyer's specialization by computing TF-IDF Cosine Similarity
    between their description and predefined legal category keywords.
    """
    if not description or not description.strip():
        return "Others Lawyer"
        
    categories_keys = list(CATEGORIES.keys())
    categories_docs = list(CATEGORIES.values())
    
    # We add the lawyer's description as the last document
    corpus = categories_docs + [description.lower()]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Calculate cosine similarity of the description against the categories
    # description is the last row, categories are all other rows
    desc_vector = tfidf_matrix[-1]
    cat_vectors = tfidf_matrix[:-1]
    
    similarities = cosine_similarity(desc_vector, cat_vectors).flatten()
    
    # Find the index of the highest similarity score
    best_match_idx = np.argmax(similarities)
    best_score = similarities[best_match_idx]
    
    # If there is very little overlap, default to General Practice
    if best_score < 0.05:
        return "Others Lawyer"
        
    return categories_keys[best_match_idx]

def extract_numerical_data(description):
    """
    Uses Regex to extract experience, juniors count, and cases handled from the description.
    """
    desc_lower = description.lower() if description else ""
    
    # Extract Experience
    exp_match = re.search(r'\b(\d+)\+?\s*(?:years?|yrs?|y/o)\s*(?:of)?\s*(?:[a-z\-]+\s+){0,3}experience\b', desc_lower)
    if not exp_match:
        exp_match = re.search(r'\b(?:experience)(?:[:\-\s]*)(\d+)\+?\s*(?:years?|yrs?)\b', desc_lower)
    experience = int(exp_match.group(1)) if exp_match else 0
    
    # Extract Juniors Count
    juniors_match = re.search(r'\b(\d+)\+?\s*(?:juniors?|junior lawyers?|associates?|assistants?|interns?)\b', desc_lower)
    if not juniors_match:
        juniors_match = re.search(r'\b(?:juniors?|associates?)(?:[:\-\s]*)(\d+)\+?\b', desc_lower)
    juniors_count = int(juniors_match.group(1)) if juniors_match else 0
    
    # Extract Cases Handled
    # Allows up to 3 alphabetical words between the number and the word 'cases' to catch things like "95 family law cases"
    cases_match = re.search(r'\b(\d+)\+?\s+(?:[a-z\-]+\s+){0,3}(?:cases?|lawsuits?|matters?|disputes?|trials?)\b', desc_lower)
    if not cases_match:
        cases_match = re.search(r'\b(?:cases?|lawsuits?|matters?|disputes?|trials?)(?:[:\-\s]*| handled: | won: |: )(\d+)\+?\b', desc_lower)
    
    cases_count = int(cases_match.group(1)) if cases_match else 0
    
    return experience, juniors_count, cases_count

def calculate_ranking_points(experience, juniors_count, cases_count, user_rating=0.0):
    """
    Calculates the Lawyer Ranking Score based on specific point rules.
    Point System:
    Experience: <5 (2.5), 5-10 (5.0), 10-17 (7.5), >17 (10.0)
    Juniors: <5 (2.5), 5-8 (5.0), 8-12 (7.5), >12 (10.0)
    Cases: <20 (2.5), 20-50 (5.0), 50-80 (7.5), >80 (10.0)
    Average = (Exp_Pts + Jun_Pts + Case_Pts + User_Rating) / 4
    """
    # Experience Points
    if experience < 5:
        exp_pts = 2.5
    elif 5 <= experience <= 10:
        exp_pts = 5.0
    elif 10 < experience <= 17:
        exp_pts = 7.5
    else:
        exp_pts = 10.0
        
    # Juniors Count Points
    if juniors_count < 5:
        jun_pts = 2.5
    elif 5 <= juniors_count <= 8:
        jun_pts = 5.0
    elif 8 < juniors_count <= 12:
        jun_pts = 7.5
    else:
        jun_pts = 10.0
        
    # Cases Count Points
    if cases_count < 20:
        case_pts = 2.5
    elif 20 <= cases_count <= 50:
        case_pts = 5.0
    elif 50 < cases_count <= 80:
        case_pts = 7.5
    else:
        case_pts = 10.0
        
    # User Rating is already assumed to be out of 10. If it's out of 5, multiply by 2?
    # Assuming user_rating is out of 10 for consistency.
    # Total Average calculation
    ranking_score = (exp_pts + jun_pts + case_pts + user_rating) / 4.0
    
    return round(ranking_score, 2)

def process_lawyer_profile(description, current_user_rating=0.0):
    """
    Main pipeline function that connects all NLP steps.
    """
    specialization = predict_specialization(description)
    exp, jun, cases = extract_numerical_data(description)
    score = calculate_ranking_points(exp, jun, cases, current_user_rating)
    
    return {
        "specialization": specialization,
        "experience": exp,
        "juniors_count": jun,
        "cases_count": cases,
        "ranking_score": score
    }

if __name__ == "__main__":
    # Test the NLP extraction
    sample_desc = "I am a senior lawyer with 12 years of experience handling divorce and child custody. I currently manage 6 juniors and have successfully handled 60 cases."
    result = process_lawyer_profile(sample_desc, current_user_rating=8.0)
    print("Test Description:", sample_desc)
    print("NLP Output:", result)
