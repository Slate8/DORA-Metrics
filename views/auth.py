from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import User
from db import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('start_page'))
        else:
           error = "Benutzername oder Passwort ist nicht korrekt!"
    return render_template("login.html",error=error)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['new_username']
        password = request.form['new_password']

        # Überprüfen, ob der Benutzername bereits existiert
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_message = "Dieser Benutzername ist bereits vergeben."
            return render_template('login.html', register_error=error_message)

        # Hashen des Passworts und Erstellen eines neuen Benutzers
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('login.html')
