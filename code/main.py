from bs4 import BeautifulSoup
import timeit
from random_words import RandomWords
import requests
import re
from bs4.element import Comment
from urllib.parse import urljoin
import copy
import math
from enum import Enum
import random


class BinaryTreeNode:

    def __init__(self, data):
        self.data = data
        self.left_child = None
        self.right_child = None


class BinarySearchTree:
    class NotFoundError(Exception):
        pass

    class EmptyTreeError(Exception):
        pass

    def __init__(self):
        self._root = None
        self._size = 0

    @property
    def size(self):
        return self._size

    def find(self, key: str):
        return self._find(key.upper(), self._root)

    def _find(self, key, sub_root):
        if sub_root is None:
            raise BinarySearchTree.NotFoundError
        if key < sub_root.data:
            return self._find(key, sub_root.left_child)
        elif sub_root.data < key:
            return self._find(key, sub_root.right_child)
        else:
            return sub_root.data

    def __contains__(self, key):
        try:
            self.find(key)
            return True
        except self.NotFoundError:
            return False

    def insert(self, data):
        old_size = self._size
        self._root = self._insert(data, self._root)
        return old_size != self._size

    def _insert(self, data, sub_root):
        if sub_root is None:
            self._size += 1
            return BinaryTreeNode(data)
        if data < sub_root.data:
            sub_root.left_child = self._insert(data, sub_root.left_child)
        elif sub_root.data < data:
            sub_root.right_child = self._insert(data, sub_root.right_child)
        return sub_root

    def remove(self, data):
        self._root = self._remove(data, self._root)

    def _remove(self, data, sub_root):
        if sub_root is None:
            raise BinarySearchTree.NotFoundError
        if data < sub_root.data:
            sub_root.left_child = self._remove(data, sub_root.left_child)
        elif sub_root.data < data:
            sub_root.right_child = self._remove(data, sub_root.right_child)

        elif sub_root.left_child is not None \
                and sub_root.right_child is not None:
            sub_root.data = self._find_min(sub_root.right_child)
            sub_root.right_child = \
                self._remove(sub_root.data, sub_root.right_child)
        else:
            sub_root = sub_root.left_child if sub_root.left_child is not None \
                else sub_root.right_child
            self._size -= 1
        return sub_root

    def find_min(self):
        if self._root is None:
            raise BinarySearchTree.EmptyTreeError
        return self._find_min(self._root)

    def _find_min(self, sub_root):
        if sub_root.left_child is None:
            return sub_root.data
        else:
            return self._find_min(sub_root.left_child)

    def find_max(self):
        if self._root is None:
            raise BinarySearchTree.EmptyTreeError
        return self._find_max(self._root)

    def _find_max(self, sub_root):
        if sub_root.right_child is None:
            return sub_root.data
        else:
            return self._find_max(sub_root.right_child)

    def traverse(self, function):
        self._traverse(function, self._root)

    def _traverse(self, function, sub_root):
        if sub_root is None:
            return
        if sub_root.left_child is not None:
            self._traverse(function, sub_root.left_child)
        function(sub_root)
        if sub_root.right_child is not None:
            self._traverse(function, sub_root.right_child)

