from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server

class Home(HomeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Initialize state
        self.action_items = []
        self.current_task = None
        # Configure components
        self.ta_transcript.auto_expand = True
        self.ta_transcript.placeholder = "Enter your transcript here..."
        # Initialize with empty task list
        self.rp_tasks.items = []

    def btn_submit_click(self, **event_args):
        """Handle transcript submission and start background processing"""
        transcript = self.ta_transcript.text
        if not transcript:
            notification = Notification("Please enter a transcript first.", 
                                     title="Input Required",
                                     style="warning")
            notification.show()
            return

        with anvil.server.no_loading_indicator:
            try:
                self.btn_submit.enabled = False
                self.btn_submit.text = "Processing..."
                self.current_task = anvil.server.call('process_transcript', transcript)
                self.img_loading.visible = True
                self.timer_prompt.interval = 2
            except Exception as e:
                notification = Notification(f"Error: {str(e)}", 
                                         title="Processing Error",
                                         style="danger")
                notification.show()
                self.reset_ui()

    def timer_prompt_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        with anvil.server.no_loading_indicator:
            try:
                status = self.current_task.get_termination_status()
                if status == 'completed':
                    self.action_items = self.current_task.get_return_value()
                    self.rp_tasks.items = self.action_items
                    notification = Notification("Tasks processed successfully!", 
                                             title="Success",
                                             style="success")
                    notification.show()
                    self.reset_ui()
                elif status == 'failed':
                    error = self.current_task.get_error()
                    notification = Notification(f"Error processing transcript: {str(error)}", 
                                             title="Processing Error",
                                             style="danger")
                    notification.show()
                    self.reset_ui()
            except Exception as e:
                notification = Notification(f"Error: {str(e)}", 
                                         title="System Error",
                                         style="danger")
                notification.show()
                self.reset_ui()

    def reset_ui(self):
        """Reset UI elements to their default state"""
        self.timer_prompt.interval = 0
        self.btn_submit.enabled = True
        self.btn_submit.text = "Process Tasks"
        self.img_loading.visible = False
