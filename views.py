from fwarg import render
from patterns.architectural_system_pattern_mappers import MapperRegistry
from patterns.architectural_system_pattern_unit_of_work import UnitOfWork
from patterns.generative_patterns import Engine, Logger, LoggerInFile, LoggerInStdout
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import CreateView, ListView, UpdateView, SerializerView, EmailNotifier, SmsNotifier

base = Engine()

# mapper = MapperRegistry.get_current_mapper('Course')
# base.curses = mapper.all()
#
# mapper = MapperRegistry.get_current_mapper('Category')
# base.categorys = mapper.all()
#
# mapper = MapperRegistry.get_current_mapper('User')
# base.students = mapper.all()

# Создаем наблюдателей для курсов
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()

# Попробовала паттерн "Стратегия", только у меня сам логгер в файле generative_patterns.py -
# - там же дописала стратегию...
log_strategy_one = LoggerInFile('main_log.txt')
logger_main = Logger('main', log_strategy_one)

# подключила для проверки работы - обе ли стратегии рабочие,
# соответственно логгер нужно еще один создать (с другим именем), чтобы они отдельно работали
log_strategy_two = LoggerInStdout()
logger_main_stdout = Logger('additionally', log_strategy_two)

UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}


@AppRoute(routes=routes, url='/')
class Main:
    @Debug()
    def __call__(self, request):
        #  тут добавила создание текущих списков из базы - на них много функционала завязано,
        #  переписать пока не успеваю, хотя надо завязать функционал на данных из БД
        mapper = MapperRegistry.get_current_mapper('Course')
        base.curses = mapper.all()

        mapper = MapperRegistry.get_current_mapper('Category')
        base.categorys = mapper.all()

        mapper = MapperRegistry.get_current_mapper('User')
        base.students = mapper.all()

        for curse in base.curses:
            mapper = MapperRegistry.get_current_mapper('StudentsCourses')
            students = mapper.find_by_field('id_course', int(curse.id))
            # print(f'студенты при открытии главной-->{students}')
            for student in students:
                # print(f'студент курса-->{student}')
                # print(f'студент курса логин-->{student.login_student}')
                curse.students.append(student.login_student)
            # print(f'студентs курса {curse.id}-->{curse.students}')
            cat = base.find_category_by_id(curse.id_category)
            print(f'категория курса {curse.name}(id-{curse.id})-->{cat.id}')
            cat.course.append(curse.id)
            print(f'курсы категории-->{cat.course}')
            print(f'курсы категории-->{cat.course_count()}')

        # for category in base.categorys:
        #     mapper = MapperRegistry.get_current_mapper('CoursesCategories')
        #     courses = mapper.find_by_field('id_category', int(category.id))
        #     # print(f'студенты при открытии главной-->{students}')
        #     for curse in courses:
        #         # print(f'студент курса-->{student}')
        #         # print(f'студент курса логин-->{student.login_student}')
        #         category.course.append(curse.id_course)
        #     # print(f'студентs курса {curse.id}-->{curse.students}')

        logger_main.log('Главная страница')
        logger_main_stdout.log('Главная страница ---> stdout')
        return '200 OK', render('index.html')


@AppRoute(routes=routes, url='/about/')
class About:
    @Debug()
    def __call__(self, request):
        logger_main.log('Страница О нас')
        logger_main_stdout.log('О нас страница ---> stdout')
        return '200 OK', render('about.html')


@AppRoute(routes=routes, url='/contacts/')
class Contacts:
    @Debug()
    def __call__(self, request):
        logger_main.log('Контакты')
        return '200 OK', render('contacts.html')


@AppRoute(routes=routes, url='/curseslist/')
class CursesList:
    @Debug()
    def __call__(self, request):
        logger_main.log('Список курсов')
        mapper = MapperRegistry.get_current_mapper('Course')
        curses_list = mapper.all()
        return '200 OK', render('curses.html', curses_list=curses_list)