class SplayTree(BinarySearchTree):
    def __init__(self):
        super().__init__()

    def insert(self, data):
        if self._root is None:
            self._root = BinaryTreeNode(data)
            self._size += 1
            return True
        self._root = self._splay(data)
        if data < self._root.data:
            new_node = BinaryTreeNode(data)
            new_node.left_child = self._root.left_child
            new_node.right_child = self._root
            self._root.left_child = None
            self._root = new_node
            self._size += 1
            return True
        elif data > self._root.data:
            new_node = BinaryTreeNode(data)
            new_node.left_child = self._root
            new_node.right_child = self._root.right_child
            self._root.right_child = None
            self._root = new_node
            self._size += 1
            return True
        else:
            return False

    def remove(self, data):
        if self._root is None:
            return False
        self._root = self._splay(data)
        if data != self._root.data:
            return False
        if self._root.left_child is None:
            new_root = self._root.right_child
        else:
            new_root = self._root.left_child
            new_root = self._splay(data, new_root)
            new_root.right_child = self._root.right_child
        self._root = new_root
        self._size -= 1
        return True

    def __contains__(self, data):
        try:
            self.find(data)
            return True
        except self.NotFoundError:
            return False

    def find(self, data):
        if self._root is None:
            raise BinarySearchTree.NotFoundError
        self._root = self._splay(data)
        if self._root.data != data:
            raise BinarySearchTree.NotFoundError
        else:
            return self._root.data

    def show_root(self):
        if self._root is not None:
            return self._root.data

    def print_tree(self, sub_root=None):
        if sub_root is None:
            if self._root is None:
                return
            else:
                sub_root = self._root
        self._print_tree(sub_root, 0)

    def _print_tree(self, sub_root, depth):
        if sub_root is None:
            return
        for _ in range(depth):
            print("-", end="")
        print(sub_root.data)
        print("L")
        self._print_tree(sub_root.left_child, depth + 1)
        print("R")
        self._print_tree(sub_root.right_child, depth + 1)

    def _splay(self, data, sub_root=None):
        if sub_root is None:
            sub_root = self._root
        right_tree = None
        left_tree = None
        right_tree_min = None
        left_tree_max = None

        while sub_root.data != data:
            if data < sub_root.data:
                if sub_root.left_child is None:
                    break
                if data < sub_root.left_child.data:
                    sub_root = self._right_rotation(sub_root)
                    # sub_root = self._root
                    if sub_root.left_child is None:
                        break
                if right_tree is None:
                    right_tree = sub_root
                    right_tree_min = sub_root
                else:
                    # Specifically, it will be placed to the left of R's minimum node
                    right_tree_min.left_child = sub_root
                    right_tree_min = sub_root
                sub_root = sub_root.left_child
            elif data > sub_root.data:
                if sub_root.right_child is None:
                    break
                if data > sub_root.right_child.data:
                    sub_root = self._left_rotation(sub_root)
                    # sub_root = self._root
                    if sub_root.right_child is None:
                        break
                if left_tree is None:
                    left_tree = sub_root
                    left_tree_max = sub_root
                else:
                    # Feels infinite loopy
                    left_tree_max.right_child = sub_root
                    left_tree_max = sub_root
                sub_root = sub_root.right_child
            else:
                break

        if left_tree is not None:
            left_tree_max.right_child = sub_root.left_child
            sub_root.left_child = left_tree
        if right_tree is not None:
            right_tree_min.left_child = sub_root.right_child
            sub_root.right_child = right_tree

        return sub_root

    def _right_rotation(self, sub_root):
        # Identify the new sub_root and save to a temporary variable
        new_sub_root = sub_root.left_child

        # Move the node that would otherwise become the "middle node" to its new
        # position on the left side of the tree
        # Thus maneuver also makes space for the old sub_root
        sub_root.left_child = new_sub_root.right_child

        # Move the old sub_root to its position on the right of the new sub_root
        new_sub_root.right_child = sub_root

        return new_sub_root

    def _left_rotation(self, sub_root):
        # Identify the new sub_root and save to a temporary variable
        new_sub_root = sub_root.right_child

        # Move the node that would otherwise become the "middle node" to its new
        # position on the right side of the tree
        # Thus maneuver also makes space for the old sub_root
        sub_root.right_child = new_sub_root.left_child

        # Move the old sub_root to its position on the left of the new sub_root
        new_sub_root.left_child = sub_root

        return new_sub_root


class AVLTreeNode(BinaryTreeNode):

    def __init__(self, data):
        self.height = 0
        super().__init__(data)

    def calc_height(self):
        self.height = max(self.child_heights) + 1

    @property
    def child_heights(self):
        if self.left_child is None:
            left_height = -1
        else:
            left_height = self.left_child.height
        if self.right_child is None:
            right_height = -1
        else:
            right_height = self.right_child.height
        return left_height, right_height


