import re
from index_constructor import load_json_data
from ast import literal_eval

def get_links_from_index(word):
    """
    Extracts document IDs from the inverted index file.
    """
    doc_id_set = set()
    if len(word) == 1:
        with open("inverted_index.txt", "r", encoding="utf-8") as file:
            for _, line in enumerate(file, start=1):
                if re.search(r'\b' + re.escape(word) + r'\b', line):
                    _, values = line.split(":")
                    tuple_list = literal_eval(values)  # Convert string representation to list of tuples
                    for tuple_item in tuple_list:
                        doc_id_set.add(tuple_item[0])
    else:
        with open("inverted_index_2g.txt", "r", encoding="utf-8") as file:
            for _, line in enumerate(file, start=1):
                if re.search(r'\b' + re.escape(word) + r'\b', line):
                    _, values = line.split(":")
                    tuple_list = literal_eval(values)  # Convert string representation to list of tuples
                    for tuple_item in tuple_list:
                        doc_id_set.add(tuple_item[0])
    return doc_id_set

def display_results(doc_id_set, bookkeeping_input):
    """
    Displays the results based on the document IDs found in the inverted index.
    """
    if not doc_id_set:
        print("No results found.")
        return

    print("Total number of URLs found:", len(doc_id_set))
    json_data = load_json_data(bookkeeping_input)
    for i in range(min(len(doc_id_set), 20)):
        value = list(doc_id_set)[i]
        print(f"{i + 1}: {json_data[value]}")

def query(word, bookkeeping_input):
    """
    Performs a query and displays the results.
    """
    doc_id_set = get_links_from_index(word)
    display_results(doc_id_set, bookkeeping_input)