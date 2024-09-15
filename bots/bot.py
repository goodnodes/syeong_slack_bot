import os
import json
from dotenv import load_dotenv
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

########################## Environments ###############################
load_dotenv()
SLACK_ALARMY_OAUTH_TOKEN = os.environ['SLACK_ALARMY_OAUTH_TOKEN']
SLACK_NOTIFICATIONS_CHANNEL_ID = os.environ['SLACK_NOTIFICATIONS_CHANNEL_ID']
SLACK_DEV_CHANNEL_ID = os.environ['SLACK_DEV_CHANNEL_ID']
BOT_MSG = os.environ['BOT_MSG']
UP_AND_DOWN_COMMENTS_FILE_PATH = "crawlers/comments/up_and_down_comments.json"
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
    # print(msg)
    try:
        response = client.chat_postMessage(channel=SLACK_NOTIFICATIONS_CHANNEL_ID,
                                           text=msg)
        # response = client.chat_postMessage(channel="C07FQEVF3V2", thread_ts="", text="")
        # client.conversations_list()
        # response = client.conversations_history(channel="C07FQEVF3V2")
        # save_id(response)
        # print(response)
    except SlackApiError as e:
        print(f"Error posting slack message: {e}")

if __name__ == "__main__":
    post_msg()
