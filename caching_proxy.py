import click
from http.server import HTTPServer
from app.proxy_cache import ProxyCache
from app.proxy_http_req_handler import ProxyHTTPRequestHandler

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


""" @click.group(context_settings=CONTEXT_SETTINGS)
def caching_proxy():
    pass """


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option("-p", "--port", default=3000, help="Port to run the proxy server")
@click.option(
    "-e", "--expiration", default=300, help="Cache expiration time in seconds"
)
@click.option("-o", "--origin", required=True, help="Origin server to forward requests")
def cli(ctx, port, expiration, origin):
    print(f"Starting caching proxy server on port {port}")
    print(f"Origin server: {origin}")
    print(f"Cache expiration: {expiration} seconds")

    ProxyHTTPRequestHandler.proxy_cache = ProxyCache(expiration)
    ProxyHTTPRequestHandler.origin = origin
    server = HTTPServer(("localhost", port), ProxyHTTPRequestHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.server_close()


@cli.command()
def start():
    pass
