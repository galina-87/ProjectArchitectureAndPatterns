
# Классы - это модельки для создания БД->атрибуты классов - это наименования поля БД, словари - это настройки поля БД
# пока не все возможные учла - например внешний ключ не задать, но базовые учла, теперь в файле creat_db.py
# автоматически собирается sql код для создания БД и автоматически создается - теоритически это код фреймворка,
# но переносить не стала... Его нужно запустить как миграции для генерации sql кода и создания непосредственно БД.

class User:
    type_user = {'type': 'varchar (28)', 'not_null': 'not null', 'uniq': 'false', 'default': 'student'}
    first_name = {'type': 'varchar (64)', 'not_null': 'not null', 'uniq': 'false'}
    last_name = {'type': 'varchar (64)', 'not_null': 'null', 'uniq': 'false'}
    login = {'type': 'varchar (32)', 'not_null': 'not null', 'uniq': 'true'}
    email = {'type': 'varchar (64)', 'not_null': 'not null', 'uniq': 'true'}
    sex = {'type': 'varchar (16)', 'not_null': 'not null', 'uniq': 'false', 'default': 'w'}
    age = {'type': 'varchar (32)', 'not_null': 'not null', 'uniq': 'false'}
    password = {'type': 'varchar (8)', 'not_null': 'not null', 'uniq': 'false'}
    id = {'type': 'integer', 'not_null': 'not null', 'uniq': 'true', 'pk': 'true', 'autoincrement': 'true'}


class Course:
    name = {'type': 'varchar (64)', 'not_null': 'true'}
    id_category = {'type': 'integer', 'not_null': 'not null'}
    id = {'type': 'integer', 'not_null': 'not null', 'uniq': 'true', 'pk': 'true', 'autoincrement': 'true'}


class Category:
    name = {'type': 'varchar (64)', 'not_null': 'not null', 'uniq': 'false'}
    id = {'type': 'integer', 'not_null': 'not null', 'uniq': 'true', 'pk': 'true', 'autoincrement': 'true'}


class StudentsCourses:
    id_course = {'type': 'integer', 'not_null': 'not null', 'composite_pk': 'true'}
    login_student = {'type': 'varchar (32)', 'not_null': 'not null', 'composite_pk': 'true'}


class CoursesCategories:
    id = {'type': 'integer', 'not_null': 'not null', 'uniq': 'true', 'pk': 'true', 'autoincrement': 'true'}
    id_category = {'type': 'integer', 'not_null': 'not null', 'composite_pk': 'true'}
    id_course = {'type': 'integer', 'not_null': 'not null', 'composite_pk': 'true'}

