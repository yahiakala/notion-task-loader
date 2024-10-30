from ._anvil_designer import RouterTemplate
from anvil import *
import anvil.users

from ..Global import Global

from anvil_extras import routing

from ..Home import Home
from ..Settings import Settings
from ..Tests import Tests


@routing.template(path='app', priority=1, condition=None)
class Router(RouterTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.link_home.tag.url_hash = 'app/home'
        self.link_dev.tag.url_hash = 'app/tests'
        self.link_logout.tag.url_hash = 'app/logout'
        self.link_settings.tag.url_hash = 'app/settings'
        
        user = Global.user
        self.set_account_state(user)

    def nav_click(self, sender, **event_args):
        load_cache = True
        if sender.tag.url_hash == '':
            if Global.user:
                self.set_account_state(Global.user)
                routing.set_url_hash('app/home', load_from_cache=load_cache)
            else:
                routing.set_url_hash('signin', load_from_cache=load_cache)
        else:
            routing.set_url_hash(sender.tag.url_hash, load_from_cache=load_cache)

    def on_navigation(self, url_hash, url_pattern, url_dict, unload_form):
        """Whenever a new route is loaded."""
        for link in self.cp_sidebar.get_components():
            if type(link) == Link:
                link.role = 'selected' if link.tag.url_hash == url_pattern else None
        if url_pattern in ['app', '']:
            self.link_home.role = 'selected'

    def on_form_load(self, url_hash, url_pattern, url_dict, form):
        """Any time a form is loaded."""
        self.set_account_state(Global.user)

    def icon_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        with anvil.server.no_loading_indicator:
            anvil.users.logout()
            self.set_account_state(None)
            routing.clear_cache()
            Global.clear_global_attributes()
            routing.set_url_hash('signin', load_from_cache=False)

    def set_account_state(self, user):
        self.icon_logout.visible = user is not None
        self.link_logout.visible = user is not None
        self.link_settings.visible = user is not None

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert('For help, contact example@example.com')
