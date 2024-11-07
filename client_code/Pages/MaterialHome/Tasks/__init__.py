from ._anvil_designer import TasksTemplate
from anvil import *

class Tasks(TasksTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
