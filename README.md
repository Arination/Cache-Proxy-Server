# Caching Proxy Server

This is a simple caching proxy server CLI tool built with Python and Click. The server forwards requests to a specified origin server, caches the responses, and returns cached responses for duplicate requests. This can help reduce load on the origin server and improve response times for repeat requests.

Project URL: https://github.com/Puru80/Python-Pro

## Features

- **Request Forwarding**: Forwards client requests to a specified origin server.
- **Response Caching**: Caches the origin server responses, serving cached responses for repeated requests.
- **Cache Headers**: Adds headers to indicate whether the response is from the cache or the origin server.
- **Clear Cache**: Supports a CLI command to clear the cache.