class AVLTree(BinarySearchTree):

    def calc_heights_after_rotation(self, new_sub_root):
        if new_sub_root.left_child is not None:
            new_sub_root.left_child.calc_height()
        if new_sub_root.right_child is not None:
            new_sub_root.right_child.calc_height()
        new_sub_root.calc_height()

    def right_rotation(self, sub_root):
        new_sub_root = sub_root.left_child
        tempR = new_sub_root.right_child
        new_sub_root.right_child = sub_root
        sub_root.left_child = tempR
        sub_root.calc_height()
        new_sub_root.calc_height()
        return new_sub_root

    def left_rotation(self, sub_root):
        new_sub_root = sub_root.right_child
        tempL = new_sub_root.left_child
        new_sub_root.left_child = sub_root
        sub_root.right_child = tempL
        sub_root.calc_height()
        new_sub_root.calc_height()
        return new_sub_root

    def _insert(self, data, sub_root):
        if sub_root is None:
            self._size += 1
            return AVLTreeNode(data)
        sub_root = super()._insert(data, sub_root)
        sub_root = self._rotate_if_needed(sub_root)
        return sub_root

    def _remove(self, data, sub_root):
        sub_root = super()._remove(data, sub_root)
        sub_root = self._rotate_if_needed(sub_root)
        return sub_root

    def _rotate_if_needed(self, node):
        if node is None:
            return node
        node.calc_height()
        (left_height, right_height) = node.child_heights
        if left_height - right_height > 1:
            # Right Rotation Needed
            if node.left_child is not None:
                (left_height, right_height) = \
                    node.left_child.child_heights
                if right_height - left_height > 0:
                    # Left Right Rotation Needed
                    node.left_child = self.left_rotation(node.left_child)
            node = self.right_rotation(node)
        elif right_height - left_height > 1:
            # Right Rotation Needed
            if node.right_child is not None:
                (left_height, right_height) = \
                    node.right_child.child_heights
                if left_height - right_height > 0:
                    # Right Left Rotation Needed
                    node.right_child = self.right_rotation(node.right_child)
            node = self.left_rotation(node)
        return node

    def print_tree(self, sub_root=None):
        if sub_root is None:
            if self._root is None:
                return
            else:
                sub_root = self._root
        self._print_tree(sub_root, 0)

    def _print_tree(self, sub_root, depth):
        if sub_root is None:
            return
        for _ in range(depth):
            print("-", end="")
        print(sub_root.data)
        print("L")
        self._print_tree(sub_root.left_child, depth + 1)
        print("R")
        self._print_tree(sub_root.right_child, depth + 1)


def check_AVL_cond(sub_root):
    if sub_root is not None:
        (left, right) = sub_root.child_heights
        if abs(left - right) > 1:
            print("AVL Violated")
        if sub_root.left_child is not None:
            check_AVL_cond(sub_root.left_child)
        if sub_root.right_child is not None:
            check_AVL_cond(sub_root.right_child)

class HashEntry:
    class State(Enum):
        ACTIVE = 0
        EMPTY = 1
        DELETED = 2

    def __init__(self, data=None):
        self._data = data
        self._state = HashEntry.State.EMPTY

    @property
    def data(self):
        return self._data

