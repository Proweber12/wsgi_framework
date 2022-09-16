from wsgi_framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None))


class Examples:
    def __call__(self, request):
        return '200 OK', render('examples.html', date=request.get('date', None))


class Page:
    def __call__(self, request):
        return '200 OK', render('page.html', date=request.get('date', None))


class AnotherPage:
    def __call__(self, request):
        return '200 OK', render('another_page.html', date=request.get('date', None))


class Contact:
    def __call__(self, request):
        return '200 OK', render('contact.html', date=request.get('date', None))
