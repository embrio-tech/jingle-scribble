from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, Header, Footer

landing_text = """:::::: [i]Welcome to[/i] ::::::\n
[b]EMBRIO.tech's[/b]
[b]Jingle Scribble[/b]\n
[green][yellow]*[/yellow]
/.\\
/[red]o[/red]..\\
/..[red]o[/red]\\
/.[red]o[/red]..[red]o[/red]\\
/...[red]o[/red].\\
/..[red]o[/red]....\\
^^^[sandy_brown][_][/sandy_brown]^^^\n[/green]"""

class Body(Container):
    BORDER_SUBTITLE='Press ENTER to start ->'
    def compose(self):
      yield Static(landing_text, classes='center')
    
class Start(Screen):
    BINDINGS = [("enter", "app.switch_mode('app')", "Continue")]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Body()
        yield Footer()

