from models.user_model import (
    get_lawyer_by_id, update_lawyer_profile_full, get_lawyer_user_rating, 
    get_client_by_id, update_client_profile
)
from models.appointment_model import (
    save_lawyer_for_client, remove_saved_lawyer, get_saved_lawyers_for_client
)
import lawyer_nlp

def get_lawyer_profile(lawyer_id):
    return get_lawyer_by_id(lawyer_id)

def update_lawyer_profile_service(lawyer_id, description, gender, district, filename=None):
    # Get current rating
    current_rating = get_lawyer_user_rating(lawyer_id)
    
    # Run NLP Pipeline
    nlp_data = lawyer_nlp.process_lawyer_profile(description, current_user_rating=current_rating)
    
    # Update DB
    success = update_lawyer_profile_full(
        lawyer_id, description, nlp_data['specialization'], 
        nlp_data['experience'], nlp_data['juniors_count'], 
        nlp_data['cases_count'], nlp_data['ranking_score'], 
        filename, gender, district
    )
    return success

def get_client_profile(client_id):
    return get_client_by_id(client_id)

def update_client_profile_service(client_id, email, phone, filename=None):
    return update_client_profile(client_id, email, phone, filename)

def save_favorite_lawyer(client_id, lawyer_id):
    return save_lawyer_for_client(client_id, lawyer_id)

def remove_favorite_lawyer(client_id, lawyer_id):
    return remove_saved_lawyer(client_id, lawyer_id)

def get_favorite_lawyers(client_id):
    return get_saved_lawyers_for_client(client_id)
