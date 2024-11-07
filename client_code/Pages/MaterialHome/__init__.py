from ._anvil_designer import MaterialHomeTemplate
from anvil import *
import anvil.server

class MaterialHome(MaterialHomeTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.action_items = []
        self.current_task = None
        self.ta_transcript.auto_expand = True
        self.rp_tasks.items = [{'title': 'Test 1', 'description': 'Test1 description'}]

    def btn_submit_click(self, **event_args):
        """Handle transcript submission and start background processing"""
        transcript = self.ta_transcript.text
        if not transcript:
            Notification("Please enter a transcript first.").show()
            return

        with anvil.server.no_loading_indicator:
            self.btn_submit.enabled = False
            self.current_task = anvil.server.call('process_transcript', transcript)
            self.img_loading.visible = True
            self.timer_prompt.interval = 2

    def timer_prompt_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        with anvil.server.no_loading_indicator:
            status = self.current_task.get_termination_status()
            if status == 'completed':
                self.timer_prompt.interval = 0
                self.action_items = self.current_task.get_return_value()
                self.rp_tasks.items = self.action_items
                self.rp_tasks.visible = True
                self.btn_submit.enabled = True
                self.img_loading.visible = False
                Notification("Processing complete!", timeout=3).show()
                
            elif status == 'failed':
                self.timer_prompt.interval = 0
                error = self.current_task.get_error()
                alert(f"Error processing transcript: {str(error)}")
                self.btn_submit.enabled = True
                self.img_loading.visible = False
                self.timer_prompt.interval = 0
