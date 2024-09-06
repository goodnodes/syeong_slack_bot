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
LAST_REVIEW_FILE_PATH = "crawlers/outputs/last_review_id.json"


#########################################################################

# This function gets data from chrom browser and parse App store ranking data

def get_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_driver_path = "/usr/local/bin/chromedriver"
    service = Service(chrome_driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)
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
            f"[📈오늘의 셩 앱스토어 순위]\n\n"
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
                rank_number = rank_number_match.group()
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
            f"[📈오늘의 셩 앱스토어 순위]\n\n"
            f"{comment}\n"
            f"카테고리 : {category}\n"
            f"순위 : {rank}\n\n"
            f"시간 : {now.strftime('%Y-%m-%d %H:%M')}"

        )

def get_ranking_data():
    driver = get_chrome_driver()
    # URL로 이동
    driver.get(APP_STORE_SYEONG_URL)
    # Wait for loading web page.
    # This timer value could be coordinated as per network environment
    time.sleep(5)

    elements = driver.find_elements(By.TAG_NAME, 'a')

    #Ranking Pattern
    pattern = re.compile(r".*앱.*위.*")

    found = False
    for element in elements:
        # 각 'a' 태그에서 텍스트를 가져와 정규표현식 패턴과 매칭
        if pattern.search(element.text):
            format_ranking(element.text.strip())
            found = True
            driver.quit()
            return element.text.strip(), found

    if not found:
        driver.quit()
        return "", found

    # 브라우저 닫기
    driver.quit()


def post_ranking_msg():
    ranking_data, found = get_ranking_data()
    msg = format_ranking(ranking_data, found)
    print(f"{msg}")


if __name__ == "__main__":
    post_ranking_msg()
