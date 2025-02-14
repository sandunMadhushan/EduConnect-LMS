from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

STUDYGROUPS = [
  {
    'id': 1,
    'name': 'Study Group 1',
    'description': 'This is the first study group',
    'members': ['John', 'Jane', 'Bob']
  },
  {
    'id': 2,
    'name': 'Study Group 2',
    'description': 'This is the second study group',
    'members': ['Alice', 'Charlie', 'David']
  },
  {
    'id': 3,
    'name': 'Study Group 3',
    'description': 'This is the third study group',
    'members': ['Eve', 'Frank', 'Grace']
  },
  {
    'id': 4,
    'name': 'Study Group 4',
    'description': 'This is the fourth study group',
    'members': ['Hannah', 'Ivy', 'Jack']
  },
  {
    'id': 5,
    'name': 'Study Group 5',
    'description': 'This is the fifth study group',
    'members': ['Karen', 'Liam', 'Mia']
  }
]

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
    return render_template('study-groups-view.html', studygroups=STUDYGROUPS)