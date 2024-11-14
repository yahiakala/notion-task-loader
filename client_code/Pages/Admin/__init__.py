# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import anvil.server
from anvil import *

from ...Global import Global
from ._anvil_designer import AdminTemplate


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
        self.tb_notion_api_key.text = self.notion_stuff["notion_api_key"]
        self.tb_notion_db_id.text = self.notion_stuff["notion_db_id"]

        # Remove skeleton states
        self.tb_notion_api_key.role = "task-input"
        self.tb_notion_db_id.role = "task-input"

    def btn_save_notion_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Disable button and show processing state
        self.btn_save_notion.enabled = False
        self.btn_save_notion.text = "Saving..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            Global.tenant_notion_info = anvil.server.call(
                "save_tenant_notion",
                Global.tenant_id,
                self.tb_notion_api_key.text,
                self.tb_notion_db_id.text,
            )

        # Reload users with new API key
        self.load_users()

        # Restore button state
        self.btn_save_notion.text = "Save"
        self.btn_save_notion.enabled = True

