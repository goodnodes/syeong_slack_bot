from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import time
import json
import random
from dotenv import load_dotenv
import re
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
from requests.exceptions import RequestException

########################## Environments ###############################
load_dotenv()
APP_STORE_SYEONG_URL = os.environ['APP_STORE_SYEONG_URL']
APP_STORE_SMILEPASS_URL = os.environ['APP_STORE_SMILEPASS_URL']
SLACK_ALARMY_OAUTH_TOKEN = os.environ['SLACK_ALARMY_OAUTH_TOKEN']
SLACK_NOTIFICATIONS_CHANNEL_ID = os.environ['SLACK_NOTIFICATIONS_CHANNEL_ID']
SPECIAL_COMMENT = os.environ['SPECIAL_COMMENT']
LAST_RANK_FILE_PATH = "crawlers/outputs/last_rank.json"
COMMENTS_FILE_PATH = "crawlers/comments/comments.json"
UP_AND_DOWN_COMMENTS_FILE_PATH = "crawlers/comments/up_and_down_comments.json"
APP_BUNDLE_ID_SYEONG = os.getenv('APP_BUNDLE_ID_SYEONG', '').strip()
ITUNES_SEARCH_COUNTRY = os.getenv('ITUNES_SEARCH_COUNTRY', 'us').strip()
ITUNES_SEARCH_TERM = os.getenv('ITUNES_SEARCH_TERM', 'swimming').strip()
LAST_KEYWORD_RANK_FILE_PATH = "crawlers/outputs/last_keyword_rank.json"
LAST_GLOBAL_KEYWORD_RANK_FILE_PATH = "crawlers/outputs/last_keyword_rank.json"
ITUNES_SEARCH_LIMIT = 200  # API max
def _lookup_track_id_by_bundle(bundle_id: str, country: str) -> int:
    if not bundle_id:
        return 0
    url = "https://itunes.apple.com/lookup"
    params = {"bundleId": bundle_id, "country": country}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        if not results:
            return 0
        return int(results[0].get("trackId", 0))
    except (RequestException, ValueError) as e:
        print(f"[iTunes Lookup] error: {e}")
        return 0


def _search_keyword_positions(term: str, country: str, limit: int = 200) -> list[dict]:
    url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "country": country,
        "media": "software",
        "entity": "software",
        "limit": limit
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("results", [])
    except (RequestException, ValueError) as e:
        print(f"[iTunes Search] error: {e}")
        return []


def get_keyword_rank(term: str, country: str, track_id: int) -> int:
    results = _search_keyword_positions(term, country, ITUNES_SEARCH_LIMIT)
    if not results:
        return THE_MAGIC_NUMBER
    for idx, item in enumerate(results, start=1):
        if int(item.get("trackId", 0)) == track_id:
            return idx
    return THE_MAGIC_NUMBER


def get_last_keyword_rank():
    if not os.path.exists(LAST_KEYWORD_RANK_FILE_PATH):
        return None
    try:
        with open(LAST_KEYWORD_RANK_FILE_PATH, "r") as f:
            data = json.load(f)
            return data.get("last_rank")
    except Exception as e:
        print(f"Error reading last keyword rank: {e}")
        return None


def save_last_keyword_rank(current_rank: int):
    try:
        with open(LAST_KEYWORD_RANK_FILE_PATH, "w") as f:
            json.dump({"last_rank": current_rank}, f)
    except Exception as e:
        print(f"Error saving last keyword rank: {e}")

