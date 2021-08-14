class GetRequests:

    @staticmethod
    def parse_input_data(data: str):
        result = {}
        if data:
            # делим параметры через &
            params = data.split('&')
            for item in params:
                # делим ключ и значение через =
                k, v = item.split('=')
                result[k] = v
        return result

    @staticmethod
    def get_request_params(environ):
        # получаем параметры запроса
        query_string = environ['QUERY_STRING']
        # превращаем параметры в словарь
        request_params = GetRequests.parse_input_data(query_string)
        return request_params


class PostRequests:

    @staticmethod
    def parse_input_data(data: str):
        result = {}
        if data:
            print(data)
            # делим параметры через &
            params = data.split('&')
            for item in params:
                # делим ключ и значение через =
                k, v = item.split('=')
                result[k] = v
            # Делим строку параметров через =
            # params = data.split('=')
            # for item in params:
            #     # Параметры получаются вида:------WebKitFormBoundaryKkr1O0ccG10MxQtCContent-Disposition: form-data; name
            #     # или: "firstname"wwww------WebKitFormBoundaryKkr1O0ccG10MxQtCContent-Disposition: form-data; name
            #     # делим их по первому вхождению '------' на три части, берем первую
            #     item3 = item.partition("------")
            #     item = item3[0]
            #     # print(f'***** {item}')
            #     # делим ключ и значение через ", предварительно убрав первый символ '"'
            #     if item:
            #         item = item[1:]
            #         print(item)
            #         k, v = item.split('"')
            #         result[k] = v
        # В итоге получается словарь нужного вида:
        # {'firstname': 'wwww', 'lastname': 'dddddd', 'Email': 'galina_87@mail.ru', 'sex': 'female',
        # 'type1': 'high', 'textmail': 'bhbbhbggfhgfjdfg'}
        return result

    @staticmethod
    def get_wsgi_input_data(env) -> bytes:
        # получаем длину тела
        content_length_data = env.get('CONTENT_LENGTH')
        # приводим к int
        content_length = int(content_length_data) if content_length_data else 0
        print(content_length)
        # считываем данные, если они есть
        data = env['wsgi.input'].read(content_length) if content_length > 0 else b''
        return data

    def parse_wsgi_input_data(self, data: bytes) -> dict:
        result = {}
        if data:
            # декодируем данные
            data_str = data.decode(encoding='utf-8')
            data_str = data_str.replace("\n", "")
            data_str = data_str.replace("\r", "")
            # собираем их в словарь
            result = self.parse_input_data(data_str)
        return result

    def get_request_params(self, environ):
        # получаем данные
        data = self.get_wsgi_input_data(environ)
        # превращаем данные в словарь
        data = self.parse_wsgi_input_data(data)
        return data
