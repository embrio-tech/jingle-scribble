from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button, Header, Footer


class Body(Container):
    BORDER_TITLE="MENU"
    def compose(self):
        yield Label("Hey, what are we doing today?")
        yield Button(label="Writing a single card", variant='success', name='open_card_form')
        yield Button(label="Print cards from Google Sheets", variant='success')
        # yield Button("Write a single card", variant='primary')

    async def on_button_pressed(self, event: Button.Pressed):
        await self.run_action("app.push_screen('card_form')")


class Menu(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Body()
        yield Footer()
