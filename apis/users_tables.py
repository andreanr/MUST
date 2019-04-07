import hashlib
import pandas as pd
import sqlalchemy

import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# PostgreSQL credentials
PGDATABASE = os.environ.get('PGDATABASE')
PGPASSWORD = os.environ.get('PGPASSWORD')
PGUSER = os.environ.get('PGUSER')
PGHOST = os.environ.get('PGHOST')

# Connect sql engine
engine = sqlalchemy.create_engine('postgresql://{user}:{password}@{host}/{database}'.format(
                           host = PGHOST,
                           database = PGDATABASE,
                           user = PGUSER,
                           password = PGPASSWORD))

def hash_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def populate_users_table():
    # read user table
    users = pd.read_csv('must_data/users.csv')
    # hash password
    users['password'] = users['password'].map(hash_password)
    music_preference = pd.read_csv('must_data/music_preference.csv')
    movie_preference = pd.read_csv('must_data/movie_preference.csv')
    # upload to sql
    with engine.connect() as db_conn:
        users.to_sql('users', db_conn, index=False, if_exists='append')
    with engine.connect() as db_conn:
        music_preference.to_sql('music_preference',  db_conn, index=False, if_exists='append')
    with engine.connect() as db_conn:
        movie_preference.to_sql('movie_preference', db_conn, index=False, if_exists='append')

    return True

if __name__ == "__main__":
    print(populate_users_table())

