from ._anvil_designer import AdminTemplate
from anvil import *


class Admin(AdminTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_save_notion_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
