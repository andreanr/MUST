import hashlib
import os
from sqlalchemy import create_engine
from flask import (Flask, flash, redirect, render_template,
             request, session, redirect, url_for)
from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from dotenv import load_dotenv, find_dotenv
from app.sql_aux import (validate_username, add_user, validate_login,
        validate_email, musicians_list, movie_artists_list, get_concerts,
        get_new_music, get_new_movies, add_music_preference, delete_music_preference,
        get_user_musicians, get_user_musicians_complement, validate_user_fields, get_cities,
        add_movie_preference, delete_movie_preference, get_user_actresses, get_user_actresses_complement)

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
    username = request.form.get('username', None)
    password = request.form.get('password', None)
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
    cities = get_cities()
    if request.method == 'GET':
        return render_template('register.html', cities=cities)
    # Add to postgresql
    username = request.form.get('username', None)
    name = request.form.get('name', None)
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    city_id = request.form.get('city', None)
    if not validate_user_fields(username, name, email, password, city_id):
        flash('** Please fill all fields')
        return render_template('register.html', cities=cities)
    elif not validate_username(username):
        flash('** Username already taken')
        return render_template('register.html', cities=cities)
    elif not validate_email(email):
        flash('** Email already been used')
        return render_template('register.html', cities=cities)
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
        musicians = musicians_list(username)
        movie_artists = movie_artists_list(username)
        concerts_table = get_concerts(username)
        new_music_table = get_new_music(username)
        new_movies_table = get_new_movies(username)
        return render_template('homepage.html',
                                name=username,
                                musicians=musicians,
                                movie_artists=movie_artists,
                                concerts_table=concerts_table,
                                new_music_table=new_music_table,
                                new_movies_table=new_movies_table)
    else:
        return redirect(url_for('login'))


@login_required
@app.route('/add_musician', methods=['GET', 'POST'])
def add_musician():
    if current_user.is_authenticated:
        username = current_user.id
        if request.method == 'GET':
            user_musicians_complement = get_user_musicians_complement(username)
            return render_template('add_musician.html', user_musicians_complement=user_musicians_complement)
        sp_id = request.form['sp_id']
        add_music_preference(username, sp_id)
        user_musicians_complement = get_user_musicians_complement(username)
        flash('Musician successfully added')
        return render_template('add_musician.html', user_musicians_complement=user_musicians_complement)


@login_required
@app.route('/delete_musician', methods=['GET', 'POST'])
def delete_musician():
    if current_user.is_authenticated:
        username = current_user.id
        if request.method == 'GET':
            user_musicians = get_user_musicians(username)
            return render_template('delete_musician.html', user_musicians=user_musicians)
        sp_id = request.form['sp_id']
        delete_music_preference(username, sp_id)
        user_musicians = get_user_musicians(username)
        flash('Musician successfully deleted')
        return render_template('delete_musician.html', user_musicians=user_musicians)


@login_required
@app.route('/add_actress', methods=['GET', 'POST'])
def add_actress():
    if current_user.is_authenticated:
        username = current_user.id
        if request.method == 'GET':
            user_actresses_complement = get_user_actresses_complement(username)
            return render_template('add_actress.html', user_actresses_complement=user_actresses_complement)
        mo_id = request.form['mo_id']
        add_movie_preference(username, mo_id)
        user_actresses_complement = get_user_actresses_complement(username)
        flash('Actor/Actress successfully added')
        return render_template('add_actress.html', user_actresses_complement=user_actresses_complement)


@login_required
@app.route('/delete_actress', methods=['GET', 'POST'])
def delete_actress():
    if current_user.is_authenticated:
        username = current_user.id
        if request.method == 'GET':
            user_actresses = get_user_actresses(username)
            return render_template('delete_actress.html', user_actresses=user_actresses)
        mo_id = request.form['mo_id']
        delete_movie_preference(username, mo_id)
        user_actresses = get_user_actresses(username)
        flash('Actor/Actress successfully deleted')
        return render_template('delete_actress.html', user_actresses=user_actresses)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return "You are logged out!"
