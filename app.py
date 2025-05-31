from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'voting system.db'

# --- Helper function to get DB connection ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Home route ---
@app.route('/')
def home():
    return render_template('home.html')

# --- Voter Login Page ---
@app.route('/voter_login', methods=['GET', 'POST'])
def voter_login():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM voters WHERE voter_id = ?", (voter_id,))
        voter = c.fetchone()
        conn.close()
        if voter:
            session['voter_id'] = voter['voter_id']
            return redirect(url_for('vote_page'))
        else:
            flash("Invalid Voter ID")
    return render_template('voter_login.html')

# --- Voting Page ---
@app.route('/vote', methods=['GET', 'POST'])
def vote_page():
    voter_id = session.get('voter_id')
    if not voter_id:
        return redirect(url_for('voter_login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, encoding, has_voted FROM voters WHERE voter_id = ?", (voter_id,))
    voter = c.fetchone()

    if not voter:
        conn.close()
        flash("Voter not found.")
        return redirect(url_for('voter_login'))

    if voter['has_voted']:
        conn.close()
        return render_template('vote_success.html', message="You have already voted.")

    c.execute("SELECT * FROM candidates")
    candidates = c.fetchall()

    if request.method == 'POST':
        candidate_id = request.form['candidate_id']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO votes (voter_id, candidate_id, timestamp) VALUES (?, ?, ?)",
                  (voter_id, candidate_id, timestamp))
        c.execute("UPDATE voters SET has_voted = 1 WHERE voter_id = ?", (voter_id,))
        conn.commit()
        conn.close()
        return render_template('vote_success.html', message="Your vote has been recorded successfully.")

    conn.close()
    return render_template('vote.html', voter=voter, candidates=candidates)

# --- Admin Login Page ---
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        admin = c.fetchone()
        conn.close()

        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials")
    return render_template('admin_login.html')

# --- Admin Dashboard ---
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db()
    c = conn.cursor()

    # Count voters, candidates, votes
    c.execute("SELECT COUNT(*) as count FROM voters")
    total_voters = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM candidates")
    total_candidates = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM votes")
    total_votes = c.fetchone()['count']

    stats = {
        'total_voters': total_voters,
        'total_candidates': total_candidates,
        'total_votes': total_votes
    }

    # View vote results
    c.execute('''
        SELECT candidates.name, COUNT(votes.id) as vote_count
        FROM candidates
        LEFT JOIN votes ON candidates.id = votes.candidate_id
        GROUP BY candidates.id
    ''')
    results = c.fetchall()

    conn.close()
    return render_template('admin_dashboard.html', stats=stats, votes=results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
