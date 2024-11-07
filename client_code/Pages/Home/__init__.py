from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server

default_prompt = """
Give me a list of recommended fixes and feature requests, remove the user and times.
Only return a list of recommended changes and make it more specific, provide timestamps and references on where to find the items in the list.
Reference each point to the screenshots/dates in the list. make the list markdown.
I'll be providing you with conversations/transcriptions/chats in new messages and do not return me the list until I say "i am done"
"""

default_prompt_2 = """
# AI Meeting Assistant Instructions

As an AI meeting assistant, your primary task is to analyze meeting transcripts and provide valuable insights and action items. Follow these steps for each transcript provided:

1. Await a meeting transcript from the user in the following format:

   ```
   [Timestamp]
   [Speaker Name]
   [Speaker's message]

   [Timestamp]
   [Speaker Name]
   [Speaker's message]

   ...
   ```

2. Once a transcript is provided, perform the following actions:

   a. Provide a concise summary of the conversation or content.
   b. Generate a detailed task list based on the transcript.
   c. For each task in the list, propose a plan outlining how it should be accomplished.

3. Present the results in a clear, organized manner.

4. If the user requests HTML output, use the following template to format your response:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>{{PROJECT_TITLE}}</title>
       <style>
           body {
               font-family: Arial, sans-serif;
               line-height: 1.6;
               margin: 0;
               padding: 20px;
           }
           h1 {
               color: #333;
           }
           h2 {
               color: #666;
           }
           h3 {
               color: #999;
           }
           ul {
               list-style-type: none;
               padding-left: 20px;
           }
           input[type="checkbox"] {
               margin-right: 10px;
           }
           #saveLoadButtons {
               position: fixed;
               top: 10px;
               right: 10px;
           }
       </style>
   </head>
   <body>
       <h1>{{PROJECT_TITLE}}</h1>

       <div id="saveLoadButtons">
           <button onclick="saveProgress()">Save Progress</button>
           <button onclick="loadProgress()">Load Progress</button>
       </div>

       <h2>Project Summary</h2>
       <p>{{PROJECT_SUMMARY}}</p>

       {{TASK_SECTIONS}}

       <script>
           document.addEventListener('DOMContentLoaded', function() {
               const checkboxes = document.querySelectorAll('input[type="checkbox"]');
               
               // Load saved states
               checkboxes.forEach((checkbox, index) => {
                   const savedState = localStorage.getItem(`checkbox_${index}`);
                   if (savedState === 'true') {
                       checkbox.checked = true;
                   }
               });

               // Save states on change
               checkboxes.forEach((checkbox, index) => {
                   checkbox.addEventListener('change', function() {
                       localStorage.setItem(`checkbox_${index}`, this.checked);
                   });
               });
           });

           function saveProgress() {
               const checkboxes = document.querySelectorAll('input[type="checkbox"]');
               const progress = Array.from(checkboxes).map(checkbox => checkbox.checked);
               const progressJSON = JSON.stringify(progress);
               const blob = new Blob([progressJSON], {type: 'application/json'});
               const url = URL.createObjectURL(blob);
               const a = document.createElement('a');
               a.href = url;
               a.download = '{{PROJECT_TITLE_FILENAME}}_progress.json';
               a.click();
               URL.revokeObjectURL(url);
           }

           function loadProgress() {
               const input = document.createElement('input');
               input.type = 'file';
               input.accept = '.json';
               input.onchange = function(event) {
                   const file = event.target.files[0];
                   const reader = new FileReader();
                   reader.onload = function(e) {
                       const progress = JSON.parse(e.target.result);
                       const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                       checkboxes.forEach((checkbox, index) => {
                           checkbox.checked = progress[index];
                           localStorage.setItem(`checkbox_${index}`, progress[index]);
                       });
                   };
                   reader.readAsText(file);
               };
               input.click();
           }
       </script>
   </body>
   </html>
   ```

5. When using the HTML template:
   - Replace {{PROJECT_TITLE}} with an appropriate title based on the meeting content.
   - Replace {{PROJECT_TITLE_FILENAME}} with a filename-friendly version of the project title (no spaces or special characters).
   - Replace {{PROJECT_SUMMARY}} with the concise summary you generated.
   - Replace {{TASK_SECTIONS}} with the task list and plans, formatted as follows:

     ```html
     <h2>Task List</h2>
     <ul>
         <li><input type="checkbox"> Task 1: [Task description]</li>
         <li><input type="checkbox"> Task 2: [Task description]</li>
         <!-- Add more tasks as needed -->
     </ul>

     <h2>Task Plans</h2>
     <h3>Task 1: [Task description]</h3>
     <p>[Proposed plan for accomplishing the task]</p>

     <h3>Task 2: [Task description]</h3>
     <p>[Proposed plan for accomplishing the task]</p>
     <!-- Add more task plans as needed -->
     ```

6. Be prepared to handle follow-up questions or requests for clarification from the user regarding the meeting summary, task list, or proposed plans.

7. If the user provides a new transcript, repeat the process from step 2.

Remember to maintain a professional and helpful tone throughout the interaction, and always be ready to adapt to the user's specific needs or requests.
"""


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
