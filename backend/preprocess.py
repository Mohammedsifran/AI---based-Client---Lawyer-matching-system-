import pandas as pd
import re 
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import numpy as np

# Try to download NLTK data if not already present
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

def arrangeDataset():
    # File paths based on user requirement
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(BASE_DIR, "raw dataset", "legal_text_classification_with_category.csv")
    output_dir = os.path.join(BASE_DIR, "processed dataset")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading dataset from {input_file}...")
    df = pd.read_csv(input_file)

    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Combine title and text into a single content column for analysis
    if 'case_title' in df.columns and 'case_text' in df.columns:
        df['content'] = df['case_title'].astype(str) + " " + df['case_text'].astype(str)
    elif 'case_text' in df.columns:
        df['content'] = df['case_text'].astype(str)
    else:
        raise Exception("Dataset must contain 'case_title' or 'case_text' columns")
    
    # Map the target label correctly
    if 'case_category' in df.columns:
        df['label'] = df['case_category']
    else:
        raise Exception("Dataset must contain 'case_category' column")
        
    print("Equalizing dataset so all categories have equal count...")
    min_count = df['label'].value_counts().min()
    balanced_chunks = []
    for lbl, group in df.groupby('label'):
        balanced_chunks.append(group.sample(n=min_count, random_state=42))
    df = pd.concat(balanced_chunks, ignore_index=True)
    
    # Shuffle again after group balancing
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("Applying text cleaning and preprocessing... This may take a while.")
    # Apply cleaning
    df['cleaned'] = df['content'].apply(clean_text)

    # Apply preprocessing to tokens
    df['preprocessed'] = df['cleaned'].apply(preprocess_text)
    
    # Remove any empty rows after preprocessing
    df = df[df['preprocessed'].notnull() & (df['preprocessed'].str.strip() != '')]

    print("Vectorizing the text using TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=10000,    # or 5000, 15000 depending on model size constraints
        ngram_range=(1,2),     # include bigrams
        stop_words='english',  # removes common stop words
        sublinear_tf=True      # more emphasis on rare terms
    )

    X = vectorizer.fit_transform(df['preprocessed']) 

    # Save the cleaned data set
    output_csv_path = os.path.join(output_dir, "cleaned_legal_dataset.csv")
    df[['preprocessed', 'label']].to_csv(output_csv_path, index=False)
    print(f"Saved cleaned dataset to: {output_csv_path}")

    # Save the vectorizer in a file
    vectorizer_path = os.path.join(output_dir, 'tfidf_vectorizer.pkl')
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"Saved TF-IDF vectorizer to: {vectorizer_path}")

if __name__ == "__main__":
    arrangeDataset()
