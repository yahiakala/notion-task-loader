from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.users
import anvil.server

from ...Global import Global


class Settings(SettingsTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.rp_mfa.add_event_handler('x-remove-mfa-id', self.remove_mfa_id)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.load_data()

    def load_data(self):
        """Load data and remove skeleton states"""
        self.user = Global.user
        if self.user['password_hash']:
            self.cp_password_change.visible = True
            self.cp_mfa.visible = True
        self.rp_mfa.items = self.user['mfa']

        # Load user tenant data including Notion settings
        usertenant = Global.usertenant
        
        # Populate Notion fields
        self.tb_notion_api_key.text = usertenant.get('notion_api_key', '')
        self.tb_notion_db_id.text = usertenant.get('notion_task_db_id', '')
        self.load_notion_user_ids()

        # Remove skeleton roles after data is loaded
        self.tb_notion_api_key.role = 'task-input'
        self.tb_notion_db_id.role = 'task-input'

    def load_notion_user_ids(self, **event_args):
        self.dd_notion_personal_user.items = (
            [(u["name"], u["id"]) for u in Global.usertenant['notion_users_personal']]
            if Global.usertenant['notion_users_personal'] else []
        )
        if self.dd_notion_personal_user.items:
            self.dd_notion_personal_user.selected_value = Global.usertenant['notion_user_id']
        
        self.dd_notion_team_user.items = (
            [(u["name"], u["id"]) for u in Global.usertenant['notion_users_team']]
            if Global.usertenant['notion_users_team'] else []
        )
        if self.dd_notion_team_user.items:
            self.dd_notion_team_user.selected_value = Global.usertenant['notion_team_user_id']

    def btn_chg_pw_click(self, **event_args):
        self.lbl_pw_error.visible = False
        self.user = Global.user
        if self.tb_oldpw.text and self.tb_newpw.text:
            print('Changing password')
            try:
                anvil.users.reset_password(self.tb_oldpw.text, self.tb_newpw.text)
                self.lbl_pw_error.text = 'Password Changed!'
                self.lbl_pw_error.visible = True
                self.tb_oldpw.text = ''
                self.tb_newpw.text = ''
            except anvil.users.AuthenticationFailed:
                print('Auth failed')
                self.lbl_pw_error.text = 'Old password is incorrect.'
                self.lbl_pw_error.visible = True
            except anvil.users.PasswordNotAcceptable:
                self.lbl_pw_error.text = 'Passwords must be 8 characters or more and be harder to guess.'
                self.lbl_pw_error.visible = True
        else:
            self.lbl_pw_error.text = 'Old or new entered password is blank.'
            self.lbl_pw_error.visible = True

    def btn_add_mfa_click(self, **event_args):
        """This method is called when the button is clicked"""
        # anvil.users.mfa.configure_mfa_with_form(allow_cancel=True)
        self.configure_mfa_custom()
        # self.user = anvil.users.get_user(allow_remembered=True)
        # Global.user = self.user
        self.rp_mfa.items = self.user['mfa']

    def configure_mfa_custom(self):
        error = None
        while True:
            mfa_method, password = anvil.users.mfa._configure_mfa(self.user['email'], error, True, True, "Save")
            
            if mfa_method:
                try:
                    # anvil.users.mfa.add_mfa_method(password, mfa_method)
                    self.user = anvil.server.call('add_mfa_method', password, mfa_method)
                    alert("Your two-factor authentication configuration has been added.")
                    return True
                except anvil.users.AuthenticationFailed as e:
                    error = e.args[0]
                except Exception as e:
                    error = str(e)
            else:
                return None

    def remove_mfa_id(self, **event_args):
        """Remove a configured MFA method."""
        try:
            self.user = anvil.server.call('delete_mfa_method', event_args['password'], event_args['id'])
            Global.user = self.user
            self.rp_mfa.items = self.user['mfa']
        except anvil.users.AuthenticationFailed as e:
            alert('Password is incorrect.')

    def btn_save_notion_click(self, **event_args):
        """Save Notion settings for the current user's tenant"""
        # Get values from text boxes
        self.btn_save_notion.enabled = False
        # Update button text to show saving state
        self.btn_save_notion.text = "Saving..."
        
        # Update settings through server function
        with anvil.server.no_loading_indicator:
            updated_usertenant = anvil.server.call(
                'save_user_notion',
                Global.tenant_id,
                self.tb_notion_api_key.text,
                self.tb_notion_db_id.text,
                self.dd_notion_personal_user.selected_value,
                self.dd_notion_team_user.selected_value
            )
            
            # Update Global state with new settings
            Global.usertenant = updated_usertenant
            
        # Show success message and restore button text
        self.btn_save_notion.text = 'Save'
        self.btn_save_notion.enabled = True

    def btn_update_users_click(self, **event_args):
        """Update list of Notion workspace users that goes into each dropdown."""
        # Disable button and show processing state
        self.btn_update_users.enabled = False
        self.btn_update_users.text = "Refreshing..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            # Call server function to update notion users
            Global.usertenant = anvil.server.call(
                "save_tenant_notion_users", Global.tenant_id
            )
            # Reload users to update dropdowns with new notion users
            self.load_notion_user_ids()

        # Restore button state
        self.btn_update_users.text = "Refresh Notion Users"
        self.btn_update_users.enabled = True
