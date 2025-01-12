import os
import json
from dotenv import load_dotenv
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

########################## Environments ###############################
load_dotenv()
SLACK_ALARMY_OAUTH_TOKEN = os.environ['SLACK_ALARMY_OAUTH_TOKEN']
SLACK_RANDOM_CHANNEL_ID = os.environ['SLACK_RANDOM_CHANNEL_ID']
BOT_MSG = os.environ['BOT_MSG']
#########################################################################
client = WebClient(token=SLACK_ALARMY_OAUTH_TOKEN)

# def save_id(id):
#     try:
#         with open("bots/syeong_info/extra.json", "w") as file:
#             json.dump(id,file,default=str)
#             # json.dump({"id" : id}, file)
#     except Exception as e:
#         print(f"Error saving last review ID: {e}")

def post_msg():
    msg = BOT_MSG
    try:
        response = client.chat_postMessage(channel=SLACK_RANDOM_CHANNEL_ID,
                                           text=msg)
    except SlackApiError as e:
        print(f"Error posting slack message: {e}")

if __name__ == "__main__":
    post_msg()
