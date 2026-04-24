import ml_search
from models.user_model import search_lawyers

def search_for_lawyer(query_text, filter_gender, filter_district):
    predicted_specialization = None
    confidence = None
    lawyers = []
    
    if query_text:
        # Predict uses ML search script
        result = ml_search.analyze_client_query(query_text)
        predicted_specialization = result['specialization']
        confidence = result['confidence']
        
        # Query Database
        lawyers = search_lawyers(predicted_specialization, filter_gender, filter_district)
        
    return {
        'predicted_specialization': predicted_specialization,
        'confidence': confidence,
        'lawyers': lawyers
    }
