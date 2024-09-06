from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time
from dotenv import load_dotenv
import re

########################## Environments ###############################
load_dotenv()
APP_STORE_SYEONG_URL = os.environ['APP_STORE_SYEONG_URL']
LAST_REVIEW_FILE_PATH = "crawlers/outputs/last_review_id.json"


#########################################################################

# This function gets data from chrom browser and parse App store ranking data
def post_ranking_data():
    # 크롬 브라우저 옵션 설정 (헤드리스 모드로 실행)
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 크롬 드라이버 경로 설정 (GitHub Actions 또는 로컬환경에 맞춰 경로 설정)
    chrome_driver_path = "/usr/local/bin/chromedriver"

    # 크롬 드라이버 서비스 설정
    service = Service(chrome_driver_path)

    # Selenium 웹드라이버 설정
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # URL로 이동
    driver.get(APP_STORE_SYEONG_URL)

    # 페이지가 로드될 시간을 기다림 (네트워크 상황에 따라 조정)
    time.sleep(5)

    # 'a' 태그를 찾음
    elements = driver.find_elements(By.TAG_NAME, 'a')

    # 정규표현식 패턴: "(아무 문자열) 앱 (아무 문자열) 위 (아무 문자열)"
    pattern = re.compile(r".*앱.*위.*")

    found = False
    for element in elements:
        # 각 'a' 태그에서 텍스트를 가져와 정규표현식 패턴과 매칭
        if pattern.search(element.text):
            print(f"순위 정보: {element.text.strip()}")
            found = True
            break

    if not found:
        print("매칭되는 순위 정보가 없습니다.")

    # 브라우저 닫기
    driver.quit()


if __name__ == "__main__":
    post_ranking_data()
