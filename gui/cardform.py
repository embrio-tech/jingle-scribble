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
        self.form = {}

    def compose(self):
        yield Label("Recipient")
        yield Input(placeholder="Who will get the card?", name='recipient')
        yield Label("Context")
        yield Input(placeholder="Tell me something about him...", name='context')
        yield Label("Language")
        yield RadioSet(
            RadioButton(label="English", name='english'),
            RadioButton(label="German", name='german'),
            RadioButton(label="Italian", name='italian'),
            RadioButton(label="French", name='french'),
            name="language"
        )
        yield Button(label="Generate", variant='success', name='generate_card')

    def on_input_changed(self, event: Input.Changed):
        self.form[event.control.name] = event.value

    def on_radio_set_changed(self, event: RadioSet.Changed):
        self.form[event.control.name] = event.pressed.name

    async def on_button_pressed(self, event: Button.Pressed):
        await self.run_action("app.push_screen('loader')")
        card_worker = self.generate_card()
        text = await card_worker.wait()
        self.app.message['text'] = text
        await self.run_action("app.pop_screen")
        await self.run_action("app.push_screen('card_edit')")

    @work(exclusive=True, thread=True)
    def generate_card(self) -> str:
        text = generate_content(self.form['recipient'], self.form['context'], self.form['language'])
        text = compute_lines(text)
        return text


class CardForm(Screen):
    BINDINGS = [("ctrl+z", "app.pop_screen()", "Back to menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Body()
        yield Footer()
