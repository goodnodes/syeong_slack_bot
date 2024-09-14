import os
from dotenv import load_dotenv
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

########################## Environments ###############################
load_dotenv()
SLACK_ALARMY_OAUTH_TOKEN = os.environ['SLACK_ALARMY_OAUTH_TOKEN']
SLACK_NOTIFICATIONS_CHANNEL_ID = os.environ['SLACK_NOTIFICATIONS_CHANNEL_ID']
BOT_MSG = os.environ['BOT_MSG']
UP_AND_DOWN_COMMENTS_FILE_PATH = "crawlers/comments/up_and_down_comments.json"
#########################################################################
client = WebClient(token=SLACK_ALARMY_OAUTH_TOKEN)



def post_msg():
    msg = BOT_MSG
    # print(msg)
    try:
        response = client.chat_postMessage(channel=SLACK_NOTIFICATIONS_CHANNEL_ID,
                                           text=msg)
    except SlackApiError as e:
        print(f"Error posting slack message: {e}")

if __name__ == "__main__":
    post_msg()
