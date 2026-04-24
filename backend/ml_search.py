import os
import pickle
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure NLTK data is available
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub(r'<.*?>', '', text)                 # Remove HTML tags
    text = re.sub(r'[^a-z\s]', '', text)              # Remove punctuation & digits
    text = re.sub(r'\s+', ' ', text).strip()          # Remove extra spaces
    return text

def preprocess_text(text):
    try:
        text = clean_text(text)
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word.isalpha()]
        tokens = [word for word in tokens if word not in stop_words]
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        return " ".join(tokens)
    except Exception as e:
        print(f"Error processing text: {text[:50]}...\n{e}")
        return ""

def load_ml_components():
    """Loads the saved Logistic Regression model and TF-IDF vectorizer."""
    # Since ml_search.py is in backend/, we go up one level to reach the root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(BASE_DIR, "model", "logistic_regression_model.pkl")
    vectorizer_path = os.path.join(BASE_DIR, "processed dataset", "tfidf_vectorizer.pkl")
    
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(vectorizer_path, "rb") as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except Exception as e:
        print(f"Error loading ML components: {e}")
        return None, None

def analyze_client_query(text):
    """
    Takes a client's raw query, preprocesses it, and predicts the legal category.
    Returns the predicted category string.
    """
    model, vectorizer = load_ml_components()
    if not model or not vectorizer:
        return "Others Lawyer"  # Fallback if models are missing
        
    preprocessed_text = preprocess_text(text)
    
    if not preprocessed_text.strip():
        return "Others Lawyer" # Fallback for empty/invalid queries

    # Transform text using the loaded vectorizer
    X_input = vectorizer.transform([preprocessed_text])
    
    # Predict the category
    prediction = model.predict(X_input)[0]
    
    # The models classes_ are ['Civil' 'Corporate' 'Criminal' 'Employment' 'Property']
    # Map them to our database specializations
    category_map = {
        'Civil': 'Civil',
        'Corporate': 'Corporate',
        'Criminal': 'Criminal',
        'Employment': 'Employment',
        'Property': 'Property'
    }
    
    # Map the prediction to our standard naming, or return itself if not found
    predicted_specialization = category_map.get(prediction, prediction)
    
    confidence = max(model.predict_proba(X_input)[0]) * 100
    
    return {
        "specialization": predicted_specialization,
        "confidence": confidence
    }