def format_keyword_message(term: str, country: str, rank_now: int, rank_prev: Optional[int]) -> str:
    """
    Formats keyword ranking messages in English for US/UK audiences,
    with a title line highlighting the global Syeong app's position.
    """
    country_label = country.upper()

    # Title line
    title_line = f"*🌎 Current US AppStore ranking of Syeong app for '{term}' keyword*"

    if rank_now == THE_MAGIC_NUMBER:
        body_line = f"*Keyword* '{term}' / {country_label} : Not ranked"
    else:
        delta = ""
        prefix = "⛔"
        if isinstance(rank_prev, int):
            if rank_prev == THE_MAGIC_NUMBER and rank_now != THE_MAGIC_NUMBER:
                prefix = "📈"
                delta = " (Entered the chart)"
            elif rank_now == THE_MAGIC_NUMBER and rank_prev != THE_MAGIC_NUMBER:
                prefix = "📉"
                delta = " (Dropped out of chart)"
            elif rank_now < rank_prev:
                prefix = "📈"
                delta = f" ({rank_prev - rank_now} place(s) up)"
            elif rank_now > rank_prev:
                prefix = "📉"
                delta = f" ({rank_now - rank_prev} place(s) down)"
        body_line = f"{prefix} *Keyword* '{term}' / {country_label} : #{rank_now}{delta}"

    return title_line + "\n" + body_line + "\n"
#########################################################################
client = WebClient(token=SLACK_ALARMY_OAUTH_TOKEN)

# [*TOP SECRET*] This magic number means unranked
THE_MAGIC_NUMBER = 3201


def load_comments(file_path):
    try:
        with open(file_path) as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading comments: {e}")
        return {}


def get_random_up_and_down_comment(comment_type, comments, last_up_and_down_comment, history):
    ud_comments_history = [entry.get('up_and_down_comment') for entry in history if 'up_and_down_comment' in history]
    up_and_down_comment_candidates = []

    if comment_type in comments:
        up_and_down_comment_candidates.extend(comments[comment_type])
    filtered_candidates = [comment for comment in up_and_down_comment_candidates if comment != last_up_and_down_comment and comment not in ud_comments_history]

    # if there is no candidate after all comments are filtered, filter again with history comments
    if not filtered_candidates:
        filtered_candidates = [comment for comment in up_and_down_comment_candidates if comment != last_up_and_down_comment]
    # if candidates only has last comment
    if not filtered_candidates:
        filtered_candidates = up_and_down_comment_candidates
    return random.choice(filtered_candidates)


def get_random_comment(comment_type, comments, rank_num, last_comment, history):
    comments_history = [entry.get('comment') for entry in history if 'comment' in history]
    comment_candidates = [""]
    if comment_type != "unranked":
        comment_candidates = [str(rank_num) + "위 입니다."]
    if comment_type in comments:
        comment_candidates.extend(comments[comment_type])
    # remove last comment in candidates
    filtered_candidates = [comment for comment in comment_candidates if comment != last_comment and comment not in comments_history]
    # if there is no candidate after all comments are filtered, filter again with history comments
    if not filtered_candidates:
        filtered_candidates = [comment for comment in comment_candidates if comment != last_comment]
    # if candidates only has last comment
    if not filtered_candidates:
        filtered_candidates = comment_candidates
    return random.choice(filtered_candidates)


def get_last_rank():
    if not os.path.exists(LAST_RANK_FILE_PATH):
        return None, None, None, []
    try:
        with open(LAST_RANK_FILE_PATH, "r") as file:
            data = json.load(file)
            history = data.get('history',[])
            if history:
                latest = history[-1]
                return latest.get('last_rank_num'), latest.get('up_and_down_comment'), latest.get('comment'), history
            else:
                return None, None, None, history
    except Exception as e:
        print(f"Error fetching last rank num:{e}")
        return None, None, None, []


def save_last_rank(current_rank_num, up_and_down_comment, comment):
    try:
        if os.path.exists(LAST_RANK_FILE_PATH):
            with open(LAST_RANK_FILE_PATH, "r") as file:
                data = json.load(file)
                history = data.get('history',[])
        else:
            history = []

        new_entry = {
            'last_rank_num': current_rank_num,
            'up_and_down_comment': up_and_down_comment,
            'comment': comment
        }
        history.append(new_entry)
        if len(history) > 5:
            history.pop(0)

        with open(LAST_RANK_FILE_PATH, "w") as file:
            json.dump({'history':history},file)
    except Exception as e:
        print(f"Error saving last rank_num: {e}")


