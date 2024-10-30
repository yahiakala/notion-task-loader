from ._anvil_designer import ForumTemplate
from anvil import *
import anvil.server
from anvil_extras import routing


@routing.route('/forum', template='Router')
class Forum(ForumTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        self.call_js('setIframeSrc', 'https://forum.dreambyte.ai')
