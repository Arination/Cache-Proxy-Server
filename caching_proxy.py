import click
from app.server import ProxyServer


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(ProxyServer)


@cli.command("server", help="Start the caching proxy server")
@click.pass_obj
@click.option("-p", "--port", default=3000, help="Port to run the proxy server")
@click.option(
    "-e", "--expiration", default=300, help="Cache expiration time in seconds"
)
@click.option("-o", "--origin", help="Origin server to forward requests")
@click.option("--clear-cache", is_flag=True, help="Clear the cache and start fresh")
def start(obj, port, expiration, origin, clear_cache):

    if clear_cache:
        obj.clear_server_cache()
        return

    proxy_server = ProxyServer()

    proxy_server.run_server(port, expiration, origin)


@cli.command("stop", help="Stop the proxy server")
@click.pass_obj
def stop_server(obj):
    obj.stop_server()

def main():
    cli(obj = ProxyServer())
