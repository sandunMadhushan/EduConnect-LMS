from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import text
from database import get_studygroups, create_studygroup

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


@app.route('/create-study-group', methods=['POST'])
def create_new_studygroup():
    name = request.form.get('name')
    description = request.form.get('description')
    group_id = create_studygroup(name, description)
    if group_id:
        return redirect(url_for('ViewStudygroups'))
    return "Error creating study group", 500

if __name__ == "__main__":
     app.run(host='0.0.0.0',debug=True)

@app.route('/study-groups/all')
def ViewStudygroups():
     studygroups_list = load_studygroups_from_db()
     return render_template('study-groups-view.html', studygroups=studygroups_list)
