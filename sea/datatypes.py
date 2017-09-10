import time
from threading import RLock
from collections import OrderedDict
from itertools import repeat


def is_immutable(self):
    raise TypeError('%r objects are immutable' % self.__class__.__name__)


class ImmutableDict(dict):
    _hash_cache = None

    @classmethod
    def fromkeys(cls, keys, value=None):
        return cls(zip(keys, repeat(value)))

    def __reduce_ex__(self, protocol):
        return type(self), (dict(self),)

    def __hash__(self):
        if self._hash_cache is not None:
            return self._hash_cache
        rv = self._hash_cache = hash(frozenset(self.items()))
        return rv

    def setdefault(self, key, default=None):
        is_immutable(self)

    def update(self, *args, **kwargs):
        is_immutable(self)

    def pop(self, key, default=None):
        is_immutable(self)

    def popitem(self):
        is_immutable(self)

    def __setitem__(self, key, value):
        is_immutable(self)

    def __delitem__(self, key):
        is_immutable(self)

    def clear(self):
        is_immutable(self)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            dict.__repr__(self),
        )

    def copy(self):
        """Return a shallow mutable copy of this object.  Keep in mind that
        the standard library's :func:`copy` function is a no-op for this class
        like for any other python immutable type (eg: :class:`tuple`).
        """
        return dict(self)

    def __copy__(self):
        return self


class ConstantsObject(ImmutableDict):

    def __getattr__(self, name):
        return self[name]


class KeyExpiredDict:

    def __init__(self, max_len=1000):
        super().__init__()
        self.max_len = max_len
        self.expired_map = {}
        self.data = OrderedDict()
        self.lock = RLock()

    def __getitem__(self, key):
        with self.lock:
            try:
                value = self.data[key]
            except KeyError:
                return None

            self.data.move_to_end(key)

            expired_time = self.expired_map.get(key, None)

            # key doesn't have expired_time
            if expired_time is None:
                return value

            if expired_time <= time.monotonic():
                del self.data[key]
                del self.expired_map[key]
                return None
            return value

    def get(self, key):
        return self[key]

    def __setitem__(self, key, value):
        with self.lock:
            if key in self.data:
                self.data.pop(key)
            elif len(self.data) == self.max_len:
                self.data.popitem(last=False)
            self.data[key] = value

    def set(self, key, value, seconds=None):
        with self.lock:
            self.data[key] = value
            if seconds is not None:
                self.expired_map[key] = time.monotonic() + seconds

    def incr(self, key):
        with self.lock:
            value = self.data[key] or 0
            if not isinstance(value, int):
                raise TypeError("only Integer can incr")
            self.data[key] = value + 1

    def expire(self, key, seconds):
        with self.lock:
            if key in self.data:
                expired_time = time.monotonic() + seconds
                self.expired_map[key] = expired_time
            else:
                raise KeyError("key doesn't exist")
