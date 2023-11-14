#from cardgenerator import new_card
from globals import config
import signal
from pathlib import Path
from gui.app import JSApp

TMP_DIR = config['TMP']['DIR']

def stopHandler():
  print('closing state...')
  app.state.close()

signal.signal(signal.SIGINT, stopHandler)

Path(TMP_DIR).mkdir(exist_ok=True)

app = JSApp()
app.run()