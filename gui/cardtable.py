from globals import config
from typing import List
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual import work
from googleapiclient.discovery import build

GOOGLE_SPREADSHEET = config['SPREADSHEET']['ID']

class CardTable(Screen):
    BINDINGS = [("escape", "app.pop_screen()", "Back to menu")]

    async def on_screen_resume(self):
        has_credentials = 'credentials' in self.app.state
        if (not has_credentials):
            await self.run_action("app.push_screen('login')")
            return
        request_worker = self.get_recipients()
        print('fetching values')
        values = await request_worker.wait()
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns(*values[0])
        table.add_rows(values[1:])
        return
    
    async def on_data_table_row_selected(self, event: DataTable.RowSelected):
        request_worker = self.get_message(event.cursor_row)
        row_id, first_name, last_name, context, language, style, text = await request_worker.wait()
        message = { 'row_id': row_id, 'recipient': f'{first_name} {last_name}', 'context': context, 'language': language, 'style': style }
        if text: message['text'] = text
        self.app.state['message'] = message
        await self.run_action("app.push_screen('card_edit')")
        

    @work(exclusive=True, thread=True)
    def get_recipients(self) -> List:
        service = build("sheets", "v4", credentials=self.app.state['credentials'])
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SPREADSHEET, range='A:C').execute()
        values = result.get("values", [])
        return values
    
    @work(exclusive=True, thread=True)
    def get_message(self, line_nr: int) -> List:
        row_id = line_nr + 2
        service = build("sheets", "v4", credentials=self.app.state['credentials'])
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SPREADSHEET, range=f'A{row_id}:G{row_id}').execute()
        values = result.get("values", [['']*6])[0]
        row = [row_id, values[0], values[1], values[3], values[4], values[5], None]
        if len(values) > 6: row[6] = values[6]
        return row


    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(zebra_stripes=True, cursor_type='row')
        yield Footer()
