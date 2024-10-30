from routing.router import Route
from routing.router import TemplateWithContainerRoute as BaseRoute


class SignRoute(BaseRoute):
    template = 'Templates.Static'
    path = '/'
    form = 'Pages.Sign'
    cache_form = True


class SigninRoute(BaseRoute):
    template = 'Templates.Static'
    path = '/signin'
    form = 'Pages.Signin'
    cache_form = True


class SignupRoute(BaseRoute):
    template = 'Templates.Static'
    path = '/signup'
    form = 'Pages.Signup'
    cache_form = True


class HomeRoute(BaseRoute):
    template = 'Templates.Router'
    path = '/app'
    form = 'Pages.Home'
    cache_form = True


class SettingsRoute(BaseRoute):
    template = 'Templates.Router'
    path = '/app/settings'
    form = 'Pages.Settings'
    cache_form = True


class TestsRoute(BaseRoute):
    template = 'Templates.Router'
    path = '/app/tests'
    form = 'Pages.Tests'
    cache_form = True