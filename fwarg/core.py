import quopri
from fwarg.requests import GetRequests, PostRequests


class PageNotFound:
    def __call__(self, request):
        return '404 NOT_FOUND', '404, Page not found'


class ApplicationFW:

    def __init__(self, urlpatterns: dict, front_controllers: list):
        """
        :param urlpatterns: словарь связок url: view
        :param front_controllers: список front controllers
        """
        self.urlpatterns = urlpatterns
        self.front_controllers = front_controllers

    def __call__(self, env, start_response):
        # текущий url
        print(env)
        path = env['PATH_INFO']
        if not path.endswith('/'):
            path = f'{path}/'

        request = {'method': env['REQUEST_METHOD']}

        if path in self.urlpatterns:
            for controller in self.front_controllers:
                controller(request)
            # вызываем view, получаем результат
            view = self.urlpatterns[path]
        else:
            view = PageNotFound()

        if request['method'] == 'POST':
            # print(env)
            data = PostRequests().get_request_params(env)
            request['data'] = data
            print(f'Запрос POST: {ApplicationFW.decode_value(data)}')
            # вывод сообщения в консоль
            # print(data['textmail'])
        if request['method'] == 'GET':
            request_params = GetRequests().get_request_params(env)
            request['request_params'] = request_params
            print(f'Запрос GET: {request_params}')

        code, text = view(request)
        # возвращаем заголовки
        start_response(code, [('Content-Type', 'text/html')])
        # возвращаем тело ответа
        return [text.encode('utf-8')]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = quopri.decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data


# Новый вид WSGI-application.
# Первый — логирующий (такой же, как основной,
# только для каждого запроса выводит информацию
# (тип запроса и параметры) в консоль.
class DebugApplication(ApplicationFW):

    def __init__(self, routes_obj, fronts_obj):
        self.application = ApplicationFW(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        print('DEBUG MODE')
        print(env)
        return self.application(env, start_response)


# Новый вид WSGI-application.
# Второй — фейковый (на все запросы пользователя отвечает:
# 200 OK, Hello from Fake).
class FakeApplication(ApplicationFW):

    def __init__(self, routes_obj, fronts_obj):
        self.application = ApplicationFW(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Fake']