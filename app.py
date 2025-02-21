from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from sqlalchemy import text
from database import get_studygroups, create_studygroup, db_post_a_question, get_all_questions,  register_user, login_user, get_user_by_id
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
        return redirect(url_for('hello'))
    
    user_id = register_user(name, email, None, password)  # Address is optional
    if user_id:
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html, user=user')

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