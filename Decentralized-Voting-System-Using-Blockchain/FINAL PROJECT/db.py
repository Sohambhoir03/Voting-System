import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")  # Replace with your path
firebase_admin.initialize_app(cred)
db = firestore.client()

# ----------------- User Functions -----------------
def register_user(connection, aadhar, name):
    """Register user without email/OTP"""
    user_ref = db.collection("users").document(aadhar)
    user_ref.set({
        "aadhar": aadhar,
        "name": name,
        "has_voted": False
    })

def authenticate_user(connection, aadhar):
    user_ref = db.collection("users").document(aadhar)
    user_doc = user_ref.get()
    if user_doc.exists:
        return {"id": aadhar, **user_doc.to_dict()}
    return None

def authenticate_admin(connection, username, password):
    if username == "admin123" and password == "Pass@123":
        return {"id": "admin", "name": "Admin"}
    return None

def save_wallet(connection, user_id, wallet):
    """Save MetaMask wallet address for a user"""
    db.collection("users").document(user_id).update({"wallet": wallet})

def verify_user(connection, user_id):
    """Mark user as verified after MetaMask auth"""
    db.collection("users").document(user_id).update({"verified": True})

# ----------------- Candidate / Election Functions -----------------
def create_election(connection, name, start_date, end_date,
                    candidate1_name, candidate1_party,
                    candidate2_name, candidate2_party):
    election_ref = db.collection("elections").document()
    election_ref.set({
        "name": name,
        "start_date": start_date,
        "end_date": end_date,
        "candidates": [
            {"name": candidate1_name, "party": candidate1_party},
            {"name": candidate2_name, "party": candidate2_party}
        ]
    })

def get_all_elections(connection):
    elections = db.collection("elections").stream()
    election_list = []
    for e in elections:
        data = e.to_dict()
        election_list.append({
            "id": e.id,
            "name": data.get("name"),
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
            "candidate1_name": data["candidates"][0]["name"],
            "candidate1_party": data["candidates"][0].get("party", ""),
            "candidate2_name": data["candidates"][1]["name"],
            "candidate2_party": data["candidates"][1].get("party", ""),
            "has_voted": False  # Default, will be updated per user in app.py
        })
    return election_list

def delete_election(connection, election_id):
    db.collection("elections").document(election_id).delete()

# ----------------- Voting Functions -----------------
def has_user_voted(connection, user_id, election_id):
    votes = db.collection("votes") \
              .where("voter_id", "==", user_id) \
              .where("election_id", "==", election_id) \
              .stream()
    return any(votes)

def record_vote(connection, voter_id, election_id, candidate_name):
    db.collection("votes").add({
        "voter_id": voter_id,
        "election_id": election_id,
        "candidate": candidate_name
    })
    db.collection("users").document(voter_id).update({"has_voted": True})

# ----------------- Admin / Utility -----------------
def get_all_users(connection):
    users = db.collection("users").stream()
    return [{"id": u.id, **u.to_dict()} for u in users]

def get_all_votes(connection):
    votes_stream = db.collection("votes").stream()
    votes_list = []
    for v in votes_stream:
        vdata = v.to_dict()
        voter_doc = db.collection("users").document(vdata["voter_id"]).get()
        votes_list.append({
            "id": v.id,
            "voter": voter_doc.to_dict()["name"] if voter_doc.exists else "Unknown",
            "candidate": vdata["candidate"],
            "election_id": vdata["election_id"]
        })
    return votes_list
