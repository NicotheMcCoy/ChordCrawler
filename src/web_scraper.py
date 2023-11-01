from selenium.common import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from src.standardize import convert_to_roman

WINDOW_SIZE = 4


def search_song(driver, song, artist):
    """
    Search for a song by a specific artist on Ultimate Guitar and navigate to its page.

    Parameters:
    - driver (WebDriver): Selenium WebDriver object.
    - song (str): Name of the song to search for.
    - artist (str): Name of the artist of the song.

    Returns:
    - bool: True if the song was found and navigated to, False otherwise.
    """
    driver.get("https://www.ultimate-guitar.com/")
    # Wait for the search bar to load
    try:
        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
    except TimeoutException:
        return False
    # Search for the song
    search_bar.send_keys(f"{artist} {song}")
    search_bar.send_keys(Keys.ENTER)
    # Check if song exists
    if driver.find_elements(By.XPATH, "//h2[contains(text(), 'Nothing found for')]"):
        return False
    # Filter out songs that are not chords
    try:
        chords_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Chords"))
        )
    except TimeoutException:
        return False
    chords_button.click()
    # Get a list of all songs
    songs = driver.find_elements(By.XPATH, "//div[@class='LQUZJ']")
    # Filter out songs with the type "Official" or "Pro"
    filtered_songs = [song for song in songs if not any(
        bad_type in song.find_element(By.XPATH, ".//div[@class='lIKMM PdXKy']").text for bad_type in
        ["Official", "Pro"])]
    # If there are songs with ratings, select the one with the highest rating
    if filtered_songs:
        highest_rating = -1
        best_song = None
        for song in filtered_songs:
            rating_elements = song.find_elements(By.XPATH, ".//div[@class='djFV9']")
            if rating_elements:
                # Handle ratings with a comma
                rating = int(rating_elements[0].text.replace(',', ''))
                if rating > highest_rating:
                    highest_rating = rating
                    best_song = song
        if best_song:
            # Adjust the XPath to be more specific to the song link
            link = best_song.find_element(By.XPATH, ".//a[contains(@class, 'HT3w5 lBssT')]")
            driver.execute_script("arguments[0].click();", link)
        else:
            # If there are no ratings, click the only song left
            link = filtered_songs[0].find_element(By.XPATH, ".//a[contains(@class, 'HT3w5 lBssT')]")
            driver.execute_script("arguments[0].click();", link)
    else:
        return False
    if driver.find_elements(By.XPATH, "//h1[contains(text(), 'Sorry, this artist')]"):
        return False
    return True


def parse_chords(driver):
    """
       Parse the chords of a song from the current page of the provided WebDriver.

       Parameters:
       - driver (WebDriver): Selenium WebDriver object positioned on a song page.

       Returns:
       - list: List of chord sequences in Roman numeral notation.
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body = soup.find('pre', attrs={'class': 'tK8GG Ty_RP'})
    chords_elements = body.find_all('span', attrs={'data-name': True})
    chords = [item.get_text().strip() for item in chords_elements]
    sequences = [tuple(chords[i:i + WINDOW_SIZE]) for i in range(len(chords) - WINDOW_SIZE + 1)]
    sequences = list(dict.fromkeys(sequences))
    filtered_sequences = []
    for seq in sequences:
        valid = True
        for chord in seq:
            if seq.count(chord) > 2 or (chord, chord) in zip(seq, seq[1:]):
                valid = False
                break
        if valid:
            filtered_sequences.append(seq)
    roman_numeral_sequences = [tuple(convert_to_roman(list(seq)).split('-')) for seq in sequences]
    return roman_numeral_sequences
