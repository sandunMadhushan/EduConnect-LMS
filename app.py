from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from sqlalchemy import text
from database import get_studygroups, create_studygroup, db_post_a_question, get_all_questions,  register_user, login_user, get_user_by_id, update_user, update_user_profile_pic,update_user_profile, check_email_exists, send_welcome_email_sync, save_reset_token, verify_reset_token, update_password_with_token, get_user_by_email
import openai
# from openai import OpenAI
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
import time
from openai.error import RateLimitError
from functools import wraps

from azure.communication.email import EmailClient
import asyncio
from concurrent.futures import ThreadPoolExecutor

import secrets
from datetime import datetime, timedelta

email_executor = ThreadPoolExecutor(max_workers=3)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def load_studygroups_from_db():
    results = get_studygroups()
    studygroups = []
    for row in results:
        studygroups.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'members': row[3]
        })
    return studygroups

def load_questions_from_db():
    results = get_all_questions()
    questions = []
    for row in results:
        questions.append({
            'id': row[0],
            'title': row[1],
            'category': row[2],
            'description': row[3]
        })
    return questions

@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = login_user(email, password)
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('index'))
    
        # Check if email exists before registration
    if check_email_exists(email):
        flash('Email already registered', 'error')
        return redirect(url_for('index'))
    
    user_id = register_user(name, email, password)
    if user_id:
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        def send_email_task():
            email_sent = send_welcome_email_sync(email, name)
            if not email_sent:
                print("Failed to send welcome email")
            
        email_executor.submit(send_email_task)
        
        flash('Registration successful! A welcome email has been sent to your inbox. Please check your spam folder if you don’t see it.', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Registration failed. Email might already be registered.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session['user_id'])
    return render_template("dashboard.html", user=user)
  
@app.route('/study-groups')
@login_required
def studygroups():
    return render_template('study-groups.html')

@app.route('/discussion-forums')
@login_required
def discussionforums():
    return render_template('discussion-forums.html')

@app.route('/ai-tools')
@login_required
def aitools():
    return render_template('ai-tools.html')

@app.route('/study-sessions')
@login_required
def studysessions():
    return render_template('study-sessions.html')


@app.route('/create-study-group', methods=['GET'])
@login_required
def show_create_studygroup():
    return render_template('create-study-group.html')

@app.route('/create-study-group', methods=['POST'])
@login_required
def create_new_studygroup():
    name = request.form.get('name')
    description = request.form.get('description')
    members = request.form.get('members')
    group_id = create_studygroup(name, description, members)
    if group_id:
        return redirect(url_for('ViewStudygroups'))
    return "Error creating study group", 500

if __name__ == "__main__":
     app.run()

@app.route('/study-groups/all')
@login_required
def ViewStudygroups():
     studygroups_list = load_studygroups_from_db()
     return render_template('study-groups-view.html', studygroups=studygroups_list)

@app.route('/post-a-question', methods=['GET'])
@login_required
def show_post_a_question():
    return render_template('post-a-question.html')

@app.route('/post-a-question', methods=['POST'])
@login_required
def post_a_question():
    title = request.form.get('title')
    category = request.form.get('category')
    question = request.form.get('question')
    q_id = db_post_a_question(title, category, question)
    # if q_id:
    #     return redirect(url_for('ViewQuestions'))
    return "Successfully posted your question!", 200

@app.route('/summarize-content', methods=['GET', 'POST'])
@login_required
def summarization_form():
    if request.method == 'POST':
        # Debugging the form data and file
        print("Form data:", request.form)
        print("Files:", request.files)

        description = request.form.get('description')
        file = request.files.get('upload')

        if not description:
            return jsonify({'error': 'Description is required'}), 400

        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        # Assuming extract_text is defined
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        text = extract_text(file_path)

        if not text:
            return jsonify({'error': 'Unable to extract text from the file'}), 400

        summary = summarize_text(text, description)

        return jsonify({'summary': summary})

    return render_template('summarization-form.html')



@app.route('/generate-insights')
@login_required
def insights_form():
    return render_template('insights.html')

@app.route('/schedule-session')
@login_required
def schedule_session():
    return render_template('schedule-session.html')


@app.route('/browse-forum/all')
@login_required
def ViewQuestions():
    questions_list = load_questions_from_db()
    return render_template('browse-forum.html', questions=questions_list)


