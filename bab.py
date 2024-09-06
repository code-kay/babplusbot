import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pytesseract
from PIL import Image
from io import BytesIO
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


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
url = 'https://blog.naver.com/babplus123/223112282256'
driver.get(url)

# 네이버 블로그 iframe에 접근
iframe = driver.find_element(By.TAG_NAME, 'iframe')
driver.switch_to.frame(iframe)

# 페이지 소스 가져오기
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 첫 번째 이미지 가져오기
first_img = soup.find('img')
if first_img and first_img.get('src'):
    img_url = first_img['src']
    print(f"이미지 URL: {img_url}")
    
    # 이미지 URL에서 데이터 가져오기
    img_response = requests.get(img_url)
    if img_response.status_code != 200:
        raise Exception(f"이미지를 가져오지 못했습니다. 상태 코드: {img_response.status_code}")
    
    # 메모리 내에서 이미지를 열기
    image = Image.open(BytesIO(img_response.content))
    
    # Tesseract OCR로 텍스트 추출
    text = pytesseract.image_to_string(image, lang='kor')  # 한국어 인식
    print(f"추출된 텍스트: {text}")
    
    # 웹훅으로 전송
    webhook_url = 'https://prod-21.southeastasia.logic.azure.com:443/workflows/4170e84816d5479b8561351ec691e162/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=w_kQ40iVvmJoPBIWK6Iqpk5THr6_TIhABj2HmjIsulQ'
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
                            "weight": "Bolder",
                            "size": "Large",
                            "text": text,  # 추출된 텍스트를 여기 삽입
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }
    
    webhook_response = requests.post(webhook_url, json=data)
    
    if webhook_response.status_code == 200:
        print('웹훅으로 텍스트를 성공적으로 전송했습니다.')
    else:
        print(f'웹훅 전송 실패: {webhook_response.status_code}')
else:
    print("첫 번째 이미지를 찾을 수 없습니다.")

driver.quit()
