import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import json
import boto3
from bs4 import BeautifulSoup
from dotenv import load_dotenv

########################## Environments ###############################
load_dotenv()
APP_STORE_REVIEW_URL = os.getenv('APP_STORE_REVIEW_URL')
BUCKET_NAME = os.getenv('BUCKET_NAME')
FILE_KEY = os.getenv('FILE_KEY')
SLACK_OAUTH_TOKEN = os.getenv('SLACK_OAUTH_TOKEN')
SLACK_ALARM_CHANNEL_ID = os.getenv('SLACK_ALARM_CHANNEL_ID')
LAST_REVIEW_FILE_PATH = "crawlers/outputs/last_review_id.json"

#########################################################################


client = WebClient(token=SLACK_OAUTH_TOKEN)

s3 = boto3.client('s3')


def fetch_reviews():
    response = requests.get(APP_STORE_REVIEW_URL)
    if response.status_code == 200:
        return response.json().get('feed', {}).get('entry', [])
    else:
        return None


def get_last_review_id():
    if not os.path.exists(LAST_REVIEW_FILE_PATH):
        return None
    try:
        with open(LAST_REVIEW_FILE_PATH, "r") as file:
            data = json.load(file)
            return data.get('last_review_id')
    except Exception as e:
        print(f"Error fetching last review ID:{e}")
        return None


def save_last_review_id(review_id):
    try:
        with open(LAST_REVIEW_FILE_PATH, "w") as file:
            json.dump({'last_review_id': review_id}, file)
    except Exception as e:
        print(f"Error saving last review ID: {e}")


def check_for_new_reviews():
    reviews = fetch_reviews()
    if reviews is None:
        print("Failed to fetch reviews.")
        return
    # last_review_id = get_last_review_id()
    new_reviews = []

    for review in reviews:
        # if last_review_id and review['id']['label'] == last_review_id:
        #     break
        new_reviews.append(review)
    if new_reviews:
        new_reviews.reverse()
        for review in new_reviews:
            print(
                f"New review id {review['id']['label']} by {review['author']['name']['label']}: {review['title']['label']} \n내용: {review['content']['label']}\nrating: {review['im:rating']['label']}, updated: {review['updated']['label']}, version: {review['im:version']['label']}", )
        # try:
        #     response = client.chat_postMessage(channel=SLACK_ALARM_CHANNEL_ID,text="slack alarm test!")
        # except SlackApiError as e:
        #     print(f"Error posting slack message: {e}")
        save_last_review_id(new_reviews[-1]['id']['label'])


if __name__ == "__main__":
    check_for_new_reviews()
