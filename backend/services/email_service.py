from flask_mail import Message
from extensions import mail
from flask import current_app

def send_new_request_notification(client_name, lawyer_email):
    """Sends an email to the lawyer when a client requests an appointment."""
    try:
        msg = Message(
            subject="New Client Request - Client - Lawyer Matching",
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[lawyer_email]
        )
        msg.body = f"Hello,\n\nYou have received a new consultation request from a client named {client_name}.\n\nPlease log in to your Lawyer Portal to view the request and Accept or Reject it.\n\nBest Regards,\nClient-Lawyer Matching System"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending request notification: {e}")
        return False

def send_acceptance_notification(client_email, lawyer_name):
    """Sends an email to the client when their request is accepted."""
    try:
        msg = Message(
            subject="Appointment Accepted! - Client - Lawyer Matching",
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[client_email]
        )
        msg.body = f"Hello,\n\nGreat news! Your consultation request has been officially ACCEPTED by {lawyer_name}.\n\nLog in to your Client Portal to view your Ongoing Cases.\n\nBest Regards,\nClient-Lawyer Matching System"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending acceptance notification: {e}")
        return False

def send_otp_email(user_email, otp):
    """Sends a Password Reset OTP to the requested user."""
    try:
        msg = Message(
            subject="Password Reset OTP - Client - Lawyer Matching",
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[user_email]
        )
        msg.body = f"Your password reset OTP is: {otp}\n\nThis code will expire in 15 minutes.\n\nIf you did not request this, please ignore this email.\n\nBest Regards,\nClient-Lawyer Matching System"
        mail.send(msg)
        return True
    except Exception as e:
        import traceback
        print(f"Failed to send email: {traceback.format_exc()}")
        return False

def send_status_update_notification(client_email, lawyer_name, status):
    """Sends an email to the client when a lawyer marks a case as Won, Lost, or Rejected."""
    try:
        msg = Message(
            subject=f"Case Status Update: {status} - Client - Lawyer Matching",
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[client_email]
        )
        msg.body = f"Hello,\n\nThe status of your case with {lawyer_name} has been updated to: {status}.\n\nLog in to your Client Portal for more details.\n\nBest Regards,\nClient-Lawyer Matching System"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending status update notification: {e}")
        return False
