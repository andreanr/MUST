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


def create_authorized_spotify_object():
    """
    Generate a spotipy object with the authorized credentials to make requests
    """
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                          client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return(sp)

def create_popular_musician_record(musician_name):
    results = sp.search(q='artist:' + musician_name, type='artist')
    
    if len(results['artists']['items']) > 0:
        musician = results['artists']['items'][0]

        popular_musician = {}
        popular_musician['sp_id'] = musician['id']
        popular_musician['name'] = musician['name']

        popular_musician = pd.DataFrame([popular_musician], columns=['sp_id', 'name'])
        #popular_musician.to_csv('must_data/musicians.csv', mode='a', index=False, header=False)
        db_conn = engine.connect()
        popular_musician.to_sql('musicians', db_conn, index=False, if_exists='append')
        db_conn.close()
    
def populate_musicians_table(musicians_names):
    """
    Populate the catalog of famous actors/actress/directors
    """
    sp = create_authorized_spotify_object()
    if musicians_names:
        # Loop across all events
        for musician_name in musicians_names:
            create_popular_musician_record(musician_name)
    else:
        print('No popular musicians')

        
if __name__ == "__main__":
    musicians_names = list(pd.read_csv('artists_names.csv', header=None)[0].values)
    populate_musicians_table(musicians_names)
