from time import time


# структурный паттерн - Декоратор
class AppRoute:
    def __init__(self, routes, url):
        '''
        Сохраняем значение переданного параметра, url будем получать из имени переданного класса
        '''
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        '''
        декоратор
        '''
        # if str(cls.__name__).lower() == 'Main'.lower() or str(cls.__name__).lower() == 'Index'.lower():
        #     url = '/'
        # else:
        #     url = '/' + str(cls.__name__).lower() + '/'
        # self.url = url
        self.routes[self.url] = cls()


# структурный паттерн - Декоратор
class Debug:

    def __call__(self, cls):
        '''
        декоратор
        '''

        def timeit(method):
            '''
            нужен для того, чтобы декоратор класса обернул в timeit
            каждый метод декорируемого класса
            '''

            def timed(*args, **kw):
                ts = time()
                result = method(*args, **kw)
                te = time()
                delta = te - ts

                # Получение имени класса
                class_ = str(method).partition(' ')[2]
                class_ = class_.partition('.')[0]
                print(f'Debug----> Функция {method.__name__} класса {class_}'
                      f' модуля {method.__module__} выполнялась {delta:2.2f} ms')
                return result

            return timed

        return timeit(cls)
