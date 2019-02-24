import json
import os
import pandas as pd
import requests

from dotenv import load_dotenv, find_dotenv


# Load environment variables
load_dotenv(find_dotenv())

# Assign KEYS
SONGKICK_KEY = os.environ.get('SONGKICK_KEY')


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
        artists_info = response_id_json["resultsPage"]["results"]["artist"]
        artist_ids = [(artist_id['id'], artist_id['displayName']) for artist_id in artists_info]
        return artist_ids[0]


def create_concert_records(event):
    """
    Generate a new concert event on the concerts table
    """
    new_event = {}
    new_event['event_id'] = event['id']
    new_event['event_name'] = event['displayName']
    new_event['event_date'] = event['start']['datetime']
    new_event['venue'] = event['venue']['displayName']
    new_event['city_id'] = create_location_record(event['location']['city'])
    new_event['url'] = event['uri']
    new_event['type'] = event['type']

    # Write new event record
    new_event = pd.DataFrame([new_event],
                             columns=['event_id', 'event_name', 'event_date',
                                    'venue', 'city_id', 'url', 'type'])
    new_event.to_csv('must_data/concerts.csv', mode='a',
                     index=False, header=False)
    return event['id']


def create_location_record(city_country_name):
    # Split name into "City, St" and "Country"
    city_name = ",".join(city_country_name.split(',')[:-1])
    country = city_country_name.split(',')[-1].strip()
    # Read location table
    location = pd.read_csv('must_data/location.csv')
    # Check if city_name exists
    check = location[(location['city_name'] == city_name) &
                     (location['country'] == country)]
    # If exits return city_id
    if len(check) > 0:
        city_id = check['city_id'][0]
    # If not generate a new location record
    else:
        city_id = len(location)
        new_location = pd.DataFrame([[city_id, city_name, country]],
                                     columns = ['city_id', 'city_name', 'country'])
        new_location.to_csv('must_data/location.csv', mode='a',
                            index=False, header=False)
    return city_id


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


def create_musician_record(artist_id, artist_name):
    # Read musician table
    musicians = pd.read_csv('must_data/musicians.csv')
    # Check if the musician already exists
    check = musicians[(musicians['sk_id'] == artist_id) &
                     (musicians['name'] == artist_name)]
    if len(check) > 0:
        mu_id = check.index[0]
    else:
        mu_id = len(musicians)
        new_musician = pd.DataFrame([[mu_id, artist_name, artist_id]],
                                     columns = ['mu_id', 'name', 'sk_id'])
        new_musician.to_csv('must_data/musicians.csv', mode='a',
                            index=False, header=False)
    return mu_id


def concert_performances_record(event_id, mu_id):
    new_concert_performance = pd.DataFrame([[event_id, mu_id]],
                                          columns = ['event_id','mu_id'])
    new_concert_performance.to_csv('must_data/concert_performances.csv',
                                  mode='a', index=False, header=False)


def populate_all_concert_tables(artist_name):
    # Get artist songkick id given the artist name
    artist_id, artist_name = get_name_id(artist_name)
    # Make a new record on musician artist if not exists
    create_musician_record(artist_id, artist_name)
    print(artist_id, artist_name)
    # Get list of events from the artist
    events = get_event_ids(artist_id)
    if events:
        # Loop across all events
        for event in events:
            # return event id and populate table
            event_id = create_concert_records(event)
            # Get list of performances by the event
            performances = event['performance']
            artists_ids = [(p['artist']['id'], p['artist']['displayName']) for p in  performances]
            for artist_id, artist_name in artists_ids:
                # Create a new artist record or get mu_id of existing one
                mu_id = create_musician_record(artist_id, artist_name)
                # Add a record to concert_performances table
                concert_performances_record(event_id, mu_id)
    else:
        print('No event')


if __name__ == "__main__":
    # Create empty csv files
    create_empty_tables()
    # Read artists names
    artists_names = open('raw_data/artists_names.csv')
    for artist_name in artists_names:
        try:
            populate_all_concert_tables(artist_name)
        except:
            pass
