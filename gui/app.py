
import shelve
from textual.app import App
from .start import Start
from .menu import Menu
from .cardform import CardForm
from .cardedit import CardEdit
from .loader import Loader
from .cardtable import CardTable
from .login import Login
from textual.widgets import Button

class JSApp(App):
    ENABLE_COMMAND_PALETTE = False
    TITLE = "Jingle Scribble"
    SUB_TITLE = "powered by EMBRIO.tech"
    CSS_PATH = "app.tcss"
    MODES = {"start": Start, "app": "menu"}
    SCREENS = {"menu": Menu, "card_form": CardForm(
    ), 'loader': Loader(), "card_edit": CardEdit(), "card_table": CardTable(classes='top') ,"login": Login()}

    def on_mount(self) -> None:
        self.state = shelve.open('.state', writeback=True)
        self.switch_mode('start')

    def action_close(self):
        self.state.close()
        self.exit()
