from bs4 import BeautifulSoup
import timeit
import random
from random_words import RandomWords
from BST import BinarySearchTree
from hash_table import HashQP
from splay_tree import SplayTree
from AVL_tree import AVLTree
import requests
import re
from bs4.element import Comment
from urllib.parse import urljoin

def text_harvester(url):
    headers = {
        'User-Agent': ''}
    try:
        page = requests.get(url, headers=headers)
    except:
        return []
    res = words_from_html(page.content)

    return res

def link_fisher(url, depth=0, reg_ex=""):
    res = _link_fisher(url, depth, reg_ex)
    res.append(url)
    return list(set(res))


def _link_fisher(url, depth, reg_ex):
    link_list = []
    if depth == 0:
        return link_list
    headers = {
        'User-Agent': ''}
    try:
        page = requests.get(url, headers=headers)
    except:
        print("Cannot retrieve", url)
        return link_list
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")
    for link in soup.find_all('a', attrs={'href': re.compile(reg_ex)}):
        link_list.append(urljoin(url, link.get('href')))
    for i in range(len(link_list)):
        link_list.extend(_link_fisher(link_list[i], depth - 1, reg_ex))
    return link_list


class WebStore(Exception):
    NotFoundError = None

    def __init__(self, ds):
        self._store = ds


    # Use link_fisher(), passing the three parameters that were passed to crawl, to capture a list of links.
    # Iterate through the list of links and capture the text on each page.
    # For each word found, either update using the KeywordEntry add() method or create a new KeywordEntry object for that word.
    # Make sure there is only one KeywordEntry object for each word, regardless of how many different pages contain that word.
    # Only store alphabetic words that are four or more letters long.
    def crawl(self, url: str, depth=0, reg_ex=""):
        kws = []
        for link in link_fisher(url, depth, reg_ex):
            for n, word in enumerate(text_harvester(link)):
                if len(word) < 4 or not word.isalpha():
                    continue
                else:
                    obj = KeywordEntry(word, link, n)
                    if obj in kws:
                        obj.add(link, n)
                    else:
                        self._store.append(obj)




    def crawl_and_list(self, url, depth=0, reg_ex=''):
        word_set = set()
        for link in link_fisher(url, depth, reg_ex):
            for word in text_harvester(link):
                if len(word) < 4 or not word.isalpha():
                    continue
                word_set.add(word)
        return list(word_set)

    # This is just a wrapper for our search method.
    # It should iterate through kw_list, calling search() for each item in the list.
    # Be sure to wrap the call to search() in a try / except block as we will be searching for many items that we know are not in the dataset.
    # For my testing, I kept track of how many words from kw_list were found in the crawled pages.I returned a tuple (found, not_found).
    # If you include this return value, you can uncomment the appropriate part of the testing code for some additional valuable metrics.

    def search_list(self, kw_list: list):
        for i in range(len(kw_list)):
            try:
                self.search(kw_list[i])
            except WebStore.NotFoundError:
                pass

    # Okay, we said we wouldn't do search yet, but we do need to make sure things are getting loaded correctly.
    # This method will just be a placeholder, and should return a list (not a KeywordEntry object) of all pages that contain keyword.
    def search(self, keyword: str):
        store = self._store()
        try:
            print(store.find(keyword).word)
            sitelist = self._store.find(keyword).sites
            return sitelist
        except self._store.NotFoundError:
            pass



def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def words_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.find_all(string=True)
    visible_texts = filter(tag_visible, texts)
    text_string = " ".join(t for t in visible_texts)
    words = re.findall(r'\w+', text_string)
    return words


class KeywordEntry:

    def __init__(self, word: str, url: str = None, location: int = None):
        self._word = word.upper()
        if url:
            self._sites = {url: [location]}
        else:
            self._sites = {}

    def add(self, url: str, location: int) -> None:
        if url in self._sites:
            self._sites[url].append(location)
        else:
            self._sites[url] = [location]

    def get_locations(self, url: str) -> list:
        try:
            return self._sites[url]
        except IndexError:
            return []

    @property
    def word(self):
        return self._word

    @property
    def sites(self) -> list:
        return [key for key in self._sites]

    def __eq__(self, other):
        if type(other) is KeywordEntry:
            if self._word == other.word:
                return self._word == other.word
        else:
            return self._word == other

    def __lt__(self, other):
        if type(other) is KeywordEntry:
            if self._word < other.word:
                return self._word.upper() < other.word
        else:
            return self._word < other

    def __gt__(self, other):
        if type(other) is KeywordEntry:
            if self._word > other.word:
                return self._word > other.word
        else:
            return self._word > other





rw = RandomWords()
num_random_words = 5449
search_trials = 10
crawl_trials = 1
structures = [BinarySearchTree, SplayTree, AVLTree, HashQP]
for depth in range(4):
    print("Depth = ", depth)
    stores = [WebStore(ds) for ds in structures]
    known_words = stores[0].crawl_and_list("http://compsci.mrreed.com", depth)
    total_words = len(known_words)
    print(f"{total_words} have been stored in the crawl")
    if len(known_words) > num_random_words:
        known_words = random.sample(known_words, num_random_words)
    random_words = rw.random_words(count=total_words)
    known_count = 0
    for word in random_words:
        if word in known_words:
            known_count += 1
    print(f"{known_count / len(random_words) * 100:.1f}% of random words "
          f"are in known words")
    for i, store in enumerate(stores):
        print("\n\nData Structure:", structures[i])
        time_s = timeit.timeit(f'store.crawl_and_list("http://compsci.mrreed.com", depth)',
                               setup=f"from __main__ import store, depth",
                               number=crawl_trials) / crawl_trials
        print(f"Crawl and Store took {time_s:.2f} seconds")
        for phase in (random_words, known_words):
            if phase is random_words:
                print("Search is random from total pool of random words")
            else:
                print("Search only includes words that appear on the site")
            for divisor in [1, 10, 100]:
                list_len = max(total_words // divisor, 1)
                print(f"- Searching for {list_len} words")
                search_list = random.sample(phase, list_len)
                store.search_list(search_list)
                total_time_us = timeit.timeit('store.search_list(search_list)',
                                              setup="from __main__ import store, search_list",
                                              number=search_trials)
                time_us = total_time_us / search_trials / list_len * (10 ** 6)
                # Uncomment for more data if you have coded a return value from search_list
                # found, not_found = store.search_list(search_list)
                # print(f"-- {found} of the words in kw_list were found, out of "
                #       f"{found + not_found} or "
                #       f"{found / (not_found + found) * 100:.0f}%")
                # print(f"-- {time_us:5.2f} microseconds per search")
print(f"{search_trials} search trials and "
      f"{crawl_trials} crawl trials were conducted")

# print(text_harvester('http://foothill.edu'))
