import csv
import logging
import traceback
import random
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from src.spotify_api import fetch_songs


def read_csv(filename):
    """
    Read data from a CSV file and return it as a list of dictionaries.

    Parameters:
    - filename (str): Path to the CSV file to be read.

    Returns:
    - list: List of dictionaries containing song details.
    """
    songs = []
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                songs.append(row)
        return songs
    except FileNotFoundError:
        logging.error("Directory not found!")
        return []
    except PermissionError:
        logging.error("Permission denied!")
        return []
    except UnicodeEncodeError as e:
        logging.error(f"Encoding error: {e}")
        return []


def write_csv(song_data, genre):
    """
    Write song data to a CSV file based on genre.

    Parameters:
    - song_data (dict): Dictionary containing song details.
    - genre (str): Genre of the song.
    """
    filename = f'output/{genre}_database.csv'
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([song_data['song_name'], song_data['artist'], song_data['key'], song_data['mode'],
                             song_data['progression']])
    except FileNotFoundError:
        logging.warning("Directory not found!")
    except PermissionError:
        logging.error("Permission denied!")
    except UnicodeEncodeError as e:
        logging.error(f"Encoding error: {e}")


def get_user_preference():
    """
    Prompt the user for various preferences including genre, delay, and song fetching options.

    Returns:
    - dict: A dictionary containing the user's preferences including songs, genre, and delay.
    """
    # Get genre input from the user
    while True:
        genre = input("Enter the genre you want to scrape songs for (e.g., 'pop'): ")
        if valid_genre(genre):
            break
        logging.error("Invalid genre! Please try again.")
    # Get delay input from the user
    while True:
        try:
            delay = int(input("Enter the delay between songs (in seconds): "))
            if delay >= 0:
                break
            logging.error("Delay must be a positive integer, please try again.")
        except ValueError:
            logging.error("Please enter a valid number.")
    # Get song input depending on user preference
    if input("Do you want to fetch new songs from Spotify? (yes/no): ").strip().lower() == 'yes':
        while True:
            try:
                num_songs = int(input("How many songs do you want to fetch? "))
                if num_songs > 0:
                    break
                logging.error("Please enter a positive integer.")
            except ValueError:
                logging.error("Please enter a valid number.")
        # Get user input for year range
        while True:
            year_range = input("Enter the year range (e.g., 2010-2020): ")
            try:
                start_year, end_year = map(int, year_range.split('-'))
                if start_year < end_year:
                    break
            except ValueError:
                logging.error("Please enter a valid year range.")
        songs = fetch_songs(genre, num_songs, start_year, end_year)
    else:
        songs = read_csv(f'./output/spotify_songs_{genre}.csv')
    return {
        "songs": songs,
        "genre": genre,
        "delay": delay
    }


def read_file(filename):
    """
    Read a file and return its lines as a list.

    Parameters:
    - filename (str): Path to the file to be read.

    Returns:
    - list: List of lines from the file.
    """
    with open(filename, mode='r', encoding='utf-8') as file:
        return list(line.strip() for line in file)


def create_driver():
    """
    Initialize and return a Selenium WebDriver with specific configurations.

    Returns:
    - WebDriver: Selenium WebDriver object.
    """
    proxy = ""
    user_agent = random.choice(read_file('./config/user_agents.txt'))
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Uncomment the following lines if you want to use a proxy and/or a specific user agent
    # chrome_options.add_argument(f"user-agent={user_agent}")
    # chrome_options.add_argument(f"--proxy-server={proxy}")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except WebDriverException as e:
        logging.error(f"Error initializing WebDriver: {e}")
        logging.error(traceback.format_exc())
        return None


def valid_genre(genre):
    """
    Check if the provided genre is valid based on a predefined list.

    Parameters:
    - genre (str): Genre to be checked.

    Returns:
    - bool: True if genre is valid, False otherwise.
    """
    genres = read_file('./config/genres.txt')
    return genre.lower() in genres


def get_existing_songs(genre):
    """
    Retrieve existing songs from a CSV file based on genre.

    Parameters:
    - genre (str): Genre of songs to retrieve.

    Returns:
    - set: Set of tuples containing song_name and artist.
    """
    try:
        existing_songs = read_csv(f'./output/{genre}_database.csv')
        return {(song['song_name'], song['artist']) for song in existing_songs}
    except FileNotFoundError:
        logging.warning("Directory not found, returning empty set!")
        return set()