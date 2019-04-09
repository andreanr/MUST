import hashlib
import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

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


def hash_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def validate_username(username):
    db_conn = engine.connect()
    cursor = db_conn.execute("SELECT  exists(SELECT username FROM users WHERE username = '{}')".format(username))
    db_conn.close()
    record = cursor.fetchone()
    print(record)
    if record[0]:
        return False
    else:
        return True

def validate_email(email):
    db_conn = engine.connect()
    cursor = db_conn.execute("SELECT exists(SELECT email FROM users WHERE email = '{}')".format(email))
    db_conn.close()
    record = cursor.fetchone()
    print(record)
    if record[0]:
        return False
    else:
        return True


def validate_login(username, password):
    query = """SELECT EXISTS(SELECT username FROM users
                            WHERE username = '{}'
                            AND password = '{}')""".format(username,
                                                           hash_password(password))
    with engine.connect() as db_conn:
        cursor = db_conn.execute(query)
        record = cursor.fetchone()
    if record[0]:
        return True
    else:
        return False


def add_user(username, name, email, password, city_id):
    query = """INSERT INTO users (username, name, email, password, city_id)
                 VALUES ('{username}', '{name}', '{email}', '{password}',
                 {city_id})""".format(username=username,
                                      name=name,
                                      email=email,
                                      password=hash_password(password),
                                      city_id=city_id)
    with engine.connect() as db_conn:
        res = db_conn.execute(query)


def musicians_list(username):
    query = """SELECT name FROM music_preference
                NATURAL JOIN musicians
                WHERE username = '{username}'""".format(username=username)

    with engine.connect() as db_conn:
        cursor = db_conn.execute(query)
        record = cursor.fetchall()
    musicians = ", ".join([x[0] for x in record])
    return musicians

def movie_artists_list(username):
    query = """SELECT name FROM movie_preference
                NATURAL JOIN movie_artists
                WHERE username = '{username}'""".format(username=username)

    with engine.connect() as db_conn:
        cursor = db_conn.execute(query)
        record = cursor.fetchall()
    movie_artists = ", ".join([x[0] for x in record])
    return movie_artists


def get_concerts(username):
    query = """WITH music_pref_userx AS (
                SELECT sk_id, username, m.name AS musician_name, city_id
	            FROM users AS U
	            NATURAL JOIN music_preference AS mp
	            JOIN musicians AS m USING (sp_id)
	            WHERE username = '{username}'
            ) SELECT  musician_name, c.event_date, c.event_name,
                        c.venue, city_name, country, url
            FROM music_pref_userx AS u
            JOIN concert_performances  AS cp  USING (sk_id)
            JOIN concerts AS c
  	        ON u.city_id = c.city_id AND c.event_id = cp.event_id
            JOIN city ON c.city_id = city.city_id
            ORDER BY event_date""".format(username=username)
    with engine.connect() as db_conn:
        cursor = db_conn.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    if len(df) > 0:
        df.columns = cursor.keys()
        return [df.to_html(classes='table', header="true", index=False)]
    else:
        return None

def get_new_music(username):
    query="""WITH music_pref_userx AS (
                SELECT sp_id, username, m.name AS musician_name
                FROM music_preference AS mp
	            JOIN musicians AS m USING (sp_id)
	            WHERE username = '{username}'
            ) SELECT  musician_name, m.release_date, m.name, m.album_type, url
                FROM music_pref_userx AS u
                JOIN  music_releases USING (sp_id)
                JOIN new_music AS m USING (release_id)
                ORDER BY release_date""".format(username=username)
    with engine.connect() as db_conn:
        cursor = db_conn.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    if len(df) > 0:
        df.columns = cursor.keys()
        return [df.to_html(classes='table', header="true", index=False)]
    else:
        return None

def get_new_movies(username):
    query = """WITH actors_pref_userx AS (
 	            SELECT mo_id, username, m.name AS artist_name
 	            FROM movie_preference AS mp
 	            JOIN movie_artists AS m USING (mo_id)
 	            WHERE username = '{username}'
             ) SELECT artist_name, release_date, title, description, url
                FROM actors_pref_userx
                JOIN movie_releases USING (mo_id)
                JOIN new_films USING (mdb_id)
                ORDER BY release_date""".format(username=username)
    with engine.connect() as db_conn:
        cursor = db_conn.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    if len(df) > 0:
        df.columns = cursor.keys()
        return [df.to_html(classes='table', header="true", index=False)]
    else:
        return None


def add_music_preference(username, sp_id):
    query = """INSERT INTO music_preference (username, sp_id)
                 VALUES ('{username}', '{sp_id}')""".format(username=username,
                                                            sp_id=sp_id)
    with engine.connect() as db_conn:
        res = db_conn.execute(query)


def delete_music_preference(username, sp_id):
    query = "DELETE FROM music_preference WHERE username = '{}' AND sp_id = '{}';".format(username, sp_id)

    with engine.connect() as db_conn:
        res = db_conn.execute(query)


def validate_musician(username, sp_id):
    db_conn = engine.connect()
    cursor = db_conn.execute(
        "SELECT EXISTS (SELECT sp_id FROM music_preference WHERE username = '{}' AND sp_id = '{}')".format(username, sp_id)
    )
    db_conn.close()
    record = cursor.fetchone()
    print(record)
    if record[0]:
        return False
    else:
        return True

def get_user_musicians(username):
    db_conn = engine.connect()
    cursor = db_conn.execute(
        """
        SELECT sp_id, name
        FROM musicians
        WHERE sp_id IN (SELECT sp_id FROM music_preference WHERE username = '{}')
        """.format(username)
    )
    db_conn.close()
    user_musicians = cursor.fetchall()
    return(user_musicians)
