# coding: utf-8

from wsgiref.simple_server import make_server

from wsgi.middlewares import CORSMiddleware, ResponseTimingMiddleware
from wsgi.app import application

app = ResponseTimingMiddleware(
    CORSMiddleware(
        app=application,
        whitelist=['http://localhost:9000', 'http://localhost:9001']))

if __name__ == '__main__':
    print("Server is running at http://localhost:8888 . Press Ctrl+C to stop.")
    server = make_server('localhost', 8888, app)
    server.serve_forever()
