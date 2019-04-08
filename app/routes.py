import hashlib
import os
from sqlalchemy import create_engine
from flask import (Flask, flash, redirect, render_template,
             request, session, redirect, url_for)
from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from dotenv import load_dotenv, find_dotenv
from app.sql_aux import (validate_username, add_user, validate_login,
        validate_email, musicians_list)

from app import app, login_manager

# Load environment variables
load_dotenv(find_dotenv())

# PostgreSQL credentials
PGDATABASE = os.environ.get('PGDATABASE')
PGPASSWORD = os.environ.get('PGPASSWORD')
PGUSER = os.environ.get('PGUSER')
PGHOST = os.environ.get('PGHOST')

engine = create_engine('postgresql://{user}:{password}@{host}/{database}'.format(
                            host = PGHOST,
                            database = PGDATABASE,
                            user = PGUSER,
                            password = PGPASSWORD))


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    if validate_login(username, password):
        flash('Logged in successfully.')
        login_user(User(username))
        return redirect(url_for('homepage'))
    else:
        error = 'Invalid username/password'
        flash(error)
        return render_template('login.html')


@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    # Add to postgresql
    username = request.form['username']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    city_id = request.form['city']
    if not validate_username(username):
        flash('Username already taken')
        return render_template('register.html')
    elif not validate_email(email):
        flash('Email already been used')
        return render_template('register.html')
    else:
        add_user(username, name, email, password, city_id)
        flash('User successfully registered')
        return redirect(url_for('login'))

@login_required
@app.route('/homepage')
def homepage():
    # TODO queries that gives a list of their artists / musicians and
    # events/songs/movies coming
    if current_user.is_authenticated:
        username = current_user.id
        musicians_list(username)
        return render_template('homepage.html', name=username)
    else:
        return redirect(url_for('login'))

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return "you are logged out"
