from selenium.webdriver.common.by import By
import re
import logging


def transposer(driver, key, mode):
    """
    Transpose the chords of a song to the key of C using the Ultimate Guitar website's transpose feature.

    Parameters:
    - driver (WebDriver): Selenium WebDriver object positioned on a song page.
    - key (int): Key of the song (0-11, where 0 is C, 1 is C#/Db, etc.).
    - mode (int): Mode of the song (0 for minor, 1 for major).

    Returns:
    - bool: True if the transposition was successful, False otherwise.
    """
    capo_row = driver.find_elements(By.XPATH, "//th[text()='Capo: ']/following-sibling::td/span")
    capo_text = capo_row[0].text
    if capo_text:
        if capo_text == 'no capo':
            capo = 0
        else:
            capo = int(re.search(r'\d+', capo_text).group())
    else:
        capo = 0
        logging.warning("Capo not found! Defaulting to 0.")
    # Get transpose buttons
    transpose_down = driver.find_element(By.XPATH, "//span[contains(text(), 'Transpose')]//following-sibling"
                                                   "::span//button[span[text()='−1']]")
    transpose_up = driver.find_element(By.XPATH, "//span[contains(text(), 'Transpose')]//following-sibling"
                                                 "::span//button[span[text()='+1']]")
    # Transpose up three half steps if the song is in minor
    if mode == 0:
        key = (key + 3) % 12
    # Transpose up by the capo
    if capo != 0:
        key = (key + capo) % 12
    # Transpose to C Major
    if key in [6, 7, 8, 9, 10, 11]:
        while key != 0:
            key = (key + 1) % 12
            transpose_up.click()
    elif key in [1, 2, 3, 4, 5]:
        while key != 0:
            key = (key - 1) % 12
            transpose_down.click()
    return True


def convert_to_roman(chords):
    """
    Convert a list of chords to Roman numeral notation based on the key of C.

    Parameters:
    - chords (list): List of chord names.

    Returns:
    - str: String of chords in Roman numeral notation separated by hyphens.
    """
    # Define the diatonic chords and their Roman numerals in C major
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
    all_roots = ["C", "D", "E", "F", "G", "A", "B", "C#", "D#", "F#", "G#", "A#", "Db", "Eb", "Gb", "Ab", "Bb"]

    output = []

    for chord in chords:
        # Handle slash chords by removing the bass note
        if '/' in chord:
            chord = chord.split('/')[0]

        # Extract the root, sharp/flat, and type of the chord
        root = chord[0]  # First character is always part of the root
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root += chord[1]
            chord_type = chord[2:]
        else:
            chord_type = chord[1:]

        # Convert the root to Roman numeral
        try:
            index = all_roots.index(root)
            roman_chord = roman_numerals[index % 7]
            chord_type = chord_type.lower()
            # Handle common chord types
            if 'maj' in chord_type:
                pass  # Major chords are already uppercase
            elif 'dim' in chord_type:
                roman_chord += "°"  # Diminished chords are represented with a degree symbol
            elif 'aug' in chord_type:
                roman_chord += "+"  # Augmented chords are represented with a plus symbol
            elif 'm' in chord_type or 'min' in chord_type:
                roman_chord = roman_chord.lower()
            # Append the rest of the chord type (like 7sus4, 7add9, etc.)
            roman_chord += chord_type.replace('maj', '').replace('min', '').replace('dim', '').replace('m', '')
            output.append(roman_chord)
        except ValueError:
            output.append(f"Chord {chord} not recognized")
    return '-'.join(output)
