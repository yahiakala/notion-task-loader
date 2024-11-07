from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server


class Home(HomeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # anvil.server.call('do_admin')
        # Any code you write here will run before the form opens.
        self.ta_prompt.text = default_prompt
        self.action_items = []
        self.current_task = None
        
        # Add timer component for polling
        self.timer = Timer(interval=1)  # noqa
        self.timer.set_event_handler('tick', self.check_task_status)

    def btn_edit_prompt_click(self, **event_args):
        """This method is called when the component is clicked."""
        self.ta_prompt.visible = True

    def btn_submit_click(self, **event_args):
        """Handle transcript submission and start background processing"""
        transcript = self.ta_transcript.text
        if not transcript:
            alert("Please enter a transcript first.")
            return
            
        self.btn_submit.enabled = False
        
        try:
            # Start background processing
            self.current_task = anvil.server.call('start_processing', transcript)
            
            # Start polling for results
            self.timer.enabled = True
            
        except Exception as e:
            alert(f"Error starting processing: {str(e)}")
            self.reset_button_state()
            
    def check_task_status(self, **event_args):
        """Check status of current background task"""
        if not self.current_task:
            self.timer.enabled = False
            return
            
        try:
            if self.current_task.is_completed():
                # Get the results
                self.action_items = self.current_task.get_result()
                self.display_action_items()
                self.cleanup_task()
                
            elif self.current_task.is_error():
                # Handle error
                error = self.current_task.get_error()
                alert(f"Error processing transcript: {str(error)}")
                self.cleanup_task()
                
        except Exception as e:
            alert(f"Error checking task status: {str(e)}")
            self.cleanup_task()
            
    def cleanup_task(self):
        """Clean up task state"""
        self.reset_button_state()
        self.timer.enabled = False
        self.current_task = None
            
    def reset_button_state(self):
        """Reset submit button to initial state"""
        self.btn_submit.icon = "mi:send"
        self.btn_submit.enabled = True
            
    def display_action_items(self):
        """Display the action items in a formatted way"""
        if not self.action_items:
            alert("No action items were found in the transcript.")
            return
            
        # Create a formatted display of action items
        display_text = "Action Items:\n\n"
        
        for item in self.action_items:
            display_text += f"Title: {item['title']}\n"
            display_text += f"Description: {item['description']}\n"
            display_text += "-" * 50 + "\n\n"
            
        # Create or update results text area
        if not hasattr(self, 'ta_results'):
            self.ta_results = TextArea(
                visible=True,
                enabled=True,
                spacing_above="small",
                spacing_below="small",
                height=300
            )
            self.add_component(self.ta_results)
            
        self.ta_results.text = display_text

    def timer_prompt_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        pass
