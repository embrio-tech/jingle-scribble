
from textual.app import App
from .start import Start
from .menu import Menu
from .cardform import CardForm
from .cardedit import CardEdit
from .loader import Loader
from textual.widgets import Button


class JSApp(App):
    ENABLE_COMMAND_PALETTE = False
    TITLE = "Jingle Scribble"
    SUB_TITLE = "powered by EMBRIO.tech"
    CSS_PATH = "app.tcss"
    MODES = {"start": Start, "app": "menu"}
    SCREENS = {"menu": Menu, "card_form": CardForm(
    ), 'loader': Loader(), "card_edit": CardEdit()}

    def on_mount(self) -> None:
        self.message = {}
        self.switch_mode('start')
