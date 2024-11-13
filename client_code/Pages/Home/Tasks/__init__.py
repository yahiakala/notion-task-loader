from ._anvil_designer import TasksTemplate
from anvil import *


class Tasks(TasksTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def btn_personal_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def btn_team_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def btn_discard_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
