from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button, Header, Footer


class Body(Container):
    BORDER_TITLE = "MENU"

    def compose(self):
        yield Label("Hey, what are we doing today?")
        yield Button(label="Writing a single card", variant='success', name='single_card')
        yield Button(label="Print cards from Google Sheets", variant='success', name='google_cards')
        # yield Button("Write a single card", variant='primary')

    async def on_button_pressed(self, event: Button.Pressed):
        if (event.button.name == 'single_card'):
            await self.run_action("app.push_screen('card_form')")
        if (event.button.name == 'google_cards'):
            await self.run_action("app.push_screen('card_table')")


class Menu(Screen):
    BINDINGS = [("q", "app.close", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Body()
        yield Footer()
