from ._anvil_designer import TasksTemplate
from anvil import *


class Tasks(TasksTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)