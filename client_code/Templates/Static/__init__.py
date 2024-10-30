from ._anvil_designer import StaticTemplate
from anvil import *

from ...Signin import Signin
from ...Signup import Signup
from ...Sign import Sign


class Static(StaticTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
