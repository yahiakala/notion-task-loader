from ._anvil_designer import RouterTemplate
from anvil import *
import anvil.users

from ...Global import Global

from routing import router


class Router(RouterTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.link_home.tag.path = "/app"
        self.link_dev.tag.path = "/app/tests"
        self.link_logout.tag.path = "/app/logout"
        self.link_settings.tag.path = "/app/admin"

        user = Global.user
        self.set_account_state(user)

    def nav_click(self, sender, **event_args):
        if sender.tag.path == "":
            if Global.user:
                self.set_account_state(Global.user)
                router.navigate(path='app/home')
            else:
                router.navigate(path='/signin')
        else:
            router.navigate(path=sender.tag.path)

        for link in self.cp_sidebar.get_components():
            if type(link) == Link:
                link.role = "selected" if link.tag.path == sender.tag.path else None
        if sender.tag.path in ["app", ""]:
            self.link_home.role = "selected"

    def on_form_load(self, url_hash, url_pattern, url_dict, form):
        """Any time a form is loaded."""
        self.set_account_state(Global.user)

    def icon_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        with anvil.server.no_loading_indicator:
            anvil.users.logout()
            self.set_account_state(None)
            router.clear_cache()
            Global.clear_global_attributes()
            router.navigate(path='/signin')
            # routing.set_url_hash("signin", load_from_cache=False)

    def set_account_state(self, user):
        self.icon_logout.visible = user is not None
        self.link_logout.visible = user is not None
        self.link_settings.visible = user is not None and 'see_members' in Global.permissions

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert("For help, contact example@example.com")
