from datetime import date
from views import Index, Examples, Page, AnotherPage, Contact, ProductsList, CreateProduct, CategoryList, CreateCategory, CopyProduct


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
    '/product_list/': ProductsList(),
    '/create_product/': CreateProduct(),
    '/category_list/': CategoryList(),
    '/create_category/': CreateCategory(),
    '/copy_product/': CopyProduct(),
}
