<<<<<<< Updated upstream
=======
import html
from quopri import decodestring
from wsgi_framework.http_requests import GetRequests, PostRequests


>>>>>>> Stashed changes
class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class Framework:

    def __init__(self, routes_obj, fronts_obj):
        self.routes_lst = routes_obj
        self.fronts_lst = fronts_obj

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        if not path.endswith('/'):
            path = f'{path}/'

        if path in self.routes_lst:
            view = self.routes_lst[path]
        else:
            view = PageNotFound404()
        request = {}
        for front in self.fronts_lst:
            front(request)
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]
<<<<<<< Updated upstream
=======

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = v.replace('%', '=').replace("+", " ").encode('UTF-8')
            val_decode_str = decodestring(val).decode('UTF-8')
            new_data[k] = html.unescape(val_decode_str)
        return new_data
>>>>>>> Stashed changes
