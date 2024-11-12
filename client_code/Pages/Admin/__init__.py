from ._anvil_designer import AdminTemplate
from anvil import *
import anvil.server
from ...Global import Global


class Admin(AdminTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.notion_stuff = Global.tenant_notion_info
    
    def btn_save_notion_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call(
            'save_tenant_notion',
            self.tb_notion_api_key.text,
            self.tb_notion_db_id.text,
            self.tb_notion_userid.text
        )


