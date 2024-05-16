from flask import Blueprint, render_template, request,redirect, flash, redirect, url_for, jsonify
from .models import User,Admin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
import hashlib
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta


admin = Blueprint('admin', __name__)

@admin.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dash():
    all_users = User.query.all()
    total_users = len(all_users)

    # Calculate the start date of the current week (assuming Monday is the start of the week)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())

    # Filter new users registered this week
    new_users_this_week = [user for user in all_users if user.reg_date >= start_of_week]

    # Calculate the number of new users registered this week
    num_new_users_this_week = len(new_users_this_week)

    return render_template("admin_dashboard.html", analy_data=all_users, click_num=total_users, session=num_new_users_this_week)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin.route('/reset_pass', methods=['POST'])
@login_required
def reset():
    if request.method == 'POST':
        data = request.json  # Parse JSON data from request body
        email = data.get('email')
        text = data.get('text')
        user = User.query.filter_by(email=email).first() 
        if user:
            hashed_pass = generate_password_hash(text, method='pbkdf2:sha256', salt_length=8)
            user.password = hashed_pass
            db.session.commit()
            return jsonify({'success': True})
    
    return jsonify({'success': False})

@admin.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if request.method == 'POST':
        data = request.json  # Parse JSON data from request body
        email = data.get('email')
        
        # Find the user by email
        user = User.query.filter_by(email=email).first() 
        if user:
            # Delete the user from the database
            db.session.delete(user)
            # Commit the changes to the database
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False})



@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('email')
        email = request.form.get('email')
        password = request.form.get('password')

        user = Admin.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect("/admin/admin_dashboard")
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("admin_login.html", user=current_user)