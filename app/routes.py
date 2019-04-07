import hashlib
import os
from sqlalchemy import create_engine
from flask import (Flask, flash, redirect, render_template,
             request, session, redirect, url_for)
from dotenv import load_dotenv, find_dotenv
from app.sql_aux import validate_username, add_user, validate_login

from app import app

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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    if validate_login(username, password):
        return redirect(url_for('index'))
    else:
        error = 'Invalid username/password'
        return render_template('login.html', error=error)


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
    if validate_username(username):
        add_user(username, name, email, password, city_id)
        flash('User successfully registered')
        return redirect(url_for('login'))
    else:
        error = 'Username already taken'
        return render_template('register.html', error=error)

