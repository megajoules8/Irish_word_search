import string
import requests
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import streamlit as st

# Normalize function to remove accents
def normalize_string(input_str: str) -> str:
    return ''.join(
        char for char in unicodedata.normalize('NFD', input_str)
        if unicodedata.category(char) != 'Mn'
    )

# Function to get words starting with a given letter
def get_words_starting_with(letter: str) -> list:
    try:
        result = requests.get(f"https://www.teanglann.ie/en/fgb/_{letter}")
        result.raise_for_status()
    except requests.exceptions.HTTPError as e:
        st.warning(f"Failed to fetch words for letter '{letter}': {e}")
        return []
    soup = BeautifulSoup(result.content, "html.parser")
    samples = soup.find_all("span", class_="abcItem")
    words = [(sample.a.text, f"https://www.teanglann.ie/en/fgb/{sample.a.text}") for sample in samples]
    return words

# Function to get all words from Teanglann.ie
def get_all_words() -> list:
    all_words = []
    for letter in string.ascii_lowercase:
        words = get_words_starting_with(letter)
        all_words.extend(words)
    return all_words

# Function to filter words based on search criteria
def filter_words(words: list, substring: str, search_type: str) -> list:
    normalized_substring = normalize_string(substring)
    if search_type == 'begins':
        return [(word, link) for word, link in words if normalize_string(word).startswith(normalized_substring)]
    elif search_type == 'ends':
        return [(word, link) for word, link in words if normalize_string(word).endswith(normalized_substring)]
    elif search_type == 'contains':
        return [(word, link) for word, link in words if normalized_substring in normalize_string(word)]
    else:
        raise ValueError("Invalid search_type. Choose from 'begins', 'ends', or 'contains'.")

# Streamlit UI
st.title("Irish Words Search")
substring = st.text_input("Enter substring to search for:")
search_type = st.selectbox("Search type:", ['begins', 'ends', 'contains'])

if st.button("Search"):
    all_words = get_all_words()
    filtered_words = filter_words(all_words, substring, search_type)
    df = pd.DataFrame(filtered_words, columns=['Word', 'Link'])
    df['Link'] = df['Link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
    st.write(df.to_html(escape=False), unsafe_allow_html=True)
