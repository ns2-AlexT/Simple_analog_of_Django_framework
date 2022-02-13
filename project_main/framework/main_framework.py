import quopri
from views import PageNotFound
from framework.requests import GetRequest, PostRequest


class MainFramework:
    def __init__(self, url_routes):
        self.url_routes = url_routes

    def __call__(self, environ, start_response):
        """
        Get path of VIEWS & method of request
        """
        get_path = environ['PATH_INFO']
        method_of_request = environ['REQUEST_METHOD']
        details_of_request = {}
        details_of_request['method of request'] = method_of_request

        """
        Handing GET & POST requests
        """
        if method_of_request == "GET":
            details_of_request['param of request'] = GetRequest.parse_get_request(environ)
        else:
            data_of_request = PostRequest.post_data_request(environ)
            details_of_request['param of request'] = MainFramework.decode_value(data_of_request)

        print(f'We have {method_of_request} request')
        print(details_of_request)

        """
        Control endswith / in urls
        """
        if not get_path.endswith('/'):
            get_path = f'{get_path}/'

        """
        Realize FC pattern
        """
        if get_path in self.url_routes:
            get_view = self.url_routes[get_path]
        else:
            get_view = PageNotFound()
        answer_code, answer_body = get_view(details_of_request)
        start_response(answer_code, [('Content-Type', 'text/html')])
        return [answer_body.encode('utf-8')]

    """
    Decode cyrillic symbols
    """
    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = quopri.decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data


class MainFrameworkDebug(MainFramework):
    def __init__(self, url_routes):
        self.debug_framework = MainFramework(url_routes)
        super().__init__(url_routes)

    def __call__(self, environ, start_response):
        print('Debug mode:')
        print(f'Type of request {environ["REQUEST_METHOD"]}')
        print(f'Type of request {environ}')
        # return self.debug_framework(environ, start_response)
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Debug mode']


class MainFrameworkFake(MainFramework):
    def __init__(self, url_routes):
        self.fake_framework = MainFramework(url_routes)
        super().__init__(url_routes)

    def __call__(self, environ, start_response):
        print('Fake mode is running')
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from fake framework']
