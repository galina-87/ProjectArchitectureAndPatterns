import inspect
import sqlite3
import sys

import patterns.generative_patterns
import models


# Маппер - универсальный, в классах соответсвующих таблицам БД должна быть указана соответствующая модель
# и имена файлов с моделями и и с классами им соответствующими должны быть models и patterns.generative_patterns
# обязательно (тут как в джанго получилось с обязательными именами так как они импортируются сюда)
# Можно вынести в __init__ маппера получение data и кое чего еще - а то пока повторения есть в коде функций маппера...
# Но это чуть позже - сегодня не успеваю...
# Но в целом: на основании входящих данных (имени модели и того, что передается в функции) маппер для любого объекта БД
# получает полный список, получает запись по id (и отдает соответствующий объект), может обновить запись БД, а так же
# внести новую запись в БД (удалить думаю, что тоже может - на мой взгляд должно работать, но может мелкие косяки
# проявятся - нужно будет немного поправить - удаление не проверяла...=((( ...не успела - нужно писать и шаблоны и view)
class UniversalMapper:

    def __init__(self, connection, model):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = model

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        data = {}

        result = []
        attr_classes = {}
        class_tec = None

        clsmembers = [obj for name, obj in inspect.getmembers(sys.modules['models'], inspect.isclass)]
        for item in clsmembers:
            if item.__name__ == self.tablename:
                attr_classes = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])

        clsmembers_obj = [obj for name, obj in inspect.getmembers(sys.modules['patterns.generative_patterns'],
                                                                  inspect.isclass)]
        for item in clsmembers_obj:
            attr_classes_obj = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])
            # print(f'tec attr_classes_obj ---> {item} --- > {attr_classes_obj}')
            for atr in attr_classes_obj:
                # print(f'atr--->{atr}')
                if atr == 'model' and attr_classes_obj['model'] == self.tablename:
                    class_tec = item

        for attr_class in attr_classes:
            data[attr_class] = None
        # print(data)
        for list_attr in self.cursor.fetchall():
            # print(list_attr)
            i = 0
            for item_data in data.keys():
                item = str(list_attr[i])
                data[item_data] = item
                i += 1
                # print(f'tec data ---> {data}')
            tec_obj = class_tec(data)
            # print(f'tec data ---> {data}')
            result.append(tec_obj)
        return result

    def find_by_id(self, id):
        statement = f"SELECT * FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        class_tec = None
        clsmembers_obj = [obj for name, obj in inspect.getmembers(sys.modules['patterns.generative_patterns'],
                                                                  inspect.isclass)]
        for item in clsmembers_obj:
            attr_classes_obj = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])
            # print(f'tec attr_classes_obj ---> {item} --- > {attr_classes_obj}')
            for atr in attr_classes_obj:
                # print(f'atr--->{atr}')
                if atr == 'model' and attr_classes_obj['model'] == self.tablename:
                    class_tec = item
        # print(f'tec_class ---> {class_tec}')
        result = self.cursor.fetchall()
        data = {}
        attr_classes = None
        clsmembers = [obj for name, obj in inspect.getmembers(sys.modules['models'], inspect.isclass)]
        for item in clsmembers:
            if item.__name__ == self.tablename:
                attr_classes = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])
        for attr_class in attr_classes:
            data[attr_class] = None
        # print(data)
        for list_attr in result:
            # print(list_attr)
            i = 0
            for item_data in data.keys():
                # print(f'tec item_data ---> {item_data}')
                item = str(list_attr[i])
                data[item_data] = item
                i += 1
                # print(f'tec data ---> {data}')
        tec_obj = class_tec(data)
        # print(f'tec data ---> {data}')
        result = tec_obj
        if result:
            return class_tec(data)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        data = {}
        attr_classes = {}
        clsmembers = [obj for name, obj in inspect.getmembers(sys.modules['models'], inspect.isclass)]
        for item in clsmembers:
            if item.__name__ == self.tablename:
                attr_classes = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])
        for attr_class in attr_classes.keys():
            # print(f'tec attr_class ---> {attr_class}')
            data[attr_class] = getattr(obj, attr_class)
        # print(data)
        statement = f'INSERT INTO {self.tablename} '
        data_list = []
        values_list = []
        for key in data.keys():
            if not key == 'id':
                data_list.append(key)
                values_list.append(data[key])

        data_set = tuple(data_list)
        print(f'tec data_set ---> {data_set}')
        # str_data_set = str(data_set)[:-2]
        value_set = tuple(values_list)
        print(f'tec value_set ---> {value_set}')
        # str_value_set = str(value_set)[:-2]
        statement = f'{statement}{data_set} VALUES {value_set}'
        statement = statement.replace(',)', ')')
        print(f'tec statement ---> {statement}')
        self.cursor.execute(statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        data = {}
        attr_classes = {}
        clsmembers = [obj for name, obj in inspect.getmembers(sys.modules['models'], inspect.isclass)]
        for item in clsmembers:
            if item.__name__ == self.tablename:
                attr_classes = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])
        for attr_class in attr_classes.keys():
            # print(f'tec attr_class ---> {attr_class}')
            data[attr_class] = getattr(obj, attr_class)
        # print(data)
        statement = f'UPDATE {self.tablename} SET '
        data_list = []
        for key in data.keys():
            if not key == 'id':
                statement = f'{statement}{key}=?, '
                data_list.append(data[key])
        statement = statement[:-2]
        statement = f'{statement} WHERE id =?'
        data_list.append(data['id'])
        # print(f'tec statement ---> {statement}')
        data_set = tuple(data_list)
        # print(f'tec data_set ---> {data_set}')
        # Где взять obj.id? Добавить в DomainModel? Или добавить когда берем объект из базы

        self.cursor.execute(statement, data_set)
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

    def find_by_field(self, field, value):
        statement = f"SELECT * FROM {self.tablename} WHERE {field}={value}"
        self.cursor.execute(statement)
        data = {}

        result = []
        attr_classes = {}
        class_tec = None

        clsmembers = [obj for name, obj in inspect.getmembers(sys.modules['models'], inspect.isclass)]
        for item in clsmembers:
            if item.__name__ == self.tablename:
                attr_classes = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])

        clsmembers_obj = [obj for name, obj in inspect.getmembers(sys.modules['patterns.generative_patterns'],
                                                                  inspect.isclass)]
        for item in clsmembers_obj:
            attr_classes_obj = dict([attr for attr in inspect.getmembers(item) if not (attr[0].startswith('__')
                                                                                       and attr[0].endswith('__'))])
            # print(f'tec attr_classes_obj ---> {item} --- > {attr_classes_obj}')
            for atr in attr_classes_obj:
                # print(f'atr--->{atr}')
                if atr == 'model' and attr_classes_obj['model'] == self.tablename:
                    class_tec = item

        for attr_class in attr_classes:
            data[attr_class] = None
        # print(data)
        for list_attr in self.cursor.fetchall():
            # print(list_attr)
            i = 0
            for item_data in data.keys():
                item = str(list_attr[i])
                data[item_data] = item
                i += 1
                # print(f'tec data ---> {data}')
            tec_obj = class_tec(data)
            # print(f'tec data ---> {data}')
            result.append(tec_obj)
        return result


connection = sqlite3.connect('my_database.db')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    # mappers = {
    #     'student': UniversalMapper,
    #     # 'category': CategoryMapper
    # }
    #
    # @staticmethod
    # def get_mapper(obj):
    #     # if isinstance(obj, Student):
    #     return UniversalMapper(connection, obj)
    #     # if isinstance(obj, Category):
    #     # return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(model):
        return UniversalMapper(connection, model)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
