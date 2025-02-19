from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import text
from database import get_studygroups, create_studygroup, db_post_a_question, get_all_questions

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

@app.route('/summarize-content')
def summarization_form():
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