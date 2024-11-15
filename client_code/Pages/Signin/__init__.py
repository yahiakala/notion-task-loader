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
from ._anvil_designer import SigninTemplate


class Signin(SigninTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.lbl_title.text = 'Sign in to ' + AppName
        self.init_components(**properties)
        self.routing_context = routing_context
        self.url_dict = routing_context.query
        self.user = Global.user
        self.route_user()

        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False
            self.cp_login.role = ["narrow-col", "narrow-col-mobile"]

    def route_user(self, **event_args):
        """Send the user on their way."""
        if "redirect" in self.url_dict and self.user:
            self.tb_email.text = ""
            self.tb_password.text = ""
            Global.user = self.user
            anvil.js.window.location.href = self.url_dict["redirect"]
        elif self.user:
            self.tb_email.text = ""
            self.tb_password.text = ""
            Global.user = self.user
            router.navigate(path="/app/home")

    def btn_google_click(self, **event_args):
        """Signin with google. Creates a user if none exists."""
        # Disable button and show processing state
        self.btn_google.enabled = False
        self.btn_google.text = "Signing in..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            self.user = anvil.users.login_with_google(remember=True)
            self.route_user()

        # Restore button state
        self.btn_google.text = "Sign in with Google"
        self.btn_google.enabled = True

    def link_forgot_click(self, **event_args):
        """This method is called when the link is clicked"""
        utils.reset_password(self.tb_email, self.lbl_error)

    def link_signup_click(self, **event_args):
        """This method is called when the link is clicked"""
        router.navigate(path="/signup", query=self.url_dict)

    def btn_signin_click_custom(self, **event_args):
        # Disable button and show processing state
        self.btn_signin.enabled = False
        self.btn_signin.text = "Signing in..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            self.user = utils.signin_with_email(
                self.tb_email,
                self.tb_password,
                "login_with_email_custom",
                self.lbl_error,
            )
            self.route_user()

        # Restore button state
        self.btn_signin.text = "Sign in"
        self.btn_signin.enabled = True

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert("Email support@dreambyte.ai.")  # noqa
