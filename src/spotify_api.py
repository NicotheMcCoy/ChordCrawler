import os
import csv
import spotipy
import logging
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables for Spotify API credentials
load_dotenv()


def get_spotify_client():
    """
    Initialize and return a Spotify client using the provided credentials.

    Returns:
    - spotipy.Spotify: Initialized Spotify client.
    """
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


def fetch_songs(genre, num_songs, start_year, end_year):
    """
    Fetch songs from Spotify based on the provided genre.

    Parameters:
    - genre (str): The genre of songs to fetch.

    Returns:
    - list: List of dictionaries containing song details.
    """
    sp = get_spotify_client()
    songs = []
    full_pages = num_songs // 50  # Number of full pages
    remaining_songs = num_songs % 50  # Songs on the last page
    offset = 0

    try:
        # Fetch full pages of songs
        for _ in range(full_pages):
            results = sp.search(q=f'genre:"{genre}" year:{start_year}-{end_year}',
                                market='US', type='track', limit=50, offset=offset)
            # Process results and update offset
            songs.extend(process_results(results, sp))
            offset += 50

        # Fetch remaining songs
        if remaining_songs > 0:
            results = sp.search(q=f'genre:"{genre}" year:{start_year}-{end_year}',
                                market='US', type='track', limit=remaining_songs, offset=offset)
            songs.extend(process_results(results, sp))

        # Save songs to spotify_songs_(genre).csv
        spotify_save(songs, genre)
        logging.info(f"Saved {len(songs)} songs to 'spotify_songs_{genre}.csv'.")
        return songs
    except FileNotFoundError:
        logging.error("Directory not found!")
    except PermissionError:
        logging.error("Permission denied!")
    except UnicodeEncodeError as e:
        logging.error(f"Encoding error: {e}")


def process_results(results, sp):
    """Process the results from the Spotify search and return a list of song details."""
    songs = []
    fetched_songs = results['tracks']['items']
    for track in fetched_songs:
        track_id = track['id']
        features = sp.audio_features([track_id])[0]
        if features:
            key = features['key']
            mode = features['mode']
            songs.append(
                {'artist': track['artists'][0]['name'],
                 'song_name': track['name'], 'key': key, 'mode': mode})
    return songs


def spotify_save(songs, genre):
    """
    Save song details to a CSV file named 'spotify_songs_(genre).csv'.

    Parameters:
    - songs (list): List of dictionaries containing song details.
    - genre (str): Genre of the songs.
    """
    try:
        with open(f'data/spotify_songs_{genre}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['artist', 'song_name', 'key', 'mode']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for song in songs:
                writer.writerow(song)
    except FileNotFoundError:
        logging.error("Directory not found!")
    except PermissionError:
        logging.error("Permission denied!")
    except UnicodeEncodeError as e:
        logging.error(f"Encoding error: {e}")