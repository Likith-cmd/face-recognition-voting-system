from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3

admin_bp = Blueprint('admin', __name__)

def get_db_connection():
    conn = sqlite3.connect('voting_system.db')
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/admin', methods=['GET'])
def admin_dashboard():
    conn = get_db_connection()
    voters = conn.execute("SELECT voter_id, name, has_voted FROM voters").fetchall()
    results = conn.execute("SELECT voter_id, candidate FROM votes").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', voters=voters, results=results)

@admin_bp.route('/reset_votes', methods=['POST'])
def reset_votes():
    conn = get_db_connection()
    conn.execute("DELETE FROM votes")
    conn.execute("UPDATE voters SET has_voted = 0")
    conn.commit()
    conn.close()
    flash("All votes have been reset.")
    return redirect(url_for('admin.admin_dashboard'))
