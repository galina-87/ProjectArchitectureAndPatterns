import jsonpickle
from fwarg import render


# поведенческий паттерн - наблюдатель
class Observer:

    def update(self, subject):
        pass


class Subject:

    def __init__(self):
        self.observers = []

    def notify(self):
        for item in self.observers:
            item.update(self)


class SmsNotifier(Observer):

    def update(self, subject):
        # Как раз использование итерраций для курса
        for item in subject:
            print(f'SMS for {item}-> изменения на курсе: {subject.name}')


class EmailNotifier(Observer):

    def update(self, subject):
        # И тут тоже итеррации для курса - перебор студентов курса =)))
        for item in subject:
            print(f'EMAIL for {item}-> изменения на курсе: {subject.name}')


# поведенческий паттерн - Шаблонный метод
class TemplateView:
    template_name = 'template.html'

    def get_context_data(self):
        return {}

    def get_template(self):
        return self.template_name

    def render_template_with_context(self):
        template_name = self.get_template()
        context = self.get_context_data()
        print(f'context--> {context}')
        return '200 OK', render(template_name, **context)

    def __call__(self, request):
        return self.render_template_with_context()


class ListView(TemplateView):
    queryset = []
    template_name = 'list.html'
    context_object_name = 'objects_list'

    def get_queryset(self):
        # print(self.queryset)
        return self.queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}
        return context


class CreateView(TemplateView):
    template_name = 'create.html'

    @staticmethod
    def get_request_data(request):
        return request['data']

    def create_obj(self, data):
        pass

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = self.get_request_data(request)
            self.create_obj(data)

            return self.render_template_with_context()
        else:
            return super().__call__(request)


# Добавила шаблон для update объекта, queryset тут нужен как вспомогательный элемент - для возможности
# создания выпадающих списков на страничке, может можно как то по другому, но так работает тоже....
class UpdateView(TemplateView):
    template_name = 'update.html'
    queryset = []
    object_update = object
    context_object_name = 'objects_list'

    def update_obj(self, data):
        pass

    def get_object_update(self, data):
        pass

    def get_context_data(self):
        object_update = self.object_update
        queryset = self.queryset
        context_object_name = self.context_object_name
        context = {'object_update': object_update, context_object_name: queryset}
        # print(queryset)
        return context

    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост
            data = request['data']
            # print(data)
            self.update_obj(data)

            return self.render_template_with_context()
        else:
            id_obj = request['request_params']['object_update']
            # print(id_obj)
            self.get_object_update(id_obj)
            return super().__call__(request)


class SerializerView:

    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return jsonpickle.dumps(self.obj)

    @staticmethod
    def load(data):
        return jsonpickle.loads(data)
