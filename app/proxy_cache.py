import hashlib
import time


class ProxyCache:
    def __init__(self, expiration=300):
        self.expiration = expiration
        self.cache = {}
        
    def clear_cache(self): 
        self.cache.clear()
        print("Cache cleared")

    def generate_key(self, path):
        """
        Generates a cache key based on the request path.
        """
        return hashlib.sha256(path.encode()).hexdigest()

    def get(self, key):
        """
        Retrieves a cached response if it exists and isn't expired.
        """
        entry = self.cache.get(key)
        if entry and time.time() < entry["expiry"]:
            return entry
        return None

    def set(self, key, response, headers):
        """
        Stores the response in the cache with an expiration time.
        """
        self.cache[key] = {
            "response": response,
            "headers": headers,
            "expiry": time.time() + self.expiration,
        }
