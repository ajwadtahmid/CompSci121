import json
import nltk
import re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords, words
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('words')

def preprocess_text(content):
    """
    Tokenize the content using NLTK, remove stopwords, perform lemmatization,
    and filter out terms not present in NLTK's word corpus.
    """
    tokens = re.split(r'[^a-zA-Z]', content.lower())
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = []
    english_words = set(words.words())
    # Lemmatize known words, otherwise add them as they are
    for token in tokens:
        if token not in stop_words:
            if token in english_words:
                lemmatized_tokens.append(lemmatizer.lemmatize(token))
            else:
                lemmatized_tokens.append(token)
    return lemmatized_tokens


def load_json_data(bookkeeping_input):
    """
    Load JSON data from the specified file path.
    """
    with open(bookkeeping_input, "r", encoding="utf-8") as json_file:
        return json.load(json_file)

def exclude_tags(tag):
    return tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title']

def build_inverted_index(bookkeeping_input, directory_path, output_file):
    """
    Build the inverted index using a dictionary from the JSON data and write it to a file.
    """
    inverted_index = {}
    json_data = load_json_data(bookkeeping_input)
    for file_id, _ in json_data.items():
        file_path = directory_path + file_id
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            # Create a BeautifulSoup object
            soup = BeautifulSoup(content, 'html.parser')

            # Store the text content of the title
            title_text = soup.title.text if soup.title else None

            # Extract and remove the title element from the HTML document
            if soup.title:
                soup.title.extract()
            
            # Store the text content of all heading elements (h1, h2, h3) in one list
            headings_text = [heading.text for heading in soup.find_all(['h1', 'h2', 'h3'])] if soup.find_all(['h1', 'h2', 'h3']) else []

            # Extract and remove all heading elements from the HTML document
            for tag_name in ['h1', 'h2', 'h3']:
                for tag in soup.find_all(tag_name):
                    tag.extract()
            
            # Extract text content of all bold elements and store in bold_texts
            bold_texts = [bold.text for bold in soup.find_all('b')] if soup.find_all('b') else []
            # Remove all bold elements from the HTML document
            for bold in soup.find_all('b'):
                bold.extract()
            
            # Get all the remaining text content without tags
            html_content = soup.get_text()
            
            print(f"{headings_text}\n{title_text}\n{bold_texts}\n{html_content}")

            extracted_text = ' '.join(extracted_text_parts)

            tokens = preprocess_text(extracted_text)
            for token in tokens:
                inverted_index.setdefault(token, []).append(file_id)

    write_inverted_index_to_file(inverted_index, output_file)

def write_inverted_index_to_file(inverted_index, output_file):
    """
    Write the inverted index to a file.
    """
    with open(output_file, 'w', encoding="utf-8") as file:
        for term, postings in inverted_index.items():
            file.write(f"{term}: {postings}\n")