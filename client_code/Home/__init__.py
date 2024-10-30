from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server
from anvil_extras import routing

default_prompt = """
Give me a list of recommended fixes and feature requests, remove the user and times.
Only return a list of recommended changes and make it more specific, provide timestamps and references on where to find the items in the list.
Reference each point to the screenshots/dates in the list. make the list markdown.
I'll be providing you with conversations/transcriptions/chats in new messages and do not return me the list until I say "i am done"
"""

default_prompt_2 = """

"""

@routing.route('', template='Router')
@routing.route('/home', template='Router')
class Home(HomeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # anvil.server.call('do_admin')
        # Any code you write here will run before the form opens.
        self.ta_prompt.text = default_prompt

    def btn_edit_prompt_click(self, **event_args):
        """This method is called when the component is clicked."""
        self.ta_prompt.visible = True


