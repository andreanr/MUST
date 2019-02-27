import http.client
import json
import pandas as pd

import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Assign KEYS
TMDB_KEY = os.environ.get('TMDB_KEY')

# 1. Get upcoming films
# 2. Get the cast of those films
# 3. Populate tables

def create_empty_tables():
    """Creates empty csv files with specified columns"""
    
    # New films
    new_films = pd.DataFrame(columns=['mdb_id', 'release_date', 'title', 'description', 'url'])
    new_films.to_csv('must_data/new_films.csv', index=False)
    
    # Link between films and movie artists
    movie_releases = pd.DataFrame(columns=['mo_id', 'mdb_id'])
    movie_releases.to_csv('must_data/movie_releases.csv', index=False)


def get_upcoming_films():
    """
    Get the 20 most relevant upcoming films from TheMovieDataBase API
    """
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    upcoming_url = "/3/movie/upcoming?page=1&language=en-US&region=US&api_key=" + TMDB_KEY
    conn.request("GET", upcoming_url, payload)
    res = conn.getresponse()
    upcoming_data = res.read()
    upcoming_dict = json.loads(upcoming_data.decode('utf-8'))
    films = upcoming_dict['results']
    return(films)


def get_upcoming_film_cast(movie_id):
    """
    Get the cast of every upcoming film, taken from TheMovieDataBase API
    """
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    upcoming_url = "/3/movie/" + str(movie_id) + "/credits?api_key=" + TMDB_KEY
    conn.request("GET", upcoming_url, payload)
    res = conn.getresponse()
    upcoming_cast_data = res.read()
    cast = json.loads(upcoming_cast_data.decode('utf-8'))
    return(cast)

    
def create_upcoming_film_record(film):
    """
    Generate an upcoming film on the new_films table
    """
    upcoming_film = {}
    upcoming_film['mdb_id'] = film['id']
    upcoming_film['release_date'] = film['release_date'] 
    upcoming_film['title'] = film['title']
    upcoming_film['description'] = film['overview']
    upcoming_film['url'] = 'https://www.themoviedb.org/movie/' + str(film['id'])

    # Write a new music_release record
    upcoming_film = pd.DataFrame([upcoming_film],
                             columns=['mdb_id', 'release_date', 'title', 'description', 'url'])
    upcoming_film.to_csv('must_data/new_films.csv', mode='a',
                         index=False, header=False)

    
def create_upcoming_film_artists_records(movie_id):
    """
    Generate a tuple on the movie_releases table for every actress/actor and director that participates in 
    an upcoming film
    """
    cast = get_upcoming_film_cast(movie_id)
    actors = [actress['id'] for actress in cast['cast']]
    directors = [member['id'] for member in cast['crew'] if member['job'] == 'Director']
    movie_artists = actors + directors
    movie_releases = pd.DataFrame({'mo_id': movie_artists, 'mdb_id': cast['id']})
    movie_releases.to_csv('must_data/movie_releases.csv', mode='a',
                          index=False, header=False)


def populate_all_upcoming_films_tables():
    """
    Populate all the tables related to the upcoming films
    """
    films = get_upcoming_films()
    if films:
        # Loop across all events
        for film in films:
            create_upcoming_film_record(film)
            create_upcoming_film_artists_records(film['id'])
    else:
        print('No upcoming films')