import http.client
import json
import pandas as pd

import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Assign KEYS
TMDB_KEY = os.environ.get('TMDB_KEY')

def create_empty_tables():
    """Creates empty csv files with specified columns"""
    
    # Movie artists catalog
    movie_artists = pd.DataFrame(columns=['mo_id', 'name'])
    movie_artists.to_csv('must_data/movie_artists.csv', index=False)

def get_popular_movie_artists():
    """Get the most popular artist objects from The Movie Database"""
    
    movie_artists = list()
    for page in range(1,41):
        movie_artists.append(get_popular_movie_artists_page(page))
    movie_artists = [movie_artist for page in movie_artists for movie_artist in page]
    return(movie_artists)    

def get_popular_movie_artists_page(page):
    """Get popular artist objects from The Movie Database, for a given page"""
    
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    popular_url = "/3/person/popular?page=" + str(page) + "&language=en-US&region=US&api_key=" + TMDB_KEY
    conn.request("GET", popular_url, payload)
    res = conn.getresponse()
    popular_data = res.read()
    popular_dict = json.loads(popular_data.decode('utf-8'))
    movie_artists = popular_dict['results']
    return(movie_artists)

def create_popular_movie_artists_record(movie_artist):
    """
    Generate popular movie artist row, with its corresponding TMDB_id
    """
    
    popular_movie_artist = {}
    popular_movie_artist['mo_id'] = movie_artist['id']
    popular_movie_artist['name'] = movie_artist['name'] 

    # Write a new music_release record
    popular_movie_artist = pd.DataFrame([popular_movie_artist], columns=['mo_id', 'name'])
    popular_movie_artist.to_csv('must_data/movie_artists.csv', mode='a', index=False, header=False)

def populate_movie_artists_table():
    """
    Populate the catalog of famous actors/actress/directors
    """
    
    movie_artists = get_popular_movie_artists()
    if movie_artists:
        # Loop across all events
        for movie_artist in movie_artists:
            create_popular_movie_artists_record(movie_artist)
    else:
        print('No popular movie_artists')
