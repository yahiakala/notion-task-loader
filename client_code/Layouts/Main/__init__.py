from ._anvil_designer import MainTemplate
from anvil import *


class Main(MainTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def select_link(self, sender, **event_args):
        # for link in self.link_panel.get_components():
        #     link.selected = False
        # sender.selected = True
        pass