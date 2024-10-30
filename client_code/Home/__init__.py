from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server
from anvil_extras import routing


@routing.route('', template='Router')
@routing.route('/home', template='Router')
class Home(HomeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # anvil.server.call('do_admin')
        # Any code you write here will run before the form opens.