def format_ranking(ranking, found,ranking_sp,found_sp):
    comment_list = load_comments(COMMENTS_FILE_PATH)
    up_and_down_comment_list = load_comments(UP_AND_DOWN_COMMENTS_FILE_PATH)
    last_rank_num, last_up_and_down_comment, last_comment, history = get_last_rank()
    now = datetime.now()
    formatted_date = f'{now.month}월 {now.day}일'
    # Just set default value
    # This Default value never be used as a result in expected scenarios.
    category = "건강 및 피트니스"
    category_sp = "건강 및 피트니스"
    rank = str(THE_MAGIC_NUMBER) + "위"
    rank_sp = str(THE_MAGIC_NUMBER) + "위"
    rank_num = THE_MAGIC_NUMBER  # 9999 rank number means unranked
    rank_num_sp = THE_MAGIC_NUMBER  # 9999 rank number means unranked

    # comment for unranked case
    comment = get_random_comment("unranked", comment_list, rank_num, last_comment, history)
    # default value
    rank_diff = ""
    rank_diff_sp = ""

    if found_sp:
        if "앱" in ranking_sp:
            parts_sp = ranking_sp.split("앱")
            if len(parts_sp) == 2:
                category_sp = parts_sp[0].strip()
                rank_sp = parts_sp[1].strip()

                rank_num_match_sp = re.search(r'\d+', rank_sp)
                if rank_num_match_sp:
                    rank_num_sp = int(rank_num_match_sp.group())
        else:
            print("[MUST NOT ERROR]\nSomthing wrong")
            return
    if found:
        if "앱" in ranking:
            parts = ranking.split("앱")
            if len(parts) == 2:
                category = parts[0].strip()
                rank = parts[1].strip()

                rank_num_match = re.search(r'\d+', rank)
                if rank_num_match:
                    rank_num = int(rank_num_match.group())
        else:
            print("[MUST NOT ERROR]\nSomthing wrong")
            return
    # If last ranking was unranked
    if last_rank_num == THE_MAGIC_NUMBER:
        # And current rank is also unranked (in this condition, found should be false)
        if rank_num == THE_MAGIC_NUMBER:
            up_and_down_prefix = "⛔"
            up_and_down_comment = get_random_up_and_down_comment("same", up_and_down_comment_list,
                                                                 last_up_and_down_comment, history)
        # Chart IN
        else:
            up_and_down_prefix = "📈"
            up_and_down_comment = get_random_up_and_down_comment("chart_in", up_and_down_comment_list,
                                                                 last_up_and_down_comment, history)
    else:
        if rank_num > last_rank_num:
            up_and_down_prefix = "📉"
            if rank_num == THE_MAGIC_NUMBER:
                # Chart OUT (in this condition, found should be false)
                up_and_down_comment = get_random_up_and_down_comment("chart_out", up_and_down_comment_list,
                                                                     last_up_and_down_comment, history)
            else:
                # down
                up_and_down_comment = get_random_up_and_down_comment("down", up_and_down_comment_list,
                                                                     last_up_and_down_comment, history)
                rank_diff = " (" + str(rank_num - last_rank_num) + "위 하락)"
        # same
        elif rank_num == last_rank_num:
            up_and_down_prefix = "⛔"
            up_and_down_comment = get_random_up_and_down_comment("same", up_and_down_comment_list,
                                                                 last_up_and_down_comment, history)
        # up
        else:
            up_and_down_prefix = "📈"
            up_and_down_comment = get_random_up_and_down_comment("up", up_and_down_comment_list,
                                                                 last_up_and_down_comment, history)
            rank_diff = " (" + str(last_rank_num - rank_num) + "위 상승)"

    if rank_num < 10:
        comment = get_random_comment("top_10", comment_list, rank_num, last_rank_num, history)
    elif rank_num < 50:
        comment = get_random_comment("top_50", comment_list, rank_num, last_rank_num, history)
    elif rank_num < 100:
        comment = get_random_comment("top_100", comment_list, rank_num, last_rank_num, history)
    elif rank_num < 150:
        comment = get_random_comment("top_150", comment_list, rank_num, last_rank_num, history)
    elif rank_num <= 200:
        comment = get_random_comment("top_200", comment_list, rank_num, last_rank_num, history)

    save_last_rank(rank_num, up_and_down_comment, comment)
    if SPECIAL_COMMENT != "NONE":
        merged_comment = SPECIAL_COMMENT
    elif up_and_down_prefix == "📉" and comment != "" and found:
        merged_comment = up_and_down_comment + "그래도... " + comment
    else:
        merged_comment = up_and_down_comment + comment
    if not found:
        return (
            f"*[{up_and_down_prefix}오늘의 셩 앱스토어 순위]* {formatted_date}\n"
            f"{merged_comment}\n"
        )
    return (
        f"*[{up_and_down_prefix}오늘의 셩 앱스토어 순위]* {formatted_date}\n"
        f"{merged_comment}\n"
        f"*카테고리* : {category}\n"
        f"*순위* : {rank}{rank_diff}\n\n"
    )


