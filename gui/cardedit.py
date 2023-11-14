import webbrowser
from globals import config
from pathlib import Path
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, TextArea
from textual import work
from textual.worker import WorkerFailed
from cardgenerator import format_content, draw_svg, compile_gcode, generate_content, compute_lines, format_content
from googleapiclient.discovery import build
import httpx

CHARS_PER_LINE = int(config['PAPER']['CHARS_PER_LINE'])
TMP_DIR = config['TMP']['DIR']
TMP_FILENAME = config['TMP']['FILENAME']
GOOGLE_SPREADSHEET = config['SPREADSHEET']['ID']
CNC_URL = config['CNC']['URL']
CNC_TOKEN = config['CNC']['TOKEN']

class TextEditor(TextArea):
    BINDINGS = [
        ("escape", "close", "Back"),
        ("ctrl+w", "generate_card", "Re-write card"),
        ("ctrl+s", "save_message", "Save card"),
        ("ctrl+g", "draw_card", "Draw card"),
        ('ctrl+p', 'screen.preview','Preview SVG'),
        ('ctrl+t', 'screen.send_gcode', 'Transfer GCODE')
        ]
    
    async def action_generate_card(self):
        await self.run_action("app.push_screen('loader')")
        text_worker = self.generate_card()
        text = await text_worker.wait()
        self.app.state['message'] = { **self.app.state['message'], 'text': text }
        self.load_text(text)
        await self.run_action("app.pop_screen")

    @work(exclusive=True, thread=True)
    def generate_card(self) -> str:
        text = generate_content(
            self.app.state['message']['recipient'], 
            self.app.state['message']['context'], 
            self.app.state['message']['language'], 
            self.app.state['message']['style']
            )
        text = format_content(text)
        text = compute_lines(text, chars=CHARS_PER_LINE)
        return text
        
    @work(exclusive=True, thread=True, exit_on_error=False)
    def draw_card(self) -> None:
        lines = format_content(self.text).split('\n')
        svg = draw_svg(lines)
        gcode = compile_gcode(svg)
        return gcode
    
    async def action_draw_card(self):
        self.app.state['message']['text'] = self.text
        await self.run_action("app.push_screen('loader')")
        try:
          card_maker = self.draw_card()
          await card_maker.wait()
        except WorkerFailed as err:
            self.app.notify(message=err.error.__str__(),severity='error',timeout=10)
        await self.run_action("app.pop_screen")

    async def action_close(self):
        svg_path = Path(TMP_DIR,f'{TMP_FILENAME}.svg')
        gcode_path = Path(TMP_DIR,f'{TMP_FILENAME}.gcode')
        if svg_path.exists(): svg_path.unlink()
        if gcode_path.exists(): gcode_path.unlink()
        await self.run_action("app.pop_screen")

    async def action_save_message(self):
        message = self.app.state['message']
        if 'row_id' not in message:
            self.app.notify('Cannot save, Missing row id!')
            return
        self.app.state['message']['text'] = self.text
        row_id = message['row_id']
        await self.run_action("app.push_screen('loader')")
        update_worker = self.save_message(row_id, self.text)
        await update_worker.wait()
        await self.run_action("app.pop_screen")
    
    @work(exclusive=True, thread=True)
    def save_message(self, row_id: int, text: str) -> None:
        service = build("sheets", "v4", credentials=self.app.state['credentials'])
        sheet = service.spreadsheets()
        sheet.values().update(spreadsheetId=GOOGLE_SPREADSHEET, range=f'G{row_id}', valueInputOption='USER_ENTERED', body={'values': [[text]]}).execute()

class CardEdit(Screen):
    async def on_screen_resume(self):
        text_editor = self.query_one('TextEditor')
        if 'text' in self.app.state['message']: 
            text_editor.load_text(self.app.state['message']['text'])
        else:
            await text_editor.action_generate_card()

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextEditor()
        yield Footer()

    async def action_preview(self):
        svg = Path(TMP_DIR, f'{TMP_FILENAME}.svg')
        if svg.exists(): webbrowser.get('safari').open('file://' + svg.absolute().as_posix())
        else: self.app.notify('No SVG to preview, Please draw it first!', timeout=10)

    async def action_send_gcode(self):
        gcode = Path(TMP_DIR, f'{TMP_FILENAME}.gcode')
        if gcode.exists(): 
            gcode_worker = self.send_gcode(gcode.absolute())
            await gcode_worker.wait()
            self.app.notify('GCODE Sent!', timeout=10)
        else: 
            self.app.notify('No GCODE, Please generate first!', timeout=10, severity='error')

    @work(exclusive=True, thread=True)
    async def send_gcode(self, path):
        with open(path, 'r') as f:
          gcode = f.read()
        response = httpx.post(f'{CNC_URL}/api/gcode', headers={'authorization': f'Bearer {CNC_TOKEN}'}, json={'port': '/dev/ttyACM0', 'gcode': gcode})
        return response.json()

