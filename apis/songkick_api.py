import json
import os
import pdb
import pandas as pd
import requests
import sqlalchemy

from dotenv import load_dotenv, find_dotenv


# Load environment variables
load_dotenv(find_dotenv())

# Assign KEYS
SONGKICK_KEY = os.environ.get('SONGKICK_KEY')
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

# 1. Read artists names
# 2. Search for artist id
# 3. Get artist events

def create_empty_tables():
    """Creates empty csv files with specified columns"""
    # location
    location = pd.DataFrame(columns=['city_id', 'city_name', 'country'])
    location.to_csv('must_data/location.csv', index=False)

    # concerts
    concerts = pd.DataFrame(columns=['event_id', 'event_name', 'event_date',
                                    'venue', 'city_id', 'url', 'type'])
    concerts.to_csv('must_data/concerts.csv', index=False)

    # musicians
    musicians = pd.DataFrame(columns=['mu_id', 'name', 'sk_id'])
    musicians.to_csv('must_data/musicians.csv', index=False)

    # concert_performances
    concert_performances = pd.DataFrame(columns=['event_id', 'mu_id'])
    concert_performances.to_csv('must_data/concert_performances.csv', index=False)


def get_name_id(artist_name):
    """
    Given a musician name return the musician songkick id by calling Singkick
    API
    """
    url_artist = "https://api.songkick.com/api/3.0/search/" + \
                 "artists.json?apikey={api_key}&".format(api_key=SONGKICK_KEY) + \
                 "query={artist_name}".format(artist_name=artist_name)
    response_id = requests.get(url_artist)
    if(response_id.ok):
        response_id_json = json.loads(response_id.content)
        if response_id_json["resultsPage"]["results"]:
            artists_info = response_id_json["resultsPage"]["results"]["artist"]
            artist_ids = [(artist_id['id'], artist_id['displayName']) for artist_id in artists_info]
            #print(artist_ids[0])
            return artist_ids[0]
    return (None, None)


def create_concert_records(event):
    """
    Generate a new concert event on the concerts table
    """
    #print(event.keys())
    if 'metroArea' in event['venue'].keys():
        event_id = event['id']
        db_conn = engine.connect()
        result = db_conn.execute("SELECT  exists(SELECT event_id FROM concerts WHERE event_id = {})".format(event_id))
        db_conn.close()
        result = [r for r in result][0]
        if not result[0]:
            new_event = {}
            new_event['event_id'] = event_id
            new_event['event_name'] = event['displayName']
            new_event['event_date'] = event['start']['date']
            new_event['venue'] = event['venue']['displayName']
            new_event['city_id'] = create_city_record(event['venue']['metroArea'])
            new_event['url'] = event['uri']
            new_event['event_type'] = event['type']

            # Write new event record
            new_event = pd.DataFrame([new_event],
                                     columns=['event_id', 'event_name', 'event_date',
                                            'venue', 'city_id', 'url', 'event_type'])
            # Append to SQL
            db_conn = engine.connect()
            new_event.to_sql('concerts', db_conn, index=False, if_exists='append')
            db_conn.close()
            return event['id']


def create_city_record(location):
    city_id = location['id']
    db_conn = engine.connect()
    result = db_conn.execute("SELECT  exists(SELECT city_id FROM city WHERE city_id = {})".format(city_id))
    result = [r for r in result][0]
    if not result[0]:
        city_name = location['displayName']
        country = location['country']['displayName']
        #country = create_country_record(location['country']['displayName'])
        new_location = pd.DataFrame([[city_id, city_name, country]],
                                     columns = ['city_id', 'city_name', 'country'])
        new_location.to_sql('city', db_conn, index=False, if_exists='append')
    db_conn.close()
    return city_id

def create_country_record(country):
    db_conn = engine.connect()
    result = db_conn.execute("SELECT  exists(SELECT country FROM country WHERE country = '{}')".format(country))
    result = [r for r in result][0]
    if not result[0]:
        new_country = pd.DataFrame([country], columns=['country'])
        new_country.to_sql('country', db_conn, index=False, if_exists='append')
    db_conn.close()
    return country


def get_event_ids(artist_id):
    url_events = "https://api.songkick.com/api/3.0/artists/" + \
             "{artist_id}/calendar.json?apikey={api_key}".format(artist_id=artist_id,
                                                                 api_key=SONGKICK_KEY)
    response_events = requests.get(url_events)
    if (response_events.ok):
        response_events_json = json.loads(response_events.content)
        result_events = response_events_json['resultsPage']['results']
        if result_events:
            return result_events['event']


def concert_performances_record(event_id, mu_id):
    new_concert_performance = pd.DataFrame([[event_id, mu_id]],
                                          columns = ['event_id','sk_id'])
    db_conn = engine.connect()
    new_concert_performance.to_sql('concert_performances', db_conn, index=False,
            if_exists='append')
    db_conn.close()


def populate_songkick_tables(sk_id):
    # Get artist songkick id given the artist name
    # artist_id, artist_name = get_name_id(artist_name)
    # Get list of events from the artist
    events = get_event_ids(sk_id)
    if events:
        # Loop across all events
        for event in events:
            # return event id and populate table
            event_id = create_concert_records(event)
            if event_id:
                # Add a record to concert_performances table
                concert_performances_record(event_id, sk_id)
    else:
        print('No event')


if __name__ == "__main__":
    # Read artists names
    #artists_names = ['Foals']
    db_conn = engine.connect()
    results = db_conn.execute("SELECT sk_id FROM musicians")
    db_conn.close()
    sk_ids = [r[0] for r in results]
    # artists_names = open('raw_data/artists_names.csv')
    for sk_id in sk_ids:
        print(sk_id)
        populate_songkick_tables(sk_id)
