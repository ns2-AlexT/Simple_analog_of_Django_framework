from time import time


class Routes:
    def __init__(self, routes, url):
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        self.routes[self.url] = cls()


class Debug:
    def __call__(self, cls):
        def get_def(some_def):
            def wrapper(*args, **kwargs):
                start_wrapper = time()
                result = some_def(*args, **kwargs)
                stop_wrapper = time()
                delta = stop_wrapper-start_wrapper
                print(f'Debug --> {some_def} spend time {delta:2.2f} ms')
                return result

            return wrapper

        return get_def(cls)
