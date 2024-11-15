from ._anvil_designer import TasksTemplate
from anvil import *
from ....Global import Global
import anvil.server


class Tasks(TasksTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        if Global.check_api_keys['personal']:
            self.btn_personal.enabled = True
        else:
            self.btn_personal.tooltip = 'Please configure your API key.'
        if Global.check_api_keys['team']:
            self.btn_team.enabled = True
        else:
            self.btn_team.tooltip = 'Please configure your API key.'

    def btn_personal_click(self, **event_args):
        """Send task to personal Notion workspace"""
        # Disable button and show processing state
        self.btn_personal.enabled = False
        self.btn_personal.text = "Sending..."
        
        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            _ = anvil.server.call(
                'send_to_personal_notion',
                Global.tenant_id,
                self.item['title'],
                self.item['description']
            )
            
            # Remove task from repeating panel on success
            self.remove_from_parent()
        
        # Restore button state
        self.btn_personal.text = "Send to Personal"
        self.btn_personal.enabled = True

    def btn_team_click(self, **event_args):
        """Send task to team Notion workspace"""
        # Disable button and show processing state
        self.btn_team.enabled = False
        self.btn_team.text = "Sending..."
        
        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            result = anvil.server.call(
                'send_to_team_notion',
                Global.tenant_id,
                self.item['title'],
                self.item['description']
            )
            
            # Remove task from repeating panel on success
            self.remove_from_parent()
        
        # Restore button state
        self.btn_team.text = "Send to Team"
        self.btn_team.enabled = True

    def btn_discard_click(self, **event_args):
        """Delete task from repeating panel"""
        # Disable button and show processing state
        self.btn_discard.enabled = False
        self.btn_discard.text = "Discarding..."
        
        # Remove task from repeating panel
        self.remove_from_parent()
        
        # Restore button state
        self.btn_discard.text = "Discard"
        self.btn_discard.enabled = True
