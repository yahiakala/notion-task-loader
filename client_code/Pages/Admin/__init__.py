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
        with anvil.server.no_loading_indicator:
            self.load_data()
    
    def load_data(self):
        """Load data and remove skeleton states"""
        self.notion_stuff = Global.tenant_notion_info
        
        # Populate fields
        self.tb_notion_api_key.text = self.notion_stuff['notion_api_key']
        self.tb_notion_db_id.text = self.notion_stuff['notion_db_id']
        
        # Remove skeleton states
        self.tb_notion_api_key.role = 'task-input'
        self.tb_notion_db_id.role = 'task-input'
    
    def btn_save_notion_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call(
            'save_tenant_notion',
            Global.tenant_id,
            self.tb_notion_api_key.text,
            self.tb_notion_db_id.text
        )