# class CursesListForCategory:
#     def __call__(self, request):
#         return '200 OK', render('curses.html', category=base.categorys)


@AppRoute(routes=routes, url='/categorylist/')
class CategoryList:
    @Debug()
    def __call__(self, request):
        logger_main.log('Список категорий')
        # mapper = MapperRegistry.get_current_mapper('Category')
        # list_cat = mapper.all()
        list_cat = base.categorys
        return '200 OK', render('category.html', category_list=list_cat)


@AppRoute(routes=routes, url='/cursescreate/')
class CursesCreate:
    @Debug()
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            data['name'] = base.decode_value(data['name'])
            category = base.find_category_by_id(data['id_category'])
            logger_main.log('Создание курса--->' + data['name'] + '(' + str(category.id) + ')')
            curse = base.create_course(data)

            # mapper = MapperRegistry.get_current_mapper('Course')
            # mapper.insert(curse)

            curse.mark_new()
            UnitOfWork.get_current().commit()
            mapper = MapperRegistry.get_current_mapper('Course')
            base.curses = mapper.all()
            id_courses = []

            # При создании курса добавляем наблюдателей, при обновлении будем отсылать сообщения студентам курса
            curse.observers.append(email_notifier)
            curse.observers.append(sms_notifier)
            # category.course.append(curse)
            # base.curses.append(curse)
            # print(curse.observers)

            return '200 OK', render('curses.html', curses_list=base.curses)
        else:
            if base.categorys:
                logger_main.log('Страница--->Создание курса')
                return '200 OK', render('create_curse.html', category_list=base.categorys)
            else:
                logger_main.log('Create a category before creating a course!--->Отстуствуют категории')
                return '200 OK', '<h1>Create a category before creating a course!' \
                                 '<br><a href="/categorycreate/">Create a category</a><h1>'


@AppRoute(routes=routes, url='/curse/')
class Curse:
    @Debug()
    def __call__(self, request):
        # find_by_id
        id_course = request['request_params']['course']
        mapper = MapperRegistry.get_current_mapper('Course')
        course = mapper.find_by_id(id_course)
        logger_main.log('Страница курса ' + id_course)

        # course = base.find_course_by_id(id_course)
        #  тут просто проверяла итеррируемость курса - использование итерратора в Наблюдателях
        # print(f'course ---> {course.name}')
        # for item in course:
        #     print(f'student ---> {item}')
        return '200 OK', render('curse.html', course=course)


@AppRoute(routes=routes, url='/cursecopy/')
class CurseCopy:
    @Debug()
    def __call__(self, request):
        id_course = request['request_params']['course_id']
        logger_main.log('Копирование курса ' + id_course)
        course = base.find_course_by_id(id_course)
        new_course = course.clone()
        category = base.find_category_by_id(course.category)
        category.course.append(new_course)
        base.curses.append(new_course)
        # print(new_course.category)
        # print(new_course.id)
        return '200 OK', render('curses.html', curses_list=base.curses)


@AppRoute(routes=routes, url='/categorycreate/')
class CategoryCreate:
    @Debug()
    def __call__(self, request):
        if request['method'] == 'POST':
            # print(request)
            data = request['data']

            name = data['name']
            name = base.decode_value(name)

            category_id = data.get('category_id')

            category = None
            # if category_id:
            #     category = base.find_category_by_id(int(category_id))

            new_category = base.create_category(data)

            # mapper = MapperRegistry.get_current_mapper('Category')
            # mapper.insert(new_category)

            new_category.mark_new()
            UnitOfWork.get_current().commit()

            # base.categorys.append(new_category)
            logger_main.log('Создание категории ' + name)
            return '200 OK', render('category.html', category_list=base.categorys)
        else:
            categorys = base.categorys
            logger_main.log('Страница--->Создание категории')
            return '200 OK', render('create_category.html')


