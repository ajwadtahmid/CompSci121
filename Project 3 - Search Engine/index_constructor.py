import json
import nltk
import re
import math
import sqlite3
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
        if token not in stop_words and len(token) > 1:
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


def parse_html_content(content):
    # Initialize lists to store extracted data
    meta_texts = []
    titles = []
    headings = []
    bold_texts = []
    remaining_text = []

    # Parse the HTML content
    soup = BeautifulSoup(content, 'lxml')

    # Extract meta tags
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        content = tag.get('content', '').strip()
        if content:
            meta_texts.append(content)
        tag.extract()

    # Extract title
    title_tag = soup.title
    if title_tag:
        title = title_tag.string.strip() if title_tag.string else ''
        title_tag.extract()
        titles.append(title)

    # Extract headings (h1 to h6)
    for heading_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        heading_text = heading_tag.get_text(strip=True)
        headings.append(heading_text)
        heading_tag.extract()

    # Extract bold texts (b)
    for bold_tag in soup.find_all('b'):
        bold_text = bold_tag.get_text(strip=True)
        bold_texts.append(bold_text)
        bold_tag.extract()

    # Extract remaining text
    text_elements = soup.find_all(text=True)
    for element in text_elements:
        text = element.strip()
        if text:  # Exclude empty strings
            remaining_text.append(text)

    # Join the remaining text elements into a single string
    remaining_text_str = ' '.join(remaining_text)

    return titles, headings, meta_texts, bold_texts, remaining_text_str


def build_inverted_index(bookkeeping_input, directory_path, output_file, output_file_2g):
    """
    Build the inverted index using a dictionary from the JSON data and write it to a file.
    """
    initial_index = {}
    initial_2_gram_index = {}
    json_data = load_json_data(bookkeeping_input)
    total_docs = len(json_data)
    for file_id, _ in json_data.items():
        file_path = directory_path + file_id
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            title, headings, meta_texts, bold_texts, remaining_text_str = parse_html_content(content)
            build_initial_index(title, headings, meta_texts, bold_texts, remaining_text_str, initial_index, initial_2_gram_index, file_id)
    
    final_index = calculate_tf_idf_and_sort(initial_index, total_docs)

    final_2g_index = calculate_tf_idf_and_sort(initial_2_gram_index, total_docs)

    write_inverted_index_to_file(final_index, output_file)
    write_inverted_index_to_file(final_2g_index, output_file_2g)

def build_initial_index(title, headings, meta_texts, bold_texts, remaining_text_str, initial_index, initial_2_gram_index, file_id):
    """
    Build an initial version of the index.
    """
    title_token = preprocess_text(' '.join(title))
    heading_token = preprocess_text(' '.join(headings))
    bold_meta_token = preprocess_text(' '.join(meta_texts + bold_texts))
    regular_token = preprocess_text(' '.join([remaining_text_str]))

    for token in title_token:
        initial_index.setdefault(token, []).append((file_id, 1.5))
    for token in heading_token:
        initial_index.setdefault(token, []).append((file_id, 1.15))
    for token in bold_meta_token:
        initial_index.setdefault(token, []).append((file_id, 1.05))
    for token in regular_token:
        initial_index.setdefault(token, []).append((file_id, 1))

    all_text = ' '.join(title + headings + meta_texts + bold_texts + [remaining_text_str])
    tokens = preprocess_text(all_text)

    for first, second in zip(tokens, tokens[1:]):
        key = first + " " + second
        initial_2_gram_index.setdefault(key, []).append((file_id, 1))

def calculate_tf_idf_and_sort(initial_index, total_docs):
    '''
    Function to calculate tf-idf and sort postings.
    '''
    it_idf_index = {}
    for word, doc_id_list in initial_index.items():
        it_idf_index[word] = calculate_tf_idf(doc_id_list, total_docs)

    final_index = {}
    for key, value in it_idf_index.items():
        final_index[key] = sorted(value, key=lambda x: x[1], reverse=True)

    return final_index

def calculate_tf_idf(doc_id_list, total_docs):
    """
    Calculate TF-IDF for each term in the index and add it to a list of tuple in the following format,
    ['doc_id1,score1, doc_id2,score2]
    """
    tf_idf_list = []
    n = total_docs
    doc_id_set = compress_doc_id_list(doc_id_list)
    df = len(doc_id_set)
    idf = math.log10(n / df) if df != 0 else 0
    for doc_id, score in doc_id_set:
        tf = sum(1 for d_id, _ in doc_id_list if d_id == doc_id)
        tf_idf = tf * idf
        tf_idf = score + tf_idf
        tf_idf = round(tf_idf, 3)
        tf_idf_list.append((doc_id, tf_idf))

    return tf_idf_list


def compress_doc_id_list(doc_id_list):
    doc_id_scores = {}
    for doc_id, score in doc_id_list:
        if doc_id in doc_id_scores:
            doc_id_scores[doc_id] += score
        else:
            doc_id_scores[doc_id] = score
    
    result_list = []
    for doc_id, score in doc_id_scores.items():
        result_tuple = (doc_id, score)
        result_list.append(result_tuple)
    return result_list


def write_inverted_index_to_file(inverted_index, output_file):
    """
    Write the inverted index to a text file.
    """
    with open(output_file, 'w', encoding="utf-8") as file:
        for term, postings in inverted_index.items():
            file.write(f"{term}: {postings}\n")


def write_inverted_index_to_db(inverted_index, output_db):
    """
    Write the inverted index to a SQLite DB.
    """
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS inverted_index (
                        word TEXT PRIMARY KEY,
                        doc_ids TEXT,
                        tf_idf REAL,
                    )''')

    # Insert data into the table
    for term, postings in inverted_index.items():
        for doc_ids, tf_idf in postings:
            cursor.execute("INSERT INTO inverted_index (term, doc_ids, tf_idf) VALUES (?, ?, ?)",
                           (term, doc_ids, tf_idf))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    '''
    inverted_index = {
    'car': [(1, 0.5), (2, 0.7)],
    'house': [(1, 0.6), (3, 0.8)]
    '''


    '''
    # tf-idf calc using total terms in doc
    def calculate_tf_idf(doc_id_list, directory_path, total_docs):
    tf_idf_list = []
    n = total_docs
    doc_id_set = set(doc_id_list)
    df = len(doc_id_set)
    idf = math.log10(n / df) if df != 0 else 0
    print(f"2: {idf}")
    for doc_id in doc_id_set:
        file_path = directory_path + doc_id
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            title, headings, meta_texts, bold_texts, remaining_text_str = parse_html_content(content)

            # Concatenate all the elements into a single string
            all_text = ' '.join(title + headings + meta_texts + bold_texts + [remaining_text_str])

            tokens = preprocess_text(all_text)
            total_terms = len(tokens)
            freq = doc_id_list.count(doc_id)

            tf = freq / total_terms if total_terms != 0 else 0

            tf_idf = tf * idf

            tf_idf_list.append((doc_id, tf_idf))
            print(f"3: {tf_idf}")

    return tf_idf_list
    '''
    
    '''
    def write_inverted_index_to_file_supersayain(inverted_index, output_file, gokuDict):
    data = {}
    for term, postings in inverted_index.items():
        postings_list = []
        for posting in postings:
            postings_list.append({posting: gokuDict[term][posting]})
        data[term] = postings_list

    with open(output_file, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    '''