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
        self.rp_users.add_event_handler('x-update-mapping', self.update_notion_mapping)

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

        # Load users and notion users
        self.load_users()

        # Remove skeleton states
        self.tb_notion_api_key.role = "task-input"
        self.tb_notion_db_id.role = "task-input"

    def load_users(self):
        """Load app users and notion users"""
        # Get app users with their notion mappings
        users = Global.users

        # Get notion users for dropdowns
        notion_users = self.notion_stuff.get("notion_users", []) or []

        # Format notion users for dropdown - convert to list of tuples (display_value, stored_value)
        notion_user_items = (
            [(u["name"], u["id"]) for u in notion_users] if notion_users else []
        )

        # Get existing mappings (default to empty dict if None)
        self.existing_mappings = self.notion_stuff.get("notion_user_mapping", {}) or {}

        # Update repeating panel items with users and notion user options
        self.rp_users.items = [
            {
                "email": user["user"]["email"],
                "notion_users": notion_user_items,
                "selected_notion_user": self.existing_mappings.get(user['user']['email']),
            }
            for user in users.search()
        ]

    def update_notion_mapping(self, user_notion, **event_args):
        self.existing_mappings[user_notion['email']] = user_notion['notion_user_id']
        print(self.existing_mappings)

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

    def btn_update_users_click(self, **event_args):
        """Update list of Notion workspace users that goes into each dropdown."""
        # Disable button and show processing state
        self.btn_update_users.enabled = False
        self.btn_update_users.text = "Refreshing..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            # Call server function to update notion users
            notion_users = anvil.server.call(
                "save_tenant_notion_users", Global.tenant_id
            )

            # Update tenant notion info with new users
            self.notion_stuff["notion_users"] = notion_users

            # Reload users to update dropdowns with new notion users
            self.load_users()

        # Restore button state
        self.btn_update_users.text = "Refresh Notion Users"
        self.btn_update_users.enabled = True

    def btn_save_user_mapping_click(self, **event_args):
        """Save mappings between users and notion users."""
        self.btn_save_user_mapping.enabled = False
        self.btn_save_user_mapping.text = "Saving..."

        with anvil.server.no_loading_indicator:
            anvil.server.call("save_user_notion_mappings", Global.tenant_id, self.existing_mappings)

        self.btn_save_user_mapping.text = "Save"
        self.btn_save_user_mapping.enabled = True
