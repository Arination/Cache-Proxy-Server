from http.server import HTTPServer
from app.proxy_cache import ProxyCache
from app.proxy_http_req_handler import ProxyHTTPRequestHandler
import os, signal, sys
import asyncio
from concurrent.futures import ThreadPoolExecutor


class ProxyServer: 
    PID_FILE = "proxy_server.pid"
    LOCK_FILE = "proxy_server.lock"

    def create_lock(self):
        """Creates a lock file to prevent multiple instances."""
        if os.path.exists(self.LOCK_FILE):
            print("Server is already running. Exiting.")
            sys.exit(1)
        with open(self.LOCK_FILE, "w") as lock_file:
            lock_file.write("locked")

    def remove_lock(self):
        """Removes the lock file."""
        if os.path.exists(self.LOCK_FILE):
            os.remove(self.LOCK_FILE)

    async def start_server_async(self, port, expiration, origin):
        """Start the server asynchronously and run it as a background task."""
        # Define the server
        self.proxy_cache = ProxyCache(expiration)
        ProxyHTTPRequestHandler.proxy_cache = self.proxy_cache
        ProxyHTTPRequestHandler.origin = origin

        self.server = HTTPServer(("127.0.0.1", port), ProxyHTTPRequestHandler)

        # Save the server's PID to a file
        with open(self.PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        self.create_lock()

        self.server.serve_forever()
        print(f"Started caching proxy server on port {port}")

    async def run_server_async(self, port, expiration, origin):
        """Run the HTTP server asynchronously."""
        loop = asyncio.get_event_loop()
        self.server_task = asyncio.create_task(self.start_server_async(port, expiration, origin))
        await loop.run_forever()

    def clear_server_cache(self):
        proxy_cache = ProxyCache()
        proxy_cache.clear_cache()

    def stop_server(self):
        try:
            # Check if PID file exists
            if not os.path.exists(self.PID_FILE):
                print("No running server found (PID file not found).")
                return

            # Read the PID from the file
            with open(self.PID_FILE, "r") as f:
                pid = int(f.read().strip())

            # Attempt to terminate the process
            os.kill(pid, signal.SIGTERM)
            print(f"Server with PID {pid} has been stopped.")

            # Remove the PID file after stopping the server
            os.remove(self.PID_FILE)
            self.remove_lock()

            print("Cache Proxy Server Stopped")
        except ProcessLookupError:
            print(f"No process found with PID {pid}. Removing stale PID file.")
            os.remove(self.PID_FILE)
        except Exception as e:
            print(f"An error occurred while stopping the server: {e}")