# Configure upload folder
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
openai.api_key = os.getenv("OPENAI_API_KEY")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text(text, description):
    try:
        
        prompt = f"{description}\n\nText to summarize: {text}"
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text},
                      {"role": "user", "content": prompt}
                      ],
        )
        return response.choices[0].message["content"]
    except RateLimitError:
        print("Rate limit exceeded. Retrying in 30 seconds...")
        time.sleep(30)  # Wait for 30 seconds before retrying
        return summarize_text(text)



def extract_text(file_path):
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            return " ".join([page.extract_text() for page in reader.pages])
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return " ".join([p.text for p in doc.paragraphs])
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
        
# Custom error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500 


UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Get current user
    user = get_user_by_id(session['user_id'])
    
    if request.method == 'POST':
        # Handle profile update
        name = request.form.get('name')
        bio = request.form.get('bio')
        
        # Update user info in database
        if update_user_profile(session['user_id'], name=name, bio=bio):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Error updating profile', 'error')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile-pic' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['profile-pic']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename):
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Secure the filename and make it unique
        filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Update user's profile picture in database
        if update_user_profile_pic(session['user_id'], f'/static/uploads/profile_pics/{filename}'):
            flash('Profile picture updated successfully!', 'success')
        else:
            flash('Error updating profile picture', 'error')
    else:
        flash('Invalid file type', 'error')
    
    return redirect(url_for('profile'))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        
        # Check if email exists
        if not check_email_exists(email):
            flash("Email address not found.", "error")
            return redirect(url_for("forgot_password"))
        
        # Get user's name
        user = get_user_by_email(email)
        if not user:
            flash("An error occurred.", "error")
            return redirect(url_for("forgot_password"))
        
        # Generate reset token and save to database
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=24)
        
        if save_reset_token(email, token, expiry):
            # Send reset email using Azure
            if send_password_reset_email(email, user['name'], token):
                flash("Password reset link sent to your email.", "success")
                return redirect(url_for("index"))
            else:
                flash("Error sending email. Please try again later.", "error")
                return redirect(url_for("forgot_password"))
        
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for("forgot_password"))
    
    return render_template("index.html")

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("reset_password", token=token))
        
        if update_password_with_token(token, password):
            flash("Your password has been updated.", "success")
            return redirect(url_for("index"))
        
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("index"))
    
    # Verify token is valid on GET request
    if verify_reset_token(token):
        return render_template("index.html", show_reset_form=True, reset_token=token)
    
    flash("Invalid or expired reset link.", "error")
    return redirect(url_for("index"))

def send_password_reset_email(user_email, name, reset_token):
    """Send password reset email using Azure Email Communication Service"""
    try:
        connection_string = os.getenv('CONNECTION_STRING')
        sender_address = os.getenv('SENDER_ADDRESS')
        email_client = EmailClient.from_connection_string(connection_string)
        
        reset_link = f"https://educonnect-lms.onrender.com/reset-password/{reset_token}"
        
        message = {
            "senderAddress": sender_address,
            "content": {
                "subject": "EduConnect Password Reset Request",
                "plainText": f"""
                Hi {name},

                You recently requested to reset your password for your EduConnect account. Click the link below to reset it:

                {reset_link}

                This password reset link is only valid for 24 hours. If you did not request a password reset, please ignore this email.

                Best regards,
                The EduConnect Team
                """,
                "html": f"""
                    <html>
                        <body>
                            <h1>Password Reset Request</h1>
                            <p>Hi {name},</p>
                            <p>You recently requested to reset your password for your EduConnect account. Click the button below to reset it:</p>
                            <br>
                            <a href="{reset_link}" style="color: #ffffff; background: #1d3557; background-image: linear-gradient(145deg, #1d3557, #457b9d); padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; text-align: center;">
                                Reset Your Password
                            </a>
                            <br>
                            <p style="color: #666; font-size: 14px;">This password reset link is only valid for 24 hours. If you did not request a password reset, please ignore this email.</p>
                            <br>
                            <p>Best regards,</p>
                            <p>The EduConnect Team</p>
                            <hr>
                            <p><img src="https://i.imgur.com/8yUWDDq.png" alt="EduConnect Logo" style="width:200px"></p>
                            <p style="font-size: 12px; color: #777;">This is an automated email. Please do not reply.</p>
                        </body>
                    </html>
                """
            },
            "recipients": {
                "to": [{"address": user_email, "displayName": name}]
            }
        }
        
        poller = email_client.begin_send(message)
        result = poller.result()
        return True
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False