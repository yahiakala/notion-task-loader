from ._anvil_designer import RouterTemplate
from anvil import *
import anvil.users

from ...Global import Global

from routing import router
import anvil.server


class Router(RouterTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    # def on_form_load(self, url_hash, url_pattern, url_dict, form):
    #     """Any time a form is loaded."""
    #     self.set_account_state(Global.user)

    def icon_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        with anvil.server.no_loading_indicator:
            anvil.users.logout()
            self.set_account_state(None)
            router.clear_cache()
            Global.clear_global_attributes()
            router.navigate(path='/signin')

    def set_account_state(self, user):
        self.icon_logout.visible = user is not None
        self.link_logout.visible = user is not None
        self.nav_settings.visible = user is not None
        self.nav_admin.visible = user is not None and 'see_members' in Global.permissions

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert("For help, contact example@example.com")

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.set_account_state(Global.user)
