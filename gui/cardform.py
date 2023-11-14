from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Label, Button, Header, Footer, Input, RadioSet, RadioButton
from textual import work
from cardgenerator import generate_content, compute_lines


class Body(Container):
    BORDER_TITLE = "CARD FORM"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form = { **self.app.state['message'] }
        if 'text' in self.form:
            del self.form['text']

    def compose(self):
        yield Label("Recipient")
        yield Input(placeholder="Who will get the card?", name='recipient', value=self.form.get('recipient', ''))
        yield Label("Context")
        yield Input(placeholder="Tell me something about him...", name='context', value=self.form.get('context', ''))
        yield Label("Language")
        yield RadioSet(
            RadioButton(label="English", name='english', value=True),
            RadioButton(label="German", name='german'),
            RadioButton(label="Italian", name='italian'),
            RadioButton(label="French", name='french'),
            name="language",
            )
        yield Label("Style")
        yield RadioSet(
            RadioButton(label="Informal", name='informal', value=True),
            RadioButton(label="Formal", name='formal'),
            name="style",
            )
        yield Button(label="Generate", variant='success', name='generate_card')

    def on_input_changed(self, event: Input.Changed):
        self.form[event.control.name] = event.value

    def on_radio_set_changed(self, event: RadioSet.Changed):
        self.form[event.control.name] = event.pressed.name

    async def on_button_pressed(self, event: Button.Pressed):
        self.app.state['message'] = { **self.form }
        await self.run_action("app.push_screen('card_edit')")


class CardForm(Screen):
    BINDINGS = [("escape", "app.pop_screen()", "Back to menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Body()
        yield Footer()