def get_ranking_data(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_driver_path = "/usr/local/bin/chromedriver"
    print("Starting ChromeDriver...")
    service = Service(chrome_driver_path)
    print("ChromeDriver started.")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(url)
        # Wait for loading web page.
        # This timer value could be coordinated as per network environment
        time.sleep(10)

        elements = driver.find_elements(By.TAG_NAME, 'a')

        # Ranking Pattern
        pattern = re.compile(r".*앱.*위.*")

        found = False
        for element in elements:
            if pattern.search(element.text):
                found = True
                return element.text.strip(), found
        if not found:
            return "", found
    finally:
        driver.quit()
        print("ChromeDriver closed.")


def post_global_ranking_msg():
    ranking_data, found = get_ranking_data(APP_STORE_SYEONG_URL)
    ranking_data_sp, found_sp = get_ranking_data(APP_STORE_SMILEPASS_URL)

    msg = format_ranking(ranking_data, found, ranking_data_sp, found_sp)
    # track_id = _lookup_track_id_by_bundle(APP_BUNDLE_ID_SYEONG, ITUNES_SEARCH_COUNTRY)
    # Syeong AppStore Track ID Constant Hard coded
    track_id=1667568563
    if track_id:
        prev_keyword_rank = get_last_keyword_rank()
        now_keyword_rank = get_keyword_rank(ITUNES_SEARCH_TERM, ITUNES_SEARCH_COUNTRY, track_id)
        keyword_msg = format_keyword_message(ITUNES_SEARCH_TERM, ITUNES_SEARCH_COUNTRY, now_keyword_rank, prev_keyword_rank)
        save_last_keyword_rank(now_keyword_rank)
        msg += keyword_msg
    else:
        msg += "(참고) 번들ID로 trackId를 찾지 못해 키워드 순위를 건너뜀\n"
    try:
        # print(msg)
        response = client.chat_postMessage(channel=SLACK_NOTIFICATIONS_CHANNEL_ID,
                                           text=msg)
    except SlackApiError as e:
        print(f"Error posting slack message: {e}")
def post_ranking_msg():
    ranking_data, found = get_ranking_data(APP_STORE_SYEONG_URL)
    ranking_data_sp, found_sp = get_ranking_data(APP_STORE_SMILEPASS_URL)

    msg = format_ranking(ranking_data, found,ranking_data_sp,found_sp )
    try:
        response = client.chat_postMessage(channel=SLACK_NOTIFICATIONS_CHANNEL_ID,
                                           text=msg)
    except SlackApiError as e:
        print(f"Error posting slack message: {e}")



if __name__ == "__main__":
    post_global_ranking_msg()