class HashQP:
    class NotFoundError(Exception):
        pass

    INIT_TABLE_SIZE = 97
    INIT_MAX_LAMBDA = .49

    def __init__(self, table_size=None):

        self._sites = None
        if table_size is None or table_size < HashQP.INIT_TABLE_SIZE:
            self._table_size = self._next_prime(HashQP.INIT_TABLE_SIZE)
        else:
            self._table_size = self._next_prime(table_size)
        self._buckets = [HashEntry() for _ in range(self._table_size)]
        self._max_lambda = HashQP.INIT_MAX_LAMBDA
        self._size = 0
        self._load_size = 0

    def _internal_hash(self, item):
        return hash(item) % self._table_size

    def _next_prime(self, floor):
        # loop doesn't work for 2 or 3
        if floor <= 2:
            return 2
        elif floor == 3:
            return 3
        if floor % 2 == 0:
            candidate = floor + 1
        else:
            candidate = floor

        while True:
            # we know candidate is odd.  check for divisibility by 3
            if candidate % 3 != 0:
                loop_lim = int((math.sqrt(candidate) + 1) / 6)
                # now we can check for divisibility by 6k +/- 1 up to sqrt
                for k in range(1, loop_lim + 1):
                    if candidate % (6 * k - 1) == 0:
                        break
                    if candidate % (6 * k + 1) == 0:
                        break
                    if k == loop_lim:
                        return candidate
            candidate += 2

    def _find_pos(self, data):
        kth_odd_number = 1
        bucket = self._internal_hash(data)
        while self._buckets[bucket]._state != HashEntry.State.EMPTY and \
                self._buckets[bucket]._data != data:
            bucket += kth_odd_number
            kth_odd_number += 2
            if bucket >= self._table_size:
                bucket -= self._table_size
        return bucket

    def __contains__(self, data):
        bucket = self._find_pos(data)
        return self._buckets[bucket]._state == HashEntry.State.ACTIVE

    def remove(self, data):
        bucket = self._find_pos(data)
        if self._buckets[bucket]._state != HashEntry.State.ACTIVE:
            return False
        else:
            self._buckets[bucket]._state = HashEntry.State.DELETED
            self._size -= 1
            return True

    def insert(self, data):
        bucket = self._find_pos(data.word)
        if self._buckets[bucket]._state == HashEntry.State.ACTIVE:
            return False
        elif self._buckets[bucket]._state == HashEntry.State.EMPTY:
            self._load_size += 1
        self._buckets[bucket]._data = data
        self._buckets[bucket]._state = HashEntry.State.ACTIVE
        self._size += 1
        if self._load_size > self._max_lambda * self._table_size:
            self._rehash()
        return True

    def _rehash(self):
        old_table_size = self._table_size
        self._table_size = self._next_prime(2 * old_table_size)
        old_buckets = copy.copy(self._buckets)
        self._buckets = [HashEntry() for _ in range(self._table_size)]
        self._size = 0
        self._load_size = 0
        for k in range(old_table_size):
            if old_buckets[k]._state == HashEntry.State.ACTIVE:
                self.insert(old_buckets[k]._data)

    @property
    def size(self):
        return self._size

    @property
    def max_lambda(self):
        return self._max_lambda

    @property
    def data(self):
        return self.data

    @property
    def sites(self):
        return self._sites

    @max_lambda.setter
    def max_lambda(self, max_lambda):
        if max_lambda > 0:
            self._max_lambda = max_lambda

    def find(self, data):
        if type(data) is str:
            data = data.upper()
        bucket = self._find_pos(data)
        if self._buckets[bucket]._state != HashEntry.State.ACTIVE:
            raise HashQP.NotFoundError()
        elif self._buckets[bucket]._data == data:
            return self._buckets[bucket]._data
        else:
            raise HashQP.NotFoundError()


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
                return self._word < other.word
        else:
            return self._word < other

    def __gt__(self, other):
        if type(other) is KeywordEntry:
            if self._word > other.word:
                return self._word > other.word
        else:
            return self._word > other


