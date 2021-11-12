import copy
import math
from enum import Enum


class HashEntry:
    class State(Enum):
        ACTIVE = 0
        EMPTY = 1
        DELETED = 2

    def __init__(self, data=None, site=None):
        self._data = data
        self._state = HashEntry.State.EMPTY
        self._sites = site


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
        return_value = 0

        for i in range((len(item))):
            return_value = 37 * (return_value) + ord(item[i])

        if self.size == 0:
            mysize = self.INIT_TABLE_SIZE
        else:
            mysize = self._table_size
        return return_value % self._table_size

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

