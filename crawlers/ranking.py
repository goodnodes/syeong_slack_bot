from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import time
from dotenv import load_dotenv
import re
from datetime import datetime

########################## Environments ###############################
load_dotenv()
APP_STORE_SYEONG_URL = os.environ['APP_STORE_SYEONG_URL']

#########################################################################


def format_ranking(ranking, found):
    now = datetime.now()
    # Just set default value
    # This Default value never be used as a result in expected scenarios.
    category = "건강 및 피트니스"
    rank = "1위"
    rank_number = 1
    comment = "Good"
    if not found:
        return (
            f"[📈오늘의 셩 앱스토어 순위]\n"
            f"😭안타깝지만 앱 스토어 차트에 셩이 없어요.\n\n"
            f"시간 : {now.strftime('%Y-%m-%d %H:%M')}"
        )
    if "앱" in ranking:
        parts = ranking.split("앱")
        if len(parts) == 2:
            category = parts[0].strip()
            rank = parts[1].strip()

            rank_number_match = re.search(r'\d', rank)
            if rank_number_match:
                rank_number = int(rank_number_match.group())
    print(rank_number)
    if rank_number < 10:
        comment = "🐐GOAT"
    elif rank_number < 50:
        comment = "절대 월드클래스 아닙니다."
    elif rank_number < 100:
        comment = "TOP💯 Congratulations!!! "
    elif rank_number < 150:
        comment = "조금만 더 힘내면 TOP💯..! 화이팅 !!💪"
    else:
        comment = "🌊️🏊🏻‍️🏊‍🏊🏻🌊가즈아!!! 🌊️🏊🏻‍️🏊‍🏊🏻🌊️"
    return (
        f"[📈오늘의 셩 앱스토어 순위]\n"
        f"{comment}\n"
        f"카테고리 : {category}\n"
        f"순위 : {rank}\n\n"
        f"시간 : {now.strftime('%Y-%m-%d %H:%M')}"

    )


def get_ranking_data():
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
        driver.get(APP_STORE_SYEONG_URL)
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


def post_ranking_msg():
    ranking_data, found = get_ranking_data()
    msg = format_ranking(ranking_data, found)
    print(f"{msg}")


if __name__ == "__main__":
    post_ranking_msg()
