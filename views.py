from wsgi_framework.templator import render
from patterns.creational_patterns import Engine
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import ListView, CreateView, BaseSerializer, EmailNotifier, SmsNotifier

site = Engine()
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()

routes = {}


@AppRoute(routes=routes, url='/')
class Index:
    @Debug('Index call')
    def __call__(self, request):
        return '200 OK', render('index.html', objects_list=site.categories)


@AppRoute(routes=routes, url='/examples/')
class Examples:
    def __call__(self, request):
        return '200 OK', render('examples.html', date=request.get('date', None))


@AppRoute(routes=routes, url='/page/')
class Page:
    def __call__(self, request):
        return '200 OK', render('page.html', date=request.get('date', None))


@AppRoute(routes=routes, url='/another_page/')
class AnotherPage:
    def __call__(self, request):
        return '200 OK', render('another_page.html', date=request.get('date', None))


@AppRoute(routes=routes, url='/contact/')
class Contact:
    def __call__(self, request):
        return '200 OK', render('contact.html', date=request.get('date', None))
    

@AppRoute(routes=routes, url='/product_list/')
class ProductsList:
    @Debug('Product_list call')
    def __call__(self, request):
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('product_list.html',
                                    objects_list=category.products,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK', render('product_list.html',
                                    error='No products have been added yet')


@AppRoute(routes=routes, url='/create_product/')
class CreateProduct:
    category_id = -1

    @Debug('Create_product call')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                product = site.create_product('food', name, category)

                product.observers.append(sms_notifier)
                product.observers.append(email_notifier)

                site.products.append(product)

            return '200 OK', render('product_list.html',
                                    objects_list=category.products,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_product.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', render('create_product.html', error='No categories have been added yet')


@AppRoute(routes=routes, url='/create_category/')
class CreateCategory:
    @Debug('Create_category call')
    def __call__(self, request):

        if request['method'] == 'POST':

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('index.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html',
                                    categories=categories)


@AppRoute(routes=routes, url='/category_list/')
class CategoryList:
    @Debug('Category_list call')
    def __call__(self, request):
        return '200 OK', render('category_list.html',
                                objects_list=site.categories)


@AppRoute(routes=routes, url='/copy_product/')
class CopyProduct:
    @Debug('Copy_product call')
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_product = site.get_product(name)
            if old_product:
                new_name = f'copy_{name}'
                new_product = old_product.clone()
                new_product.name = new_name
                site.products.append(new_product)

            return '200 OK', render('product_list.html',
                                    objects_list=site.products,
                                    name=new_product.category.name)
        except KeyError:
            return '200 OK', 'No products have been added yet'


@AppRoute(routes=routes, url='/buyer_list/')
class BuyerListView(ListView):
    queryset = site.buyers
    template_name = 'buyer_list.html'


@AppRoute(routes=routes, url='/create_buyer/')
class BuyerCreateView(CreateView):
    template_name = 'create_buyer.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('buyer', name)
        site.buyers.append(new_obj)


@AppRoute(routes=routes, url='/add_buyer/')
class AddBuyerByProductCreateView(CreateView):
    template_name = 'add_buyer.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['products'] = site.products
        context['buyers'] = site.buyers
        return context

    def create_obj(self, data: dict):
        product_name = data['product_name']
        product_name = site.decode_value(product_name)
        product = site.get_product(product_name)
        buyer_name = data['buyer_name']
        buyer_name = site.decode_value(buyer_name)
        buyer = site.get_buyer(buyer_name)
        product.add_buyer(buyer)


@AppRoute(routes=routes, url='/api/')
class ProductApi:
    @Debug(name='ProductApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.products).save()
