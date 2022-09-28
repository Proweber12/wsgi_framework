import html
from sqlite3 import connect
from copy import deepcopy
from quopri import decodestring

from patterns.behavioral_patterns import Subject
from patterns.architectural_pattern import DomainObject


class User:
    def __init__(self, name):
        self.name = name


class Seller(User):
    pass


class Buyer(User, DomainObject):
    def __init__(self, name):
        self.products = []
        super().__init__(name)


class UserFactory:
    types = {
        'seller': Seller,
        'buyer': Buyer
    }

    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)


class ProductPrototype:

    def clone(self):
        return deepcopy(self)


class Product(ProductPrototype, Subject):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.products.append(self)
        self.buyers = []
        super().__init__()

    def __getitem__(self, item):
        return self.buyers[item]

    def add_buyer(self, buyer: Buyer):
        self.buyers.append(buyer)
        buyer.products.append(self)
        self.notify()


class FoodProduct(Product):
    pass


class DomesticProduct(Product):
    pass


class ProductFactory:
    types = {
        'food': FoodProduct,
        'domestic': DomesticProduct
    }

    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)


class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.products = []

    def product_count(self):
        result = len(self.products)
        if self.category:
            result += self.category.product_count()
        return result


class Engine:
    def __init__(self):
        self.buyers = []
        self.sellers = []
        self.products = []
        self.categories = []

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_product(type_, name, category):
        return ProductFactory.create(type_, name, category)

    def get_product(self, name):
        for item in self.products:
            if item.name == name:
                return item
        return None

    def get_buyer(self, name) -> Buyer:
        for item in self.buyers:
            if item.name == name:
                return item

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return html.unescape(val_decode_str.decode('UTF-8'))


class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)


class BuyerMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'buyer'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            buyer = Buyer(name)
            buyer.id = id
            result.append(buyer)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Buyer(*result)
        else:
            raise FoodNotFoundException(f'food with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('db.sqlite')


class MapperRegistry:
    mappers = {
        'buyer': BuyerMapper,
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Buyer):

            return BuyerMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class FoodNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Food not found: {message}')
