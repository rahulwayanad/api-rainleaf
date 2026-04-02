import sys
import os

APP_DIR = os.path.dirname(__file__)
sys.path.insert(0, APP_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(APP_DIR, '.env'))

import asyncio
from main import app


def application(environ, start_response):
    # Build ASGI scope from WSGI environ
    headers = []
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').lower().encode()
            headers.append((header_name, value.encode()))

    scope = {
        'type': 'http',
        'asgi': {'version': '3.0'},
        'http_version': '1.1',
        'method': environ['REQUEST_METHOD'],
        'headers': headers,
        'path': environ.get('PATH_INFO', '/'),
        'query_string': environ.get('QUERY_STRING', '').encode(),
        'root_path': environ.get('SCRIPT_NAME', ''),
        'scheme': environ.get('wsgi.url_scheme', 'https'),
        'server': (environ.get('SERVER_NAME', 'localhost'), int(environ.get('SERVER_PORT', 80))),
    }

    try:
        content_length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(content_length) if content_length > 0 else b''
    except Exception:
        body = b''
    response_started = []
    response_body = []

    async def run():
        async def receive():
            return {'type': 'http.request', 'body': body, 'more_body': False}

        async def send(message):
            if message['type'] == 'http.response.start':
                status_code = message['status']
                raw_headers = [(k.decode(), v.decode()) for k, v in message.get('headers', [])]
                response_started.append((status_code, raw_headers))
            elif message['type'] == 'http.response.body':
                response_body.append(message.get('body', b''))

        await app(scope, receive, send)

    asyncio.run(run())

    status_code, raw_headers = response_started[0]
    status_map = {200: '200 OK', 201: '201 Created', 400: '400 Bad Request',
                  401: '401 Unauthorized', 403: '403 Forbidden', 404: '404 Not Found',
                  422: '422 Unprocessable Entity', 500: '500 Internal Server Error'}
    status = status_map.get(status_code, f'{status_code} Unknown')
    start_response(status, raw_headers)
    return response_body
