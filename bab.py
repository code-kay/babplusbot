import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import holidays
from datetime import date, timedelta

kr_holidays = holidays.KR()
today = date.today() + timedelta(days=1)

# 오늘이 공휴일인지 확인
if today in kr_holidays:
    print(f"내일은 공휴일입니다. ({kr_holidays.get(today)}) 작업을 중단합니다.")

else:
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    BLOG_URL = os.getenv('BLOG_URL')
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 필요한 경우 헤드리스 모드 사용
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")


    # ChromeDriver 설정
    service = Service(ChromeDriverManager().install())

    # ChromeDriver 실행
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Selenium을 사용한 페이지 열기
    driver.get(BLOG_URL)

    # 네이버 블로그 iframe 로딩 대기
    wait = WebDriverWait(driver, 10)
    iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))

    # iframe으로 전환
    driver.switch_to.frame(iframe)

    # 페이지가 로드될 때까지 대기 후, 첫 번째 이미지가 있는 se-main-container 클래스 로딩 대기
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'se-main-container')))

    # 페이지 소스 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # se-main-container 클래스 내에서 첫 번째 이미지 찾기
    container = soup.find('div', class_='se-main-container')
    first_img = container.find('img') if container else None

    if first_img and first_img.get('src'):
        img_url = first_img['src']
        print(f"이미지 URL: {img_url}")
        
        # 웹훅으로 전송
        data = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "🍽 다음 밥 플러스 메뉴 🍽",
                                "size": "Large",
                                "weight": "bolder"
                            },
                            {
                                "type": "Image",
                                "url": img_url,
                            }
                        ]
                    }
                }
            ]
        }

        webhook_response = requests.post(WEBHOOK_URL, json=data)
        print(f'웹훅 전송 상태 코드: {webhook_response.status_code}')

    else:
        print("첫 번째 이미지를 찾을 수 없습니다.")

    driver.quit()
