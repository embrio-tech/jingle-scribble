import os
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, TextArea
from textual import work
from cardgenerator import format_content, draw_svg, compile_gcode


class TextEditor(TextArea):
    BINDINGS = [("ctrl+g", "draw_card", "Generate")]

    def on_mount(self):
        self.load_text(self.app.message['text'])

    @work(exclusive=True, thread=True)
    def draw_card(self) -> None:
        lines = format_content(self.text).split('\n')
        svg = draw_svg(lines)
        gcode = compile_gcode(svg)
        return gcode
    
    async def action_draw_card(self):
        await self.run_action("app.push_screen('loader')")
        card_maker = self.draw_card()
        gcode = await card_maker.wait()
        os.system("open -a Safari file://$(pwd)/test.svg")
        await self.run_action("app.pop_screen")
        



class CardEdit(Screen):
    BINDINGS = [("esc", "app.pop_screen()", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextEditor()
        yield Footer()
