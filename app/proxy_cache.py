import hashlib
import time
import os, json


class ProxyCache:
    CACHE_FILE = "cache.json"

    def __init__(self, expiration=300):
        self.expiration = expiration
        self.cache = {}

        if not os.path.exists(self.CACHE_FILE):
            print("Cache file not found. Creating a new cache file.")
            with open(self.CACHE_FILE, "w") as f:
                json.dump({}, f)

    def load_cache(self):
        with open(self.CACHE_FILE, "r") as f:
            return json.load(f)

    def save_cache(self, cache_data):
        with open(self.CACHE_FILE, "w") as f:
            json.dump(cache_data, f)

    def generate_key(self, path):
        """
        Generates a cache key based on the request path.
        """
        return hashlib.sha256(path.encode()).hexdigest()

    def get(self, key):
        cache_data = self.load_cache()
        entry = cache_data.get(key)
        if entry and time.time() < entry["expiry"]:
            return entry

        return None

    def set(self, key, response, headers):
        cache_data = self.load_cache()

        cache_data[key] = {
            "response": response,
            "headers": headers,
            "expiry": time.time() + self.expiration
        }

        self.save_cache(cache_data)

    def clear_cache(self):
        self.save_cache({})  # Clear the cache by saving an empty dictionary
        print("Cache cleared successfully.")
