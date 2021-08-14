from datetime import date

from fwarg.core import ApplicationFW
from views import Main, About, Contacts, CursesList, CategoryList, CursesCreate, CategoryCreate, Curse, \
    CurseCopy


#
# urlpatterns = {
#     '/': Main(),
#     '/about/': About(),
#     '/contacts/': Contacts(),
#     '/curses_list/': CursesList(),
#     '/curse/': Curse(),
#     '/curse_copy/': CurseCopy(),
#     '/category_list/': CategoryList(),
#     '/curses_create/': CursesCreate(),
#     '/category_create/': CategoryCreate(),
# }
#

# FC дописывает добавляет дату
def date_controller(request):
    request['date_now'] = date.today()


front_controllers = [
    date_controller
]

# application = ApplicationFW(front_controllers)
