from flask import Blueprint, request, render_template, send_from_directory, session
import os
from config import UPLOAD_FOLDER, FRONTEND_DIR
from services.search_service import search_for_lawyer
from models.user_model import get_client_by_id

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/search-lawyer', methods=['GET', 'POST'])
def search_lawyer_route():
    query_text = ""
    
    # Auto-patch missing client name
    if 'client_id' in session and 'client_name' not in session:
        client = get_client_by_id(session['client_id'])
        if client: session['client_name'] = client['name']
            
    if request.method == 'POST':
        query_text = request.form.get('query_text', '')
        filter_gender = request.form.get('filter_gender', '')
        filter_district = request.form.get('filter_district', '')
    else:
        query_text = request.args.get('query_text', '')
        filter_gender = request.args.get('filter_gender', '')
        filter_district = request.args.get('filter_district', '')
        
    result = search_for_lawyer(query_text, filter_gender, filter_district)

    return render_template('pages/search-lawyer.html', 
                            query_text=query_text,
                            filter_gender=filter_gender,
                            filter_district=filter_district,
                            predicted_specialization=result.get('predicted_specialization'), 
                            confidence=result.get('confidence'),
                            lawyers=result.get('lawyers', []))

@main_bp.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@main_bp.route('/pages/<path:filename>')
def serve_pages(filename):
    # Some pages aren't rendering templates through a dedicated function, so this catches them
    if filename.endswith('.html'):
        return render_template('pages/' + filename)
    return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), filename)

@main_bp.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)
