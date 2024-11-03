import click
from app.server import ProxyServer


class CommandLineRunner:
    # Define the PID file path
    PID_FILE = "proxy_server.pid"

    def __init__(self):
        self.port = 3000
        self.expiry = 18000
        self.origin = None
        self.proxy_server = None

    @click.command("server", help="Start the caching proxy server")
    @click.pass_obj
    @click.option("-p", "--port", default=3000, help="Port to run the proxy server")
    @click.option(
        "-e", "--expiration", default=300, help="Cache expiration time in seconds"
    )
    @click.option("-o", "--origin", help="Origin server to forward requests")
    @click.option("--clear-cache", is_flag=True, help="Clear the cache and start fresh")
    def start(self, port, expiration, origin, clear_cache):

        if clear_cache:
            ProxyServer.clear_server_cache()
            return

        proxy_server = ProxyServer()
        
        proxy_server.run_server(port, expiration, origin)

    @click.command("stop", help="Stop the proxy server")
    @click.pass_obj
    def stop_server(self):
        """try:
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
            print(f"An error occurred while stopping the server: {e}")"""

        """ if self.proxy_server is not None:
            self.proxy_server.stop_server()
        else:
            print("No server instance found.") """
            
        server = ProxyServer()
        server.stop_server()


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    ctx.obj = CommandLineRunner()

cli.add_command(CommandLineRunner.start)
cli.add_command(CommandLineRunner.stop_server)

def main():
    cli()
