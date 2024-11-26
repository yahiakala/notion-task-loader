# from routing.router import Route
from routing.router import TemplateWithContainerRoute as BaseRoute
from routing.router import Redirect
from .Global import Global
import anvil.server


class EnsureUserMixin:
    def before_load(self, **loader_args):
        if not Global.user:
            raise Redirect(path="/signin")
        if Global.user and Global.get_s('tenant') is None:
            Global.tenant = anvil.server.call('get_tenant_single')
            if Global.get_s('tenant') is None:
                Global.tenant = anvil.server.call('create_tenant_single')
            try:
                Global.tenant_id = Global.tenant.get_id()
            except Exception:
                Global.tenant_id = Global.tenant['id']
            if 'delete_members' in Global.permissions and (Global.tenant['name'] is None or Global.tenant['name'] == ''):
                raise Redirect(path='/app/admin')


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


class HomeRoute(EnsureUserMixin, BaseRoute):
    template = 'Templates.Router'
    path = '/app/home'
    form = 'Pages.Home'
    cache_form = True


class SettingsRoute(EnsureUserMixin, BaseRoute):
    template = 'Templates.Router'
    path = '/app/settings'
    form = 'Pages.Settings'
    cache_form = True


class AdminRoute(EnsureUserMixin, BaseRoute):
    template = 'Templates.Router'
    path = '/app/admin'
    form = 'Pages.Admin'
    cache_form = True


class TestsRoute(EnsureUserMixin, BaseRoute):
    template = 'Templates.Router'
    path = '/app/tests'
    form = 'Pages.Tests'
    cache_form = True