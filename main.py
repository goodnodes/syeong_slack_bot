import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# from listners import register_listneres

# Initialization
load_dotenv()
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
logging.basicConfig(level=logging.DEBUG)

# if __name__ == "__main__":
#     SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()