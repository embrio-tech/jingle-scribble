from http.server import BaseHTTPRequestHandler, HTTPServer
from textual import work
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button, Header, Footer
from google.oauth2.credentials import Credentials
from urllib import parse
import webbrowser
import pkce
import httpx

from globals import config

PORT = int(config['OAUTH']['CALLBACK_PORT'])
CLIENT_ID = config['OAUTH']['CLIENT_ID']
CLIENT_SECRET = config['OAUTH']['CLIENT_SECRET']
AUTH_URI = config['OAUTH']['AUTH_URI']
TOKEN_URI = config['OAUTH']['TOKEN_URI']


class Body(Container):
    BORDER_TITLE = "LOGIN"

    def compose(self):
        yield Button(label="Sign-in with Google", variant='success', name='google_login')

    async def on_button_pressed(self, event: Button.Pressed):
        if (event.button.name == 'google_login'):
            has_credentials = 'credentials' in self.app.state
            if not has_credentials:
              auth_worker = self.authenticate()
              authenticated = await auth_worker.wait()
              if (authenticated): await self.run_action("app.pop_screen")
            
    @work(exclusive=True, thread=True)
    def authenticate(self):
        code_verifier, code_challenge = pkce.generate_pkce_pair()
        redirect_uri = f'http://127.0.0.1:{PORT}'
        with OAuthHttpServer(('', PORT), OAuthHttpHandler) as httpd:
            auth_args = {
                'client_id': CLIENT_ID,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'email https://www.googleapis.com/auth/spreadsheets',
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }
            auth_uri = f'{AUTH_URI}?' + parse.urlencode(auth_args)
            webbrowser.open_new(auth_uri)
            httpd.handle_request()
            auth_code = httpd.authorization_code
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        response = httpx.post(TOKEN_URI, data=data)
        auth_data = response.json()
        self.app.state['credentials'] = Credentials(
            auth_data['access_token'], 
            refresh_token=auth_data['refresh_token'], 
            id_token=auth_data['id_token'], 
            token_uri=TOKEN_URI,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        return self.app.state['credentials'].valid

class Login(Screen):
    BINDINGS = [("escape", "app.pop_screen()", "Back")]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Body()
        yield Footer()

class OAuthHttpServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.authorization_code = None
        self.qs = None


class OAuthHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            '<html><script type="application/javascript">window.close();</script></html>'.encode("UTF-8"))
        parsed = parse.urlparse(self.path)
        self.qs = parse.parse_qs(parsed.query)
        self.server.authorization_code = self.qs["code"][0]



