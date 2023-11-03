from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, Header, Footer, LoadingIndicator

class Body(Container):
    BORDER_TITLE='Loading'
    BORDER_SUBTITLE='Beep, beep, boop'
    def compose(self):
      yield LoadingIndicator()
    
class Loader(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Body()
        yield Footer()