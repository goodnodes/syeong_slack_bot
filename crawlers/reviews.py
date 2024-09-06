import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

########################## Environments ###############################
load_dotenv()
APP_STORE_REVIEW_URL = os.environ['APP_STORE_REVIEW_URL']
SLACK_ALARMY_OAUTH_TOKEN = os.environ['SLACK_ALARMY_OAUTH_TOKEN']
SLACK_USER_VOICE_CHANNEL_ID = os.environ['SLACK_USER_VOICE_CHANNEL_ID']
LAST_REVIEW_FILE_PATH = "crawlers/outputs/last_review_id.json"

#########################################################################

client = WebClient(token=SLACK_ALARMY_OAUTH_TOKEN)


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


def format_review(review):
    rating_map = {
        "1": "⭐",
        "2": "⭐️⭐️",
        "3": "⭐️⭐️⭐️",
        "4": "⭐️⭐️⭐️⭐️",
        "5": "⭐️⭐️⭐️⭐️⭐️"
    }
    title_map = {
        "1": "👿고객님이 화났어요!👿",
        "2": "🏊🏻앱스토어에 새로운 후기가 등록됐어요!",
        "3": "🏊🏻‍앱스토어에 새로운 후기가 등록됐어요!",
        "4": "🏊🏻앱스토어에 새로운 후기가 등록됐어요!",
        "5": "🐳칭찬은 고래도 춤추게 한다!",
    }

    # time format conversion
    parsed_date = datetime.fromisoformat(review['updated']['label'])
    formatted_date = parsed_date.strftime("%Y년 %m월 %d일 %I시 %M분 %S초")

    return (
        f"*[새로운 후기 등록]*\n"
        f"*{title_map.get(review['im:rating']['label'], '')}*\n\n"
        f"*별점* : {rating_map.get(review['im:rating']['label'], '')}\n"
        f"*작성자* : {review['author']['name']['label']}\n"
        f"*제목* : {review['title']['label']}\n"
        f"*내용* : {review['content']['label']}\n"
        f"*날짜* : {formatted_date}\n"
        f"*버전* : {review['im:version']['label']}"
    )


def check_for_new_reviews():
    reviews = fetch_reviews()
    if reviews is None:
        print("Failed to fetch reviews.")
        return
    last_review_id = get_last_review_id()
    new_reviews = []

    for review in reviews:
        if last_review_id and review['id']['label'] == last_review_id:
            break
        new_reviews.append(review)
    if new_reviews:
        new_reviews.reverse()
        for review in new_reviews:
            try:
                response = client.chat_postMessage(channel=SLACK_USER_VOICE_CHANNEL_ID, text=format_review(review))
            except SlackApiError as e:
                print(f"Error posting slack message: {e}")
        save_last_review_id(new_reviews[-1]['id']['label'])


if __name__ == "__main__":
    check_for_new_reviews()
