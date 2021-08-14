import abc
import copy
import quopri


from patterns.behavioral_patterns import Subject
from patterns.architectural_system_pattern_unit_of_work import DomainObject


# абстрактный пользователь
class User:
    model = 'User'

    def __init__(self, data):
        self.model = 'User'
        self.first_name = Engine.decode_value(data['first_name'])
        self.last_name = Engine.decode_value(data['last_name'])
        self.login = Engine.decode_value(data['login'])
        self.email = Engine.decode_value(data['email'])
        self.sex = Engine.decode_value(data['sex'])
        self.age = Engine.decode_value(data['age'])
        self.password = Engine.decode_value(data['password'])
        self.type_user = 'student'
        if 'id' in data:
            self.id = Engine.decode_value(data['id'])
        else:
            self.id = None


# преподаватель
class Teacher(User):
    def __init__(self, data):
        self.type_user = 'teacher'
        User.__init__(self, data)

    def __call__(self):
        return self


# студент
class Student(User, DomainObject):
    def __init__(self, data):
        User.__init__(self, data)
        self.type_user = 'student'

    def __call__(self):
        return self


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, data):
        return cls.types[type_](data)


# порождающий паттерн Прототип - Курс
class CoursePrototype:
    # прототип курсов обучения

    def clone(self):
        return copy.deepcopy(self)


# Пронаследовалась от двух классов, так как нужно, чтоб курс так же был и Subject для возможности отправки
# уведомлений через наблюдателей
class Course(CoursePrototype, Subject, DomainObject):
    auto_id = 0
    model = 'Course'

    def __init__(self, data):
        Subject.__init__(self)
        self.model = 'Course'
        # self.id = Course.auto_id
        # Course.auto_id += 1
        self.name = Engine.decode_value(data['name'])
        self.id_category = Engine.decode_value(data['id_category'])
        if 'id' in data:
            self.id = Engine.decode_value(data['id'])
        else:
            self.id = None
        self.students = []

    # Переопределила clon() так как нужно увеличивать Course.auto_id += 1 и id курса должен быть уникальным
    def clone(self):
        # print(Course.auto_id)
        new_course = copy.deepcopy(self)
        new_course.id = Course.auto_id
        Course.auto_id += 1
        return new_course

    def __iter__(self):
        return iter(self.students)


class StudentsCourses(DomainObject):
    model = 'StudentsCourses'

    def __init__(self, data):
        self.model = 'StudentsCourses'
        self.id_course = Engine.decode_value(data['id_course'])
        self.login_student = Engine.decode_value(data['login_student'])


class CoursesCategories(DomainObject):
    model = 'CoursesCategories'

    def __init__(self, data):
        if 'id' in data:
            self.id = Engine.decode_value(data['id'])
        else:
            self.id = None
        self.model = 'CoursesCategories'
        self.id_category = Engine.decode_value(data['id_course'])
        self.id_course = Engine.decode_value(data['id_course'])


# Категория
class Category(DomainObject):
    auto_id = 0
    model = 'Category'

    def __init__(self, data):
        self.model = 'Category'
        # self.id = Category.auto_id
        # Category.auto_id += 1
        self.name = Engine.decode_value(data['name'])
        # self.category = Engine.decode_value(data['category'])
        if 'id' in data:
            self.id = Engine.decode_value(data['id'])
        else:
            self.id = None
        self.course = []

    def course_count(self):
        result = len(self.course)
        # if self.category:
        #     result += self.category.course_count()
        return result

    def __iter__(self):
        return iter(self.course)


# порождающий паттерн Абстрактная фабрика - фабрика курсов
class CourseFactory:
    course_ = Course

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, data):
        return cls.course_(data)


# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.curses = []
        self.categorys = []

    @staticmethod
    def create_category(data):
        return Category(data)

    @staticmethod
    def create_courses_student(data):
        return StudentsCourses(data)

    @staticmethod
    def create_category_courses(data):
        return CoursesCategories(data)

    def find_course_by_id(self, id_course):
        for item in self.curses:
            # print('item', item.id)
            # print(id_course)
            if int(item.id) == int(id_course):
                return item
        raise Exception(f'Нет курса с id = {id_course}')

    def find_category_by_id(self, id_category):
        for item in self.categorys:
            # print('item', item.id)
            # print(id_course)
            if int(item.id) == int(id_category):
                return item
        raise Exception(f'Нет категории с id = {id_category}')

    @staticmethod
    def create_course(data):
        return CourseFactory.create(data)

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')

    @staticmethod
    def create_user(data, type_user):
        return UserFactory.create(data, type_user)

    def get_student(self, name) -> Student:
        for item in self.students:
            if item.login == name:
                return item
        raise Exception(f'Нет студента с логином = {name}')


# порождающий паттерн Синглтон
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


# Паттерн Стратегия - добавление в логгер стратегии...
# наверное нужно перенести в поведенчиские патерны, но пока тут
# Написала две стратегии в поток вывода и в файл, соответственно можно расширить варианты
class LoggerStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def log(self, text):
        pass


class LoggerInStdout(LoggerStrategy):

    def log(self, text):
        print(f'log--->{text}')


class LoggerInFile(LoggerStrategy):

    def __init__(self, file):
        self.file = file

    def log(self, text):
        f = open(self.file, 'a', encoding="utf-8")
        f.write(f'{text}\n')
        f.close()


class Logger(metaclass=SingletonByName):

    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy

    def log(self, text):
        self.strategy.log(text)

