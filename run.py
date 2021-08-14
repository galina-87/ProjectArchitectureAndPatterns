from fwarg.core import FakeApplication, ApplicationFW, DebugApplication
from main_urls import front_controllers
from wsgiref.simple_server import make_server
from views import routes

application = DebugApplication(routes, front_controllers)

with make_server('', 8000, application) as httpd:
    print("Запуск на порту 8000...")
    httpd.serve_forever()
