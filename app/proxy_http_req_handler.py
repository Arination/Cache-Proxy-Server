import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, urljoin, parse_qs
import ast


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    proxy_cache = None
    origin = None

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def handle_request(self):
        parsed_path = urlparse(self.path)
        target_url = urljoin(self.origin, parsed_path.path)
        params = parse_qs(parsed_path.query)

        cache_key = self.proxy_cache.generate_key(parsed_path.path)
        cached_entry = self.proxy_cache.get(cache_key)
        print(type(cached_entry))
        # print(cached_entry)

        if cached_entry:
            print("Cache hit")
            cached_entry = cached_entry.decode("UTF-8")
            print("Cached Entry: ", type(cached_entry)) # String type
            mydata = ast.literal_eval(cached_entry)
            print("My Data: ", type(mydata)) # List type
            print(mydata)
            response_data, cached_headers = (
                mydata["response"],
                mydata["headers"],
            )
            self.send_response(200)
            self.send_caching_headers(cached_headers, from_cache=True)
            self.wfile.write(response_data)
            return

        print("Cache miss, forwarding request")
        response = self.forward_request(target_url, params)
        self.proxy_cache.set(cache_key, response.content, response.headers)

        self.send_response(response.status_code)
        self.send_caching_headers(response.headers, from_cache=False)
        self.wfile.write(response.content)

    def forward_request(self, url, params):
        headers = {key: value for key, value in self.headers.items() if key != "Host"}
        response = requests.get(url, headers=headers, params=params)
        return response

    def send_caching_headers(self, headers, from_cache):
        """
        Send headers and an additional header indicating whether the response was served from cache or origin.
        """
        for key, value in headers.items():
            self.send_header(key, value)

        if from_cache:
            self.send_header("X-Cache-Status", "HIT")
        else:
            self.send_header("X-Cache-Status", "MISS")

        self.end_headers()
