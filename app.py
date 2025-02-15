from flask import Flask, render_template, request, redirect, url_for
from database import engine
from sqlalchemy import text

app = Flask(__name__)

def load_studygroups_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM studygroups"))
    studygroups = []
    for row in result.all():
      studygroups.append(dict(row))
    return studygroups

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

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

@app.route('/study-groups/all')
def ViewStudygroups():
    studygroups = load_studygroups_from_db()
    return render_template('study-groups-view.html', studygroups=studygroups)