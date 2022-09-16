from datetime import date
from views import Index, Examples, Page, AnotherPage, Contact


def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/examples/': Examples(),
    '/page/': Page(),
    '/another_page/': AnotherPage(),
    '/contact/': Contact(),
}
