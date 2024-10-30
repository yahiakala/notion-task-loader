from routing.router import Route
from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = 'Static'

# class IndexRoute(Route):
#     path = "/"
#     form = "Pages.Index"

# class AboutRoute(Route):
#     path = "/about"
#     form = "Pages.About"

# class ContactRoute(Route):
#     path = "/contact"
#     form = "Pages.Contact"

class SignRoute(BaseRoute):
    # self.template = 'Static'
    path = '/'
    form = 'Sign'