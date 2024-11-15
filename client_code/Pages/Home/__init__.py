from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server


class Home(HomeTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.action_items = []
        self.current_task = None
        self.ta_transcript.auto_expand = False

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        pass
        
    def btn_submit_click(self, **event_args):
        """Handle transcript submission and start background processing"""
        transcript = self.ta_transcript.text
        if not transcript:
            alert("Please enter a transcript first.")
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
                # alert(self.action_items)
                self.btn_submit.enabled = True
                self.img_loading.visible = False
                
            elif status == 'failed':
                self.timer_prompt.interval = 0
                error = self.current_task.get_error()
                alert(f"Error processing transcript: {str(error)}")
                self.btn_submit.enabled = True
                self.img_loading.visible = False
                self.timer_prompt.interval = 0
