import streamlit as st
from index_constructor import build_inverted_index, load_json_data
from basic_query import query
import time

bookkeeping_input = "webpages_raw/bookkeeping.json"
directory_path = "webpages_raw/"
output_file = "inverted_index.txt"


def main():
    st.title("Search Engine")

    build_index = st.button("Build Inverted Index")

    if build_index:
        st.subheader("Building Inverted Index")
        start_time = time.time()
        build_inverted_index(bookkeeping_input, directory_path, output_file)
        end_time = time.time()
        elapsed_time_minutes = (end_time - start_time) / 60
        st.write(f"Elapsed time for building the inverted index: {elapsed_time_minutes:.2f} minutes")

        st.subheader("Loading JSON Data")
        json_data = load_json_data(bookkeeping_input)
        st.write(f'Total Unique Documents in the Index: {len(json_data)}')

        st.subheader("Counting Unique Words")
        unique_words = 0
        with open("inverted_index.txt", "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if ":" in line:
                    unique_words += 1
        st.write("Number of keys in inverted_index.txt:", unique_words)

    st.subheader("Search Query")
    search_query = st.text_input("Enter a word (or 'quit' to exit):")

    # Add a button to trigger the search
    search_button = st.button("Search")

    # Perform search when the button is clicked
    if search_button:
        if search_query.lower() != 'quit':
            result = query(search_query.lower(), bookkeeping_input)
            st.write(f"Search Results for '{search_query}':")

            # Display clickable links without Streamlit adding the base URL
            for item in result:
                # Truncate the link to display only the first 50 characters
                truncated_item = item[:90] + '...' if len(item) > 50 else item
                st.markdown(f'<a href="{item}" target="_blank">{truncated_item}</a>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
