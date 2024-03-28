# CompSci 121: Information Retrieval
An introduction to information retrieval including indexing, retrieval, classifying, and clustering text and multimedia documents.

## Project 1: Text Processing
A Python program that runs in linear time to efficiently tokenizes a text file and arranges the tokens in descending order and also determine the count of shared words between two distinct text files.

## Project 2: Web Crawler
A web crawler navigates through the static corpus of ics.uci.edu, identifying relevant links for further exploration. It adeptly handles common crawler traps like dynamic pages, repetitive pages, and URL depth traps. Furthermore, the crawler conducts analytics on the corpus to extract meaningful insights.

## Project 3: Search Engine
A Search Engine written in Python, designed to provide efficient and accurate search capabilities for HTML documents. The program builds an inverted index and an additional 2-gram index, leveraging TF-IDF scoring and HTML tag analysis, it ranks search results based on relevance, ensuring users receive the most relevant information.

Key Features:
* TF-IDF Scoring: The search engine employs TF-IDF (Term Frequency-Inverse Document Frequency) scoring to rank search results based on the importance of terms within documents.
* HTML Tag Analysis: By analyzing HTML tags such as titles, headings, and meta tags, the search engine improves the accuracy of search results by considering the structure and semantics of HTML documents.
* 2-Gram Index: In addition to single-word indexing, the search engine utilizes a 2-gram index, allowing for more comprehensive and efficient search queries by considering word pairs.
* Graphical User Interface (GUI): The search engine features a user-friendly GUI that enables users to input search queries and view results in a visually appealing interface.
* PageRank Algorithm: Integrates the PageRank algorithm, originally developed by Google, to rank search results based on the importance of web pages, thus ensuring that more relevant and authoritative pages are displayed prominently.
* Automatic Spell Checker: Incorporates spell checking mechanisms to enhance user experience by automatically correcting or suggesting alternative spellings for search queries.
* Cosine Similarity: Computes cosine similarity between search query vectors and document vectors to determine the relevance of documents to the query, further refining search result ranking.
* Text Preprocessing: Tokezined words for the index, used lemmitization to improve the matching of similar term and also removed stop words to make the search engine more efficient.
* Graphical User Interface (GUI): Features a user-friendly GUI that enables users to input search queries and view results in a visually appealing interface, enhancing accessibility and usability.
