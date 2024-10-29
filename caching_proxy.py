import click
from http.server import HTTPServer
from app.proxy_cache import ProxyCache
from app.proxy_http_req_handler import ProxyHTTPRequestHandler
from functools import wraps
import subprocess
import sys, os, signal


# Define the PID file path
PID_FILE = "proxy_server.pid"


def run_server(port, expiration, origin):
    print(f"Starting caching proxy server on port {port}")
    print(f"Origin server: {origin}")
    print(f"Cache expiration: {expiration} seconds")

    ProxyHTTPRequestHandler.proxy_cache = ProxyCache(expiration)
    ProxyHTTPRequestHandler.origin = origin
    server = HTTPServer(("127.0.0.1", port), ProxyHTTPRequestHandler)

    # Save the server's PID to a file
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.server_close()


def clear_server_cache():
    if ProxyHTTPRequestHandler.proxy_cache:
        ProxyHTTPRequestHandler.proxy_cache.clear_cache()
    else:
        print("No cache instance found.")


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option("-p", "--port", default=3000, help="Port to run the proxy server")
@click.option(
    "-e", "--expiration", default=300, help="Cache expiration time in seconds"
)
@click.option("-o", "--origin", help="Origin server to forward requests")
@click.option("--clear-cache", is_flag=True, help="Clear the cache and start fresh")
def cli(ctx, port, expiration, origin, clear_cache,):

    if not ctx.invoked_subcommand:
        if clear_cache:
            clear_server_cache()
            return

        """ if detached:
            print("Starting the server in detached mode...")

            # Run the server in a new process, detached from the terminal
            process = subprocess.Popen(
                [
                    sys.executable,
                    __file__,
                    "--port",
                    str(port),
                    "--expiration",
                    str(expiration),
                    "--origin",
                    origin,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
                start_new_session=True,  # Detaches the process
            )

            with open(PID_FILE, "w") as f:
                f.write(str(process.pid))

            print(f"Server running in detached mode on port {port}")
            return """

        # Run the server in foreground mode
        run_server(port, expiration, origin)


@cli.command("stop", help="Stop the proxy server")
def stop_server():
    try:
        # Check if PID file exists
        if not os.path.exists(PID_FILE):
            print("No running server found (PID file not found).")
            return

        # Read the PID from the file
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        # Attempt to terminate the process
        os.kill(pid, signal.SIGTERM)
        print(f"Server with PID {pid} has been stopped.")

        # Remove the PID file after stopping the server
        os.remove(PID_FILE)
    except ProcessLookupError:
        print(f"No process found with PID {pid}. Removing stale PID file.")
        os.remove(PID_FILE)
    except Exception as e:
        print(f"An error occurred while stopping the server: {e}")
