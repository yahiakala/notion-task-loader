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

import anvil.users
from anvil import *  # noqa
from anvil_squared import utils
from routing import router

from ...Global import Global, AppName
from ._anvil_designer import SignupTemplate


class Signup(SignupTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        # Set Form properties and Data Bindings.
        self.lbl_title.text = 'Sign up for ' + AppName
        self.init_components(**properties)
        self.url_dict = routing_context.query
        self.user = Global.user
        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False
            self.cp_login.role = ["narrow-col", "narrow-col-mobile"]

    def route_user(self, **event_args):
        """Send the user on their way."""
        if "redirect" in self.url_dict and self.user:
            Global.user = self.user
            anvil.js.window.location.href = self.url_dict["redirect"]
        elif self.user:
            Global.user = self.user
            router.navigate(path="/app/home")
        pass

    def btn_google_click(self, **event_args):
        """Signup with Google"""
        if self.user:
            self.route_user()
            return

        # Disable button and show processing state
        self.btn_google.enabled = False
        self.btn_google.text = "Signing up..."

        try:
            # Make server call without loading indicator
            with anvil.server.no_loading_indicator:
                self.user = anvil.users.signup_with_google(remember=True)
                self.route_user()
        except anvil.users.UserExists as e:
            anvil.alert(str(e.args[0]))
            self.user = None
            router.navigate(path="/signin", query=self.url_dict)
        finally:
            # Restore button state
            self.btn_google.text = "Sign up with Google"
            self.btn_google.enabled = True

    def btn_signup_click(self, **event_args):
        """Signup with email/password"""
        if self.user:
            self.route_user()
            return

        # Disable button and show processing state
        self.btn_signup.enabled = False
        self.btn_signup.text = "Signing up..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            self.user = utils.signup_with_email(
                self.tb_email,
                self.tb_password,
                self.tb_password_repeat,
                AppName,
                "signup_with_email_custom",
                self.lbl_error,
            )

        # Restore button state
        self.btn_signup.text = "Sign up"
        self.btn_signup.enabled = True

    def tb_signup_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus."""
        return utils.signup_with_email_checker(
            self.tb_email.text,
            self.tb_password.text,
            self.tb_password_repeat.text,
            self.lbl_error,
        )

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert("Email support@dreambyte.ai.")  # noqa

    def link_signin_click(self, **event_args):
        """This method is called when the link is clicked"""
        router.navigate(path="/signin", query=self.url_dict)
