import inspect
import sqlite3
import sys
import models

# В файле автоматически - на основании модуля models.py создается БД. Таблицы формируются исходя
# из классов модуля. Поля таблиц формируются исходя из атребутов классов, в указанном (в модуле) количестве и с
# указанными настройками (хотя пока в урезанном варианте, не все настройки можно задать - например, внешний ключ)
# Пока можно только с нуля создать - накатить обновления структуры БД пока нельзя =((( можно пересоздать

sql_query_text = '\nBEGIN TRANSACTION;\n'

clsmembers = [obj for name, obj in inspect.getmembers(sys.modules['models'], inspect.isclass)]
print(clsmembers)

for item in clsmembers:
    sql_query_text = f'{sql_query_text}\n\nDROP TABLE IF EXISTS {item.__name__};\nCREATE ' \
                     f'TABLE {item.__name__} ('

    attr_classes = dict([attr for attr in inspect.getmembers(item) if not(attr[0].startswith('__')
                                                                          and attr[0].endswith('__'))])
    # print(attr_classes)
    composite_pk_field = ''
    for key in attr_classes.keys():
        sql_query_text = f'{sql_query_text}\n{key}'
        # print(attr_classes[key])
        for field in attr_classes[key].keys():
            # print(attr_classes[key][field])
            if str(field).upper() == 'TYPE':
                type_field = str(attr_classes[key][field]).upper()
                sql_query_text = f'{sql_query_text} {type_field}'
            elif str(field).upper() == 'NOT_NULL' and str(attr_classes[key][field]).upper() == 'NOT NULL':
                not_null_field = str(attr_classes[key][field]).upper()
                sql_query_text = f'{sql_query_text} {not_null_field}'
            elif str(field).upper() == 'UNIQ' and str(attr_classes[key][field]).upper() == 'TRUE':
                uniq_field = 'UNIQUE'
                sql_query_text = f'{sql_query_text} {uniq_field}'
            elif str(field).upper() == 'DEFAULT':
                if str(attr_classes[key][field]).isdigit():
                    default_field = f'DEFAULT {str(attr_classes[key][field])}'
                else:
                    default_field = f'DEFAULT \'{str(attr_classes[key][field])}\''
                sql_query_text = f'{sql_query_text} {default_field}'
            elif str(field).upper() == 'COMPOSITE_PK' and str(attr_classes[key][field]).upper() == 'TRUE':
                composite_pk_field = f'{composite_pk_field}{str(key)}, '
            elif str(field).upper() == 'PK' and str(attr_classes[key][field]).upper() == 'TRUE':
                PK_field = 'PRIMARY KEY'
                sql_query_text = f'{sql_query_text} {PK_field}'
            elif str(field).upper() == 'AUTOINCREMENT' and str(attr_classes[key][field]).upper() == 'TRUE':
                AUTOINCR_field = 'AUTOINCREMENT'
                sql_query_text = f'{sql_query_text} {AUTOINCR_field}'
        sql_query_text = f'{sql_query_text},'

    sql_query_text = sql_query_text[:-1]

    if len(composite_pk_field) > 0:
        composite_pk_field = composite_pk_field[:-2]
        sql_query_text = f'{sql_query_text},\nCONSTRAINT new_pk PRIMARY KEY ({composite_pk_field})\n);\n'
    else:
        sql_query_text = f'{sql_query_text}\n);\n'

sql_query_text = f'{sql_query_text}\nCOMMIT TRANSACTION;\n'

# print(sql_query_text)

with open('create_db.sql', 'w') as f:
    f.write(sql_query_text)

con = sqlite3.connect('my_database.db')
cur = con.cursor()
with open('create_db.sql', 'r') as f:
    text1 = f.read()
cur.executescript(text1)
cur.close()
con.close()
