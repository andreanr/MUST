import spotipy
import requests
import json
import re
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import sqlalchemy

import os
from dotenv import load_dotenv, find_dotenv


# Load environment variables
load_dotenv(find_dotenv())


# Assign KEYS
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SONGKICK_KEY = os.environ.get('SONGKICK_KEY')
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


def create_empty_tables():
    """Creates empty csv files with specified columns"""

    # Musicians catalog
    musicians = pd.DataFrame(columns=['sp_id', 'name'])
    musicians.to_csv('must_data/musicians.csv', index=False)

def create_authorized_spotify_object():
    """
    Generate a spotipy object with the authorized credentials to make requests
    """
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                          client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return(sp)

def get_songkick_id(musician_name):
    """
    Given a musician name return the musician songkick id by calling Singkick
    API
    """
    url_artist = "https://api.songkick.com/api/3.0/search/" + \
                 "artists.json?apikey={api_key}&".format(api_key=SONGKICK_KEY) + \
                 "query={artist_name}".format(artist_name=musician_name)
    response_id = requests.get(url_artist)
    if(response_id.ok):
        response_id_json = json.loads(response_id.content)
        if response_id_json["resultsPage"]["results"]:
            artists_info = response_id_json["resultsPage"]["results"]["artist"]
            artist_ids = [(artist_id['id'], artist_id['displayName']) for artist_id in artists_info]
            print(artist_ids[0])
            return artist_ids[0]
    return (None, None)

def clean_name(name):
    return re.sub('[!@#$.-]', ' ', name.strip().lower())

def get_spotify_id(musician_name, sp):
    results = sp.search(q='artist:' + '"{}"'.format(musician_name), type='artist')

    if len(results['artists']['items']) > 0:
        musician = results['artists']['items'][0]

        sp_id = musician['id']
        spotify_name = musician['name']
        if clean_name(musician_name) == clean_name(spotify_name):
            return sp_id


def create_musician_record(musician_name, sp):
    sk_id, new_musician_name = get_songkick_id(musician_name)
    if sk_id:
        db_conn = engine.connect()
        result = db_conn.execute("SELECT exists(SELECT sk_id FROM musicians WHERE sk_id= '{}')".format(sk_id))
        result = [r for r in result][0]
        if not result[0]:
            sp_id = get_spotify_id(new_musician_name, sp)
            if sp_id:
                print('yes')
                new_musician = pd.DataFrame([[sp_id, sk_id, new_musician_name]],
                                         columns = ['sp_id', 'sk_id', 'name'])
                db_conn = engine.connect()
                new_musician.to_sql('musicians', db_conn, index=False, if_exists='append')
                db_conn.close()


def populate_musicians_table(musicians_names):
    """
    Populate the catalog of famous actors/actress/directors
    """
    sp = create_authorized_spotify_object()
    if musicians_names:
        # Loop across all events
        for musician_name in musicians_names:
            create_musician_record(musician_name, sp)
    else:
        print('No popular musicians')

if __name__ == "__main__":
    musicians_names = open('raw_data/artists_names.csv')
    populate_musicians_table(musicians_names)