@AppRoute(routes=routes, url='/registrationuser/')
class RegistrationUser(CreateView):
    template_name = 'registration_user.html'

    def create_obj(self, data):
        new_obj = base.create_user('student', data)

        new_obj.mark_new()
        UnitOfWork.get_current().commit()

        logger_main.log(f'создан студент, логин {new_obj.login}')
        base.students.append(new_obj)


@AppRoute(routes=routes, url='/studentlist/')
class StudentList(ListView):
    # queryset = base.students
    template_name = 'student_list.html'

    # Переопределила для возможности открывать список с отбором по курсу
    def __call__(self, request):
        # print(f'----> req ---> {request}')
        data = request['request_params']

        if 'course_students' in data:
            self.queryset = []

            # list_stud = base.decode_value(data['course_students'])[2:-2].split('\', \'')
            course = base.find_course_by_id(int(data['course_students']))
            list_stud = course.students
            print(f'list--->{list_stud}')
            for item in list_stud:
                # item = base.decode_value(item)
                # print(f'item--->{item}')
                self.queryset.append(base.get_student(item))
            logger_main.log(f'Вывод списка студентов курса')
        else:
            logger_main.log(f'Вывод списка всех студентов')
            # self.queryset = base.students

            mapper = MapperRegistry.get_current_mapper('User')
            self.queryset = mapper.all()

        # print(f'query ----> {self.queryset}')
        return self.render_template_with_context()


#
# @AppRoute(routes=routes, url='/studentlist/')
# class CourseStudentList(ListView):
#     queryset = base.students
#     template_name = 'student_list.html'


@AppRoute(routes=routes, url='/enrollinacourse/')
class EnrollInACourse(CreateView):
    template_name = 'enroll_in_a_course.html'
    # queryset = base.students

    # Студента на курс можно добавить в БД, но нужно точно знать логин и id курса...
    def create_obj(self, data):
        new_obj = base.create_courses_student(data)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/updatecourse/')
class UpdateCourse(UpdateView):
    template_name = 'update_course.html'

    # queryset = base.students

    def update_obj(self, data):
        name = data['coursename']
        new_category = data['coursecategory']
        category = base.find_category_by_id(self.object_update.id_category)

        # course_category = {'id_category': self.object_update.id_category, 'id_course': self.object_update.id}
        # course_category_for_del = base.create_category_courses(course_category)
        # course_category_for_del.mark_removed()
        # UnitOfWork.get_current().commit()
        # mapper = MapperRegistry.get_current_mapper('CoursesCategories')
        # course_cat = mapper.find_by_field('id_course', self.object_update.id)
        # print(course_cat[0].id)
        self.object_update.name = base.decode_value(name)
        self.object_update.id_category = base.decode_value(new_category)
        # print(f'tec self.object_update.id_category ---> {self.object_update.id_category}')

        # mapper = MapperRegistry.get_current_mapper('Course')
        # mapper.update(self.object_update)
        # course_cat = {'id_category': new_category, 'id_course': self.object_update.id}
        # course_category_for_ins = base.create_category_courses(course_cat)
        # course_category_for_ins.mark_new()
        # UnitOfWork.get_current().commit()
        # course_cat[0].id_category = base.decode_value(new_category)
        # print(course_cat[0].id_category)
        # print(f'course-cat_id-->{course_cat[0].id}')
        # course_cat[0].mark_dirty()
        # UnitOfWork.get_current().commit()
        self.object_update.mark_dirty()
        UnitOfWork.get_current().commit()

        logger_main.log(f'курс с ID - {self.object_update.id} обновлен')
        # При обновлении курса нужно отправить уведомления студентам
        self.object_update.notify()
        # category.course.append(self.object_update)

    # Получаем объект изменения, конкретно тут - курс
    def get_object_update(self, data):
        # print(f'get obj data ---> {data}')
        self.object_update = base.find_course_by_id(data)


@AppRoute(routes=routes, url='/courseapi/')
class CourseApi:
    @Debug()
    def __call__(self, request):
        return '200 OK', SerializerView(base.curses).save()