class WebStore(Exception):
    NotFoundError = None

    def __init__(self, ds):
        self._store = ds()

    # Use link_fisher(), passing the three parameters that were passed to crawl, to capture a list of links.
    # Iterate through the list of links and capture the text on each page.
    # For each word found, either update using the KeywordEntry add() method or create a new KeywordEntry object for that word.
    # Make sure there is only one KeywordEntry object for each word, regardless of how many different pages contain that word.
    # Only store alphabetic words that are four or more letters long.
    def crawl(self, url: str, depth=0, reg_ex=""):
        for link in link_fisher(url, depth, reg_ex):
            for n, word in enumerate(text_harvester(link)):
                if len(word) < 4 or not word.isalpha():
                    continue
                try:
                    self._store.find(word.upper()).add(link, n)
                except self._store.NotFoundError:
                    self._store.insert(KeywordEntry(word, link, n))


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
                continue

    # Okay, we said we wouldn't do search yet, but we do need to make sure things are getting loaded correctly.
    # This method will just be a placeholder, and should return a list (not a KeywordEntry object) of all pages that contain keyword.
    def search(self, keyword: str):
        try:
            sitelist = self._store.find(keyword.upper()).sites
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
    print(f"{len(known_words)} have been stored in the crawl")
    if len(known_words) > num_random_words:
        known_words = random.sample(known_words, num_random_words)
    num_words = len(known_words)
    random_words = rw.random_words(count=num_words)
    known_count = 0
    for word in random_words:
        if word in known_words:
            known_count += 1
    print(f"{known_count / len(random_words) * 100:.1f}% of random words "
          f"are in known words")
    for i, store in enumerate(stores):
        print("\n\nData Structure:", structures[i])
        time_s = timeit.timeit(f'store.crawl("http://compsci.mrreed.com", depth)',
                               setup=f"from __main__ import store, depth",
                               number=crawl_trials) / crawl_trials
        print(f"Crawl and Store took {time_s:.2f} seconds")
        for phase in (random_words, known_words):
            if phase is random_words:
                print("Search is random from total pool of random words")
            else:
                print("Search only includes words that appear on the site")
            for divisor in [1, 10, 100]:
                list_len = max(num_words // divisor, 1)
                print(f"- Searching for {list_len} words")
                search_list = random.sample(phase, list_len)
                store.search_list(search_list)
                total_time_us = timeit.timeit('store.search_list(search_list)',
                                              setup="from __main__ import store, search_list",
                                              number=search_trials)
                time_us = total_time_us / search_trials / list_len * (10 ** 6)
                print(f"-- {time_us:5.2f} microseconds per search")
print(f"{search_trials} search trials and "
      f"{crawl_trials} crawl trials were conducted")

### TEST RUN ###
# Depth =  0
# 38 have been stored in the crawl
# 0.0% of random words are in known words
#
#
# Data Structure: <class '__main__.BinarySearchTree'>
# Crawl and Store took 0.11 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# --  6.30 microseconds per search
# - Searching for 3 words
# --  4.57 microseconds per search
# - Searching for 1 words
# --  6.22 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# --  5.18 microseconds per search
# - Searching for 3 words
# --  4.57 microseconds per search
# - Searching for 1 words
# --  4.19 microseconds per search
#
#
# Data Structure: <class '__main__.SplayTree'>
# Crawl and Store took 0.10 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# --  9.17 microseconds per search
# - Searching for 3 words
# --  6.75 microseconds per search
# - Searching for 1 words
# --  3.76 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# --  9.48 microseconds per search
# - Searching for 3 words
# --  4.13 microseconds per search
# - Searching for 1 words
# --  2.89 microseconds per search
#
#
# Data Structure: <class '__main__.AVLTree'>
# Crawl and Store took 0.11 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# --  5.61 microseconds per search
# - Searching for 3 words
# --  5.18 microseconds per search
# - Searching for 1 words
# --  6.34 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# --  3.84 microseconds per search
# - Searching for 3 words
# --  3.48 microseconds per search
# - Searching for 1 words
# --  5.44 microseconds per search
#
#
# Data Structure: <class '__main__.HashQP'>
# Crawl and Store took 0.11 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# --  3.43 microseconds per search
# - Searching for 3 words
# --  5.10 microseconds per search
# - Searching for 1 words
# --  5.76 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# --  4.92 microseconds per search
# - Searching for 3 words
# --  3.77 microseconds per search
# - Searching for 1 words
# --  4.89 microseconds per search
# Depth =  1
# 598 have been stored in the crawl
# 10.4% of random words are in known words
#
#
# Data Structure: <class '__main__.BinarySearchTree'>
# Crawl and Store took 1.55 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# --  7.59 microseconds per search
# - Searching for 59 words
# --  5.93 microseconds per search
# - Searching for 5 words
# --  5.74 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# --  5.03 microseconds per search
# - Searching for 59 words
# --  4.89 microseconds per search
# - Searching for 5 words
# --  5.07 microseconds per search
#
#
# Data Structure: <class '__main__.SplayTree'>
# Crawl and Store took 1.08 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# -- 10.98 microseconds per search
# - Searching for 59 words
# --  8.05 microseconds per search
# - Searching for 5 words
# --  4.69 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# -- 10.65 microseconds per search
# - Searching for 59 words
# --  6.51 microseconds per search
# - Searching for 5 words
# --  3.05 microseconds per search
#
#
# Data Structure: <class '__main__.AVLTree'>
# Crawl and Store took 1.01 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# --  7.11 microseconds per search
# - Searching for 59 words
# --  5.84 microseconds per search
# - Searching for 5 words
# --  5.98 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# --  4.29 microseconds per search
# - Searching for 59 words
# --  4.00 microseconds per search
# - Searching for 5 words
# --  4.55 microseconds per search
#
#
# Data Structure: <class '__main__.HashQP'>
# Crawl and Store took 0.99 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# --  2.90 microseconds per search
# - Searching for 59 words
# --  2.82 microseconds per search
# - Searching for 5 words
# --  2.92 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# --  3.10 microseconds per search
# - Searching for 59 words
# --  2.82 microseconds per search
# - Searching for 5 words
# --  3.11 microseconds per search
# Depth =  2
# 3920 have been stored in the crawl
# 71.2% of random words are in known words
#
#
# Data Structure: <class '__main__.BinarySearchTree'>
# Crawl and Store took 14.69 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# --  8.26 microseconds per search
# - Searching for 392 words
# --  8.45 microseconds per search
# - Searching for 39 words
# --  8.09 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# --  7.15 microseconds per search
# - Searching for 392 words
# --  7.26 microseconds per search
# - Searching for 39 words
# --  7.18 microseconds per search
#
#
# Data Structure: <class '__main__.SplayTree'>
# Crawl and Store took 13.91 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# -- 13.56 microseconds per search
# - Searching for 392 words
# -- 10.21 microseconds per search
# - Searching for 39 words
# --  6.96 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# -- 13.98 microseconds per search
# - Searching for 392 words
# -- 11.63 microseconds per search
# - Searching for 39 words
# --  6.37 microseconds per search
#
#
# Data Structure: <class '__main__.AVLTree'>
# Crawl and Store took 14.32 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# --  6.11 microseconds per search
# - Searching for 392 words
# --  6.02 microseconds per search
# - Searching for 39 words
# --  5.98 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# --  5.77 microseconds per search
# - Searching for 392 words
# --  5.78 microseconds per search
# - Searching for 39 words
# --  5.50 microseconds per search
#
#
# Data Structure: <class '__main__.HashQP'>
# Crawl and Store took 13.74 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# --  2.45 microseconds per search
# - Searching for 392 words
# --  2.21 microseconds per search
# - Searching for 39 words
# --  2.16 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# --  2.45 microseconds per search
# - Searching for 392 words
# --  2.26 microseconds per search
# - Searching for 39 words
# --  2.21 microseconds per search
# Depth =  3
# 5298 have been stored in the crawl
# 97.2% of random words are in known words
#
#
# Data Structure: <class '__main__.BinarySearchTree'>
# Crawl and Store took 118.94 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# --  7.68 microseconds per search
# - Searching for 529 words
# --  7.81 microseconds per search
# - Searching for 52 words
# --  7.58 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# --  7.99 microseconds per search
# - Searching for 529 words
# --  7.63 microseconds per search
# - Searching for 52 words
# --  7.60 microseconds per search
#
#
# Data Structure: <class '__main__.SplayTree'>
# Crawl and Store took 120.01 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# -- 15.55 microseconds per search
# - Searching for 529 words
# -- 11.28 microseconds per search
# - Searching for 52 words
# --  8.25 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# -- 15.66 microseconds per search
# - Searching for 529 words
# -- 11.19 microseconds per search
# - Searching for 52 words
# --  6.72 microseconds per search
#
#
# Data Structure: <class '__main__.AVLTree'>
# Crawl and Store took 119.64 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# --  6.38 microseconds per search
# - Searching for 529 words
# --  6.17 microseconds per search
# - Searching for 52 words
# --  5.95 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# --  6.20 microseconds per search
# - Searching for 529 words
# --  6.13 microseconds per search
# - Searching for 52 words
# --  6.07 microseconds per search
#
#
# Data Structure: <class '__main__.HashQP'>
# Crawl and Store took 116.02 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# --  3.19 microseconds per search
# - Searching for 529 words
# --  2.73 microseconds per search
# - Searching for 52 words
# --  2.74 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# --  2.75 microseconds per search
# - Searching for 529 words
# --  2.75 microseconds per search
# - Searching for 52 words
# --  2.78 microseconds per search
# 10 search trials and 1 crawl trials were conducted
#
# Process finished with exit code 0
