
import anvil.server
# from Templates.Router import Router
# from .BlankTemplate import BlankTemplate
# from .Static import Static
from .Global import Global

from routing.router import launch
from . import routes


if __name__ == "__main__":
    launch()

# TODO: add notion params, add form behavior of buttons and disappearing cards, test API call.
