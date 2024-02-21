from index_constructor import build_inverted_index, load_json_data
from basic_query import query
import time

# bookkeeping_input = "test/test.json"
# directory_path = "test/"
bookkeeping_input = "webpages_raw/bookkeeping.json"
directory_path = "webpages_raw/"
output_file = "inverted_index.txt"
output_file_2g = "inverted_index_2g.txt"
# output_file = "inverted_index.db"
# output_file_2g = "inverted_index_2g.db"

if __name__ == "__main__":
    unique_words = 0
    start_time = time.time()
    build_inverted_index(bookkeeping_input, directory_path, output_file, output_file_2g)
    end_time = time.time()
    elapsed_time_seconds = end_time - start_time
    elapsed_time_minutes = elapsed_time_seconds / 60
    elapsed_time_minutes = round (elapsed_time_minutes, 4)
    print(f"Elapsed time for building the inverted index: {elapsed_time_minutes} minutes")

    json_data = load_json_data(bookkeeping_input)
    print(f'Total Unique Documents in the Index: {len(json_data)}')

    with open("inverted_index.txt", "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if ":" in line:
                unique_words += 1
    print("Number of keys in inverted_index.txt:", unique_words)
    start_time = time.time()
    end_time = time.time()
    elapsed_time_seconds = (end_time - start_time) * 1000000
    elapsed_time_seconds = round (elapsed_time_seconds, 4)
    print(f"Elapsed time for counting unique words: {elapsed_time_seconds} microseconds")
    while True:
        word = input("Enter a word (or 'quit' to exit): ")
        if word.lower() == 'quit':
            break
        start_time = time.time()
        print(f"Word: {word}")
        query(word.lower(), bookkeeping_input)
        end_time = time.time()
        elapsed_time_seconds = (end_time - start_time) * 1000000
        elapsed_time_seconds = round (elapsed_time_seconds, 4)
        print(f"Elapsed time for searching {word}: {elapsed_time_seconds} microseconds")