from models.admin_model import (
    get_lawyer_count, get_client_count, get_pending_lawyers, 
    get_all_users_for_admin, approve_lawyer_account
)
from models.user_model import update_user_details

def get_admin_dashboard_data():
    lawyer_count = get_lawyer_count()
    client_count = get_client_count()
    pending_lawyers = get_pending_lawyers()
    all_users, all_lawyers, all_clients = get_all_users_for_admin()
    
    return {
        'lawyer_count': lawyer_count,
        'client_count': client_count,
        'pending_lawyers': pending_lawyers,
        'all_users': all_users,
        'all_lawyers': all_lawyers,
        'all_clients': all_clients
    }

def approve_lawyer(lawyer_id):
    return approve_lawyer_account(lawyer_id)

def update_user(user_id, role, new_email, new_name, new_specialization=None):
    if not new_email or not new_name or not user_id or not role:
        return False, "Missing required fields."
    
    success = update_user_details(user_id, role, new_email, new_name, new_specialization)
    if success:
        return True, f"{role}'s details updated successfully."
    return False, "Error updating user details."
