from wsgiref.simple_server import make_server

from framework.main_framework import MainFramework, MainFrameworkDebug, MainFrameworkFake
from views import routes

port = 8003
make_framework = MainFramework(routes)


with make_server('', port, make_framework) as server:
    print(f'Server is up on {port}')
    server.serve_forever()
