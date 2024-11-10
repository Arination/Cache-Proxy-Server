import http, ssl
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, urljoin, parse_qs, urlsplit
import gzip, zlib


class ProxyHTTPRequestHandler(SimpleHTTPRequestHandler):
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
            self.wfile.write(response_data.encode("utf-8"))
            return

        print("Cache miss, forwarding request")
        response = self.forward_request(target_url, params)

        content = response["content"]
        headers = {
            item[0]: item[1] for item in response["headers"]
        }

        content_encoding = headers.get("Content-Encoding", "")

        if content_encoding == "gzip":
            content = gzip.decompress(content)
        elif content_encoding == "deflate":
            content = zlib.decompress(content) 

        content_type = headers.get("Content-Type", "")
        if "text" in content_type or "json" in content_type:
            content = content.decode("utf-8", errors="replace")

        headers.pop("Content-Encoding", None)
        headers.pop("Transfer-Encoding", None)

        headers["Content-Encoding"] = "UTF-8"
        headers["Content-Length"] = len(content)

        self.proxy_cache.set(cache_key, content, headers)

        # Send response to client
        self.send_response(response["status_code"])
        self.send_caching_headers(headers=headers, from_cache=False)
        self.wfile.write(content.encode("utf-8"))

    def forward_request(self, url, params, max_redirects=5):
        """
        Forward the request to the origin server and handle redirects if needed.

        Parameters:
            url (str): The URL to forward the request to.
            params (dict): Query parameters to include in the request.
            max_redirects (int): The maximum number of redirects to follow.
        """
        redirect_count = 0
        current_url = url

        headers = {
            key: value for key, value in self.headers.items() if key.lower() != "host"
        }
        headers["Connection"] = "close"  # Keep the connection alive

        while redirect_count < max_redirects:
            parsed_url = urlsplit(current_url)
            scheme = parsed_url.scheme
            host = parsed_url.netloc

            # Decide whether to use HTTPConnection or HTTPSConnection based on scheme
            if scheme == "https":
                connection = http.client.HTTPSConnection(
                    host, timeout=5, context=ssl._create_unverified_context()
                )
            else:
                connection = http.client.HTTPConnection(host, timeout=5)

            # Prepare the path with query parameters if any
            path = parsed_url.path or "/"
            if params:
                query_string = "&".join(f"{k}={v[0]}" for k, v in params.items())
                path += f"?{query_string}"

            # Explicitly set the Host header to match the origin server
            headers["Host"] = host

            try:
                # Send the GET request to the origin server
                connection.request("GET", path, headers=headers)
                response = connection.getresponse()

                # Check if the response is a redirect (301 or 302)
                if response.status in (301, 302):
                    location = response.getheader("Location")
                    if location:
                        # Update current_url with the new URL from the Location header
                        current_url = urljoin(current_url, location)
                        redirect_count += 1
                        print(
                            f"Redirecting to {current_url} (redirect {redirect_count})"
                        )
                        # Close the current connection and move to the next redirect
                        connection.close()
                        continue
                    else:
                        # If there's no Location header, return an error
                        self.send_error(
                            502,
                            "Bad Gateway",
                            "Redirect response without Location header.",
                        )
                        return None

                # If the status is not a redirect, return the response data and headers
                return {
                    "status_code": response.status,
                    "content": response.read(),
                    "headers": response.getheaders(),
                }

            except Exception as e:
                # Send an error if an exception occurs
                self.send_error(502, "Bad Gateway", f"Error forwarding request: {e}")
                return None

            finally:
                # Close the connection
                print("Closing connection")
                connection.close()

        # If max redirects exceeded, return an error
        self.send_error(508, "Loop Detected", "Too many redirects.")
        return None

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
