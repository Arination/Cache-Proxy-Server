import http
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, urljoin, parse_qs, urlsplit


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
        print("Handling request")
        print("Path: ", self.path)

        parsed_path = urlparse(self.path)
        target_url = urljoin(self.origin, parsed_path.path)
        params = parse_qs(parsed_path.query)

        cache_key = self.proxy_cache.generate_key(parsed_path.path)
        cached_entry = self.proxy_cache.get(cache_key)

        if cached_entry:
            print("Cache hit")
            response_data, cached_headers = (
                cached_entry["response"],
                cached_entry["headers"],
            )
            self.send_response(200)
            self.send_caching_headers(cached_headers, from_cache=True)
            self.wfile.write(response_data)
            return

        print("Cache miss, forwarding request")
        response = self.forward_request(target_url, params)
        print(type(response))
        print("Response: ", response)
        
        content = response["content"].decode("utf-8")

        self.proxy_cache.set(cache_key, content, dict(response["headers"]))

        # Send response to client
        self.send_response(response["status_code"])
        self.send_caching_headers(dict(response["headers"]), from_cache=False)
        self.wfile.write(response["content"])

    def forward_request(self, url, params):
        # Parse the URL to get the host and path
        parsed_url = urlsplit(url)
        connection = http.client.HTTPConnection(parsed_url.netloc, timeout=5)

        # Prepare path with query parameters if any
        path = parsed_url.path
        if params:
            query_string = "&".join(f"{k}={v[0]}" for k, v in params.items())
            path += f"?{query_string}"

        headers = {key: value for key, value in self.headers.items() if key != "Host"}
        headers["Connection"] = "close"  # Explicitly close the connection

        try:
            # Send the GET request
            connection.request("GET", path, headers=headers)
            response = connection.getresponse()

            # Read and return response data and headers
            return {
                "status_code": response.status,
                "content": response.read(),
                "headers": response.getheaders(),
            }
        except Exception as e:
            self.send_error(502, "Bad Gateway", f"Error forwarding request: {e}")
            return None
        finally:
            connection.close()

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
