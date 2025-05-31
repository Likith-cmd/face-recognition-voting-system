from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        voter_id = request.form.get('voter_id')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if not user_type:
            flash("Please select user type to login.")
            return redirect(url_for('auth.login'))

        # Example logic (adjust as per your DB logic):
        if user_type == 'admin':
            # Verify admin credentials here
            if voter_id == "admin" and password == "adminpass":  # example hardcoded check
                session['user'] = voter_id
                session['user_type'] = user_type
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid admin credentials.")
        elif user_type == 'voter':
            # Verify voter credentials here
            # Replace below with your DB check for voter_id and password
            if voter_id == "voter1" and password == "voterpass":  # example
                session['user'] = voter_id
                session['user_type'] = user_type
                return redirect(url_for('vote'))
            else:
                flash("Invalid voter credentials.")
        else:
            flash("Unknown user type.")

        return redirect(url_for('auth.login'))

    return render_template('login.html')
