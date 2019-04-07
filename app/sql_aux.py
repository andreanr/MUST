import hashlib
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

