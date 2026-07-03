from flask import Flask, render_template, request, redirect, session, url_for
import db
from blockchain import Blockchain
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Limit max upload size to 5 MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

blockchain = Blockchain()

# -----------------------
# Helper: Face Recognition
# -----------------------
def recognize_face(image_path):
    """
    Implement your face recognition logic here.
    Return user_id if face is recognized, otherwise None.
    """
    # Example placeholder
    # TODO: integrate Face++ API or local model
    return None

# -----------------------
# INDEX / HOME
# -----------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------
# VOTER REGISTRATION
# -----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        aadhar = request.form['aadhar']
        name = request.form['name']
        db.register_user(None, aadhar, name)
        return redirect(url_for('login'))
    return render_template('register.html')

# -----------------------
# VOTER LOGIN (Aadhar)
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        aadhar = request.form['aadhar']
        user = db.authenticate_user(None, aadhar)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Aadhar!"
    return render_template('login.html', error=error)

# -----------------------
# FACE LOGIN VIA WEBCAM
# -----------------------
@app.route('/face_login', methods=['GET', 'POST'])
def face_login():
    if request.method == 'POST':
        try:
            img_data = request.form.get('image')
            if not img_data:
                return "No image received!", 400

            # Remove prefix "data:image/png;base64,"
            img_data = img_data.split(",")[1]

            # Save image temporarily
            temp_file = "temp_face.png"
            with open(temp_file, "wb") as f:
                f.write(base64.b64decode(img_data))

            # Recognize face
            recognized_user_id = recognize_face(temp_file)

            # Delete temp file
            os.remove(temp_file)

            if recognized_user_id:
                session['user_id'] = recognized_user_id
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('face_login'))

        except Exception as e:
            return f"Error during face login: {str(e)}", 500

    return render_template('face_login.html')


# -----------------------
# ADMIN LOGIN
# -----------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        if admin_username == "admin123" and admin_password == "Pass@123":
            session['admin_id'] = 1
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials"
    return render_template('admin_login.html', error=error)

# -----------------------
# VOTER DASHBOARD
# -----------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    elections = db.get_all_elections(None)

    for election in elections:
        election['has_voted'] = db.has_user_voted(None, user_id, election['id'])

    return render_template('user.html', elections=elections, user_id=user_id)

# -----------------------
# VOTING ACTION
# -----------------------
@app.route('/vote', methods=['POST'])
def vote():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    voter_id = session['user_id']
    election_id = request.form['election_id']
    candidate_name = request.form['candidate']
    
    if not db.has_user_voted(None, voter_id, election_id):
        db.record_vote(None, voter_id, election_id, candidate_name)
        blockchain.add_block({
            'voter_id': voter_id,
            'election_id': election_id,
            'candidate': candidate_name
        })
    
    return redirect(url_for('dashboard'))

# -----------------------
# CREATE ELECTION
# -----------------------
@app.route('/create_election', methods=['POST'])
def create_election():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    election_name = request.form['name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    candidate1_name = request.form['candidate1_name']
    candidate1_party = request.form.get('candidate1_party', '')
    candidate2_name = request.form['candidate2_name']
    candidate2_party = request.form.get('candidate2_party', '')

    db.create_election(None, election_name, start_date, end_date,
                       candidate1_name, candidate1_party,
                       candidate2_name, candidate2_party)

    return redirect(url_for('admin_dashboard'))

# -----------------------
# ADMIN DASHBOARD
# -----------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    users = db.get_all_users(None)
    votes = db.get_all_votes(None)
    elections = db.get_all_elections(None)

    return render_template('admin_dashboard.html', users=users, votes=votes, elections=elections)

# -----------------------
# DELETE ELECTION
# -----------------------
@app.route('/delete_election', methods=['POST'])
def delete_election():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    election_id = request.form['election_id']
    db.delete_election(None, election_id)
    return redirect(url_for('admin_dashboard'))

# -----------------------
# RESULTS
# -----------------------
@app.route('/results')
def results():
    candidate_data = {
        "labels": ["Candidate A", "Candidate B"],
        "values": [250, 150, 100]
    }

    age_data = {
        "labels": ["18-25", "26-40", "41-60", "60+"],
        "values": [120, 200, 100, 80]
    }

    gender_data = {
        "labels": ["Male", "Female", "Other"],
        "values": [200, 150, 20]
    }

    region_data = {
        "labels": ["Maharashtra", "Karnataka", "Delhi", "Others"],
        "values": [200, 100, 150, 120]
    }

    return render_template(
        "results.html",
        candidate_data=candidate_data,
        age_data=age_data,
        gender_data=gender_data,
        region_data=region_data
    )

# -----------------------
# LOGOUT
# -----------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# -----------------------
# ABOUT PAGE
# -----------------------
@app.route('/about')
def about():
    return render_template('about.html')

# -----------------------
# RUN APP
# -----------------------
if __name__ == '__main__':
    app.run(debug=True)
