import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Assign KEYS
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

# PostgreSQL credentials
PGDATABASE = os.environ.get('PGDATABASE')
PGPASSWORD = os.environ.get('PGPASSWORD')
PGUSER = os.environ.get('PGUSER')
PGHOST = os.environ.get('PGHOST')

engine = sqlalchemy.create_engine('postgresql://{user}:{password}@{host}/{database}'.format(
                                  host = PGHOST,
                                  database = PGDATABASE,
                                  user = PGUSER,
                                  password = PGPASSWORD))

# 1. Get the data from Spotify
# 2. Populate our tables


def create_authorized_spotify_object():
    """
    Generate a spotipy object with the authorized credentials to make requests
    """
    
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                          client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return(sp)

def get_last_week_music_releases(sp, country='US', limit=50):
    """
    Get the [limit] most relevant releases on the last week for the given [country]
    """
    music_releases_dict = sp.new_releases(country=country, limit=limit)
    music_releases = music_releases_dict['albums']['items']
    return(music_releases)

def create_music_release_record(music_release):
    """
    Generate a new music release on the new_music table
    """
    new_music_release = {}
    new_music_release['release_id'] = music_release['id']
    new_music_release['release_date'] = music_release['release_date']
    new_music_release['name'] = music_release['name']
    new_music_release['album_type'] = music_release['album_type']
    new_music_release['url'] = music_release['external_urls']['spotify']

    # Write a new music_release record
    new_music_release = pd.DataFrame([new_music_release],
                             columns=['release_id', 'release_date', 'name', 'album_type', 'url'])
    
    # new_music_release.to_csv('must_data/new_music.csv', mode='a', index=False, header=False)
    db_conn = engine.connect()
    new_music_release.to_sql('new_music', db_conn, index=False, if_exists='append')
    db_conn.close()

def create_musician_release_records(music_release):
    """
    Generate a tuple on the music_releases table for every musician that participates in a new release
    """
    musicians = [musician['id'] for musician in music_release['artists']]
    music_releases = pd.DataFrame({'release_id': music_release['id'], 'mu_id': musicians})
    
    # music_releases.to_csv('must_data/music_releases.csv', mode='a', index=False, header=False)
    db_conn = engine.connect()
    music_releases.to_sql('music_releases', db_conn, index=False, if_exists='append')
    db_conn.close()
    
def create_location_release_records(music_release):
    """
    Generate a tuple on the available_music table for each country where a new release is available
    """
    countries = music_release['available_markets']
    available_music = pd.DataFrame({'release_id': music_release['id'], 'country': countries})
    
    #available_music.to_csv('must_data/available_music.csv', mode='a', index=False, header=False)
    db_conn = engine.connect()
    available_music.to_sql('available_music', db_conn, index=False, if_exists='append')
    db_conn.close()

def populate_all_music_release_tables():
    """
    Populate all the tables related to the music releases of the last week 
    """
    sp = create_authorized_spotify_object()
    music_releases = get_last_week_music_releases(sp)
    if music_releases:
        # Loop across all events
        for music_release in music_releases:
            # return event id and populate table
            create_music_release_record(music_release)
            create_musician_release_records(music_release)
            create_location_release_records(music_release)
    else:
        print('No music releases')

if __name__ == "__main__":
    populate_all_music_release_tables()
