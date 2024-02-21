import logging
import re
import nltk
from urllib.parse import urlparse, urljoin
from lxml import html
from collections import Counter
from nltk.corpus import stopwords, words
logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """
    total_out_links = {}
    subdomain_count = {}
    max_out_links = {}
    valid_urls = set()
    identified_traps= set()
    repeating_subdirectory = {}
    max_words_url = ""
    max_words = 0
    total_words = []
    nltk.download('stopwords')
    nltk.download('words')

    def __init__(self, frontier, corpus):
        self.frontier = frontier
        self.corpus = corpus

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched,
                        len(self.frontier))
            url_data = self.corpus.fetch_url(url)

            for next_link in self.extract_next_links(url_data):
                if self.is_valid(next_link):
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)
        self.writeToFile()

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """
        outputLinks = []
        valid_out_links = []

        # Check if HTML content exists
        if url_data['content']:
            try:
                # Get the HTML content
                html_content = url_data['content']

            except UnicodeDecodeError as e:
                print("Error decoding HTML content:", e)
                return outputLinks

            # Parse the HTML content
            try:
                html_tree = html.fromstring(html_content)
            except Exception as e:
                print("Error parsing HTML:", e)
                return outputLinks

            # Get all links from anchor tags and their href attributes
            links = html_tree.xpath("//a/@href")

            # Get text from specific HTML elements excluding <style> elements
            text = ' '.join(html_tree.xpath('//body//*[not(self::style)]//text()'))
            words = re.findall(r'\b\w+\b', text)

            # Adding all the words to the total list
            self.total_words.extend(words)

            # Check if current page has the most words
            if self.max_words < len(words):
                self.max_words_url = url_data['url']
                self.max_words = len(words)

            # Convert relative links to absolute links and adding it to outputLinks
            if url_data['final_url']:
                base_url = url_data['final_url']
            else:
                base_url = url_data['url']
            if base_url:
                for link in links:
                    absolute_link = urljoin(base_url, link)
                    outputLinks.append(absolute_link)
                # If the links are valid then add them to the valid_out_links list
                for link in links:
                    if self.is_valid(link):
                        absolute_link = urljoin(base_url, link)
                        valid_out_links.append(absolute_link)
                    Crawler.max_out_links[base_url] = len(valid_out_links)
                    # this parses the subdomain from the domain
                    parsed = urlparse(absolute_link)
                    subdomain = parsed.hostname
                    if parsed.hostname and parsed.hostname.endswith('.ics.uci.edu'):
                        # Remove 'www' if it exists
                        if subdomain.startswith('www.'):
                            subdomain = subdomain[4:]
                        if subdomain in Crawler.subdomain_count:
                            Crawler.subdomain_count[subdomain] += 1
                        else:
                            Crawler.subdomain_count[subdomain] = 1
                        Crawler.total_out_links[subdomain] = Crawler.subdomain_count[subdomain]
        return outputLinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        parsed = urlparse(url)
        depth_limit = 5
        if parsed.scheme not in set(["http", "https"]):
            return False
        try:
            # Check if the hostname contains ".ics.uci.edu"
            if ".ics.uci.edu" not in parsed.hostname:
                return False

            # Check if the path doesn't end with certain file extensions
            if re.match(
                    r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp[234]|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz)$",
                    parsed.path.lower()):
                return False

            # Check URL depth limit
            if url.count('/') > depth_limit:
                Crawler.identified_traps.add(url)
                return False

            # Check query and fragment and repeated patters before it
            for symbol in ['?', '#']:
                index = url.find(symbol)

                if index != -1:
                    next_url = url[:index]
                else:
                    next_url = url

                if next_url in Crawler.repeating_subdirectory:
                    # if the repeated pattern is detected more than 5 times ignore it
                    if Crawler.repeating_subdirectory[next_url] > 5:
                        Crawler.identified_traps.add(url)
                        return False
                    else:
                        Crawler.repeating_subdirectory[next_url] += 1
                else:
                    Crawler.repeating_subdirectory[next_url] = 1

            # If all conditions are met, return True
            Crawler.valid_urls.add(url)
            return True

        except TypeError:
            print("TypeError for ", parsed)
            return False

    # Write the analytics to 5 files
    def writeToFile(self):
        word_counts = Counter(self.total_words)
        stop_words = set(stopwords.words('english'))  # Get NLTK English stopwords
        english_words = set(words.words())  # Get NLTK English words
        # Check if the word is not a stopword, is a word in NLTK library, and it's not a letter
        common_words = [(word, count) for word, count in word_counts.most_common() if
                        len(word) > 1 and word.lower() not in stop_words and word.lower() in english_words]
        # Select the top 50 most common words after filtering
        common_words_top_50 = common_words[:50]
        file_path1 = "analytics_1.txt"
        file_path2 = "analytics_2.txt"
        file_path3_link = "analytics_3_links.txt"
        file_path3_trap = "analytics_3_traps.txt"
        file_path4 = "analytics_4.txt"
        file_path5 = "analytics_5.txt"
        with open(file_path1, 'w', encoding="utf-8") as file:
            file.write("1.\nSubdomains: # of times visited\n")
            for link, outlink in self.total_out_links.items():
                file.write(f"{link}: {outlink}\n")
        with open(file_path2, 'w', encoding="utf-8") as file:
            file.write("2.\n")
            most_outlink_page = max(Crawler.max_out_links, key=lambda link: Crawler.max_out_links[link])
            file.write(f"The page with most valid out links: {most_outlink_page}\nThe number of out links: {Crawler.max_out_links[most_outlink_page]}")
        with open(file_path3_link, 'w', encoding="utf-8") as file:
            file.write("3.\n")
            file.write("Valid Links:\n")
            for valid_links in self.valid_urls:
                file.write(f"{valid_links}\n")
        with open(file_path3_trap, 'w', encoding="utf-8") as file:
            file.write("3.\n")
            file.write("Identified Traps:\n")
            for traps in self.identified_traps:
                file.write(f"{traps}\n")
        with open(file_path4, 'w', encoding="utf-8") as file:
            file.write("4.\n")
            file.write(f"Longest page in terms of word: {self.max_words_url}\nWord Count: {self.max_words}")
        with open(file_path5, 'w', encoding="utf-8") as file:
            file.write("5.\n50 most common words in the corpus:\n")
            for word, count in common_words_top_50:
                file.write(f"{word}: {count}\n")