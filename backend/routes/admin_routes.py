from flask import Blueprint, request, redirect, render_template, flash
from services.admin_service import get_admin_dashboard_data, approve_lawyer, update_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/pages/admin-dashboard.html')
def admin_dashboard():
    # Note: In a real app we'd want `@login_required` or check for admin session here
    data = get_admin_dashboard_data()
    
    return render_template('pages/admin-dashboard.html', **data)

@admin_bp.route('/admin/approve-lawyer/<int:lawyer_id>', methods=['POST'])
def admin_approve_lawyer(lawyer_id):
    success = approve_lawyer(lawyer_id)
    if success:
        flash('Lawyer account approved successfully.', 'success')
    return redirect('/pages/admin-dashboard.html')

@admin_bp.route('/admin/update-user', methods=['POST'])
def admin_update_user():
    user_id = request.form.get('user_id')
    role = request.form.get('role')
    new_email = request.form.get('new_email')
    new_name = request.form.get('new_name')
    new_specialization = request.form.get('new_specialization')
    
    success, message = update_user(user_id, role, new_email, new_name, new_specialization)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
        
    return redirect('/pages/admin-dashboard.html')
