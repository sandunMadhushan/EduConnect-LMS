from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import text
from database import get_studygroups, create_studygroup, db_post_a_question, get_all_questions

import openai
# from openai import OpenAI
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document

import time
from openai.error import RateLimitError

# Load environment variables
load_dotenv()

app = Flask(__name__)

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
def hello():
     return render_template("index.html")

@app.route("/dashboard")
def dashboard():
     return render_template("dashboard.html")
  
@app.route('/study-groups')
def studygroups():
     return render_template('study-groups.html')

# Route for Discussion Forums
@app.route('/discussion-forums')
def discussionforums():
     return render_template('discussion-forums.html')

# Route for AI Tools
@app.route('/ai-tools')
def aitools():
     return render_template('ai-tools.html')

# Route for Study Sessions
@app.route('/study-sessions')
def studysessions():
     return render_template('study-sessions.html')


@app.route('/create-study-group', methods=['GET'])
def show_create_studygroup():
    return render_template('create-study-group.html')

@app.route('/create-study-group', methods=['POST'])
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
def ViewStudygroups():
     studygroups_list = load_studygroups_from_db()
     return render_template('study-groups-view.html', studygroups=studygroups_list)

@app.route('/post-a-question', methods=['GET'])
def show_post_a_question():
    return render_template('post-a-question.html')

@app.route('/post-a-question', methods=['POST'])
def post_a_question():
    title = request.form.get('title')
    category = request.form.get('category')
    question = request.form.get('question')
    q_id = db_post_a_question(title, category, question)
    # if q_id:
    #     return redirect(url_for('ViewQuestions'))
    return "Successfully posted your question!", 200

# @app.route('/summarize-content', methods=['GET', 'POST'])
# def summarization_form():
#     if request.method == 'GET':
#         return render_template('summarization-form.html')  # Show the form

#     if 'upload' not in request.files:
#         return jsonify({'error': 'No file uploaded'}), 400

#     upload = request.files['upload']

#     if upload.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Ensure the uploads directory exists
#     os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

#     file_path = os.path.join(app.config["UPLOAD_FOLDER"], upload.filename)
#     upload.save(file_path)

#     # Extract text from the uploaded file (assuming extract_text is defined)
#     text = extract_text(file_path)

#     if not text:
#         return jsonify({'error': 'Unable to extract text from the file'}), 400
    
#     print(request.form)

#      # Get the custom instruction (description) from the form
#     description = request.form.get('description')
    
#     print(f"Description: {description}") 

#     if not description:
#         return jsonify({'error': 'No description provided'}), 400

#     # Summarize the extracted text with the custom description
#     summary = summarize_text(text, description)

#     # return render_template('summarization-form.html', summary=summary)
#     return jsonify({'summary': summary})

@app.route('/summarize-content', methods=['GET', 'POST'])
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
def insights_form():
    return render_template('insights.html')

@app.route('/schedule-session')
def schedule_session():
    return render_template('schedule-session.html')

@app.route('/profile')
def profile():
    user = {'username': 'Miguel'}
    return render_template('profile.html, user=user')

@app.route('/browse-forum/all')
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