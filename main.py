import logging
import time
from tqdm import tqdm
from src.standardize import transposer
from src.utilities import create_driver, write_csv, get_existing_songs, get_user_preference
from src.web_scraper import search_song, parse_chords

logging.basicConfig(filename='log/scraping.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """
    Main function to orchestrate the process of scraping song data.

    The function performs the following steps:
    1. Prompt the user for a genre and delay, then validates each input.
    2. Optionally fetch new songs from Spotify based on the genre.
    3. Initialize a Selenium WebDriver.
    4. Iterate over the songs, searching for each song on Ultimate Guitar.
    5. Transpose the song to C Major and parse its chords into roman numeral notation.
    6. Save the song data to a CSV file.
    7. Handle exceptions and log errors or information as needed.
    8. Close the WebDriver upon completion.

    Note: The function uses various helper functions from other modules to perform specific tasks.
    """
    # Fetch songs from Spotify based on genre
    preference = get_user_preference()
    songs = preference["songs"]
    genre = preference["genre"]
    delay = preference["delay"]

    # Get existing songs from (genre)_database.csv
    existing_songs = get_existing_songs(genre)
    # Initialize the WebDriver
    driver = create_driver()
    try:
        for song in tqdm(songs, desc=f"Scraping {genre} songs", unit="song"):
            # Get song data from spotify_songs_(genre).csv
            song_name = song['song_name']
            artist = song['artist']
            # Skip the song if it already exists in (genre)_database.csv
            if (song_name, artist) in existing_songs:
                logging.info(f"Song '{song_name}' by {artist} already exists in 'data/{genre}_database.csv'.")
                continue
            key = int(song['key'])
            mode = int(song['mode'])
            try:
                # Search for the song on Ultimate Guitar
                song_found = search_song(driver, song_name, artist)
                if not song_found:
                    logging.info(f"Song '{song_name}' by {artist} not available on Ultimate Guitar!")
                    continue
                # Wait set time before transposing/parsing the song
                time.sleep(delay)
                # Transpose the song to C Major
                transposed = transposer(driver, key, mode)
                if not transposed:
                    logging.error(f"Song '{song_name}' by {artist} could not be transposed!")
                    continue
                # Parse chords from the song
                progression = parse_chords(driver)
                song_data = {
                    'song_name': song_name,
                    'artist': artist,
                    'key': key,
                    'mode': mode,
                    'progression': progression
                }
                # Write song data to (genre)_database.csv
                write_csv(song_data, genre)
                existing_songs.add((song_name, artist))
                logging.info(f"Song '{song_name}' by {artist} has been saved to 'data/{genre}_database.csv'.")
                # Wait set time before scraping the next song
                time.sleep(delay)
            except Exception as e:
                logging.error(f"Error processing song '{song_name}' by {artist}: {e}")
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected!")
    finally:
        # Close the WebDriver
        logging.info("All songs have been scraped!")
        driver.close()


if __name__ == "__main__":
    main()
