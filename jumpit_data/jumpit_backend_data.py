from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.jobkorea.co.kr/Search/?stext=백엔드개발자&tabType=recruit")
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-default > ul.clear > li"))
)
time.sleep(2)

cards = driver.find_elements(By.CSS_SELECTOR, "div.list-default > ul.clear > li")

if cards:
    first_card = cards[0]
    title = first_card.find_element(By.CSS_SELECTOR, "div.information-title > a").text
    link = first_card.find_element(By.CSS_SELECTOR, "div.information-title > a").get_attribute("href")
    company = first_card.find_element(By.CSS_SELECTOR, "div.list-section-corp").text

    print("✅ 첫 번째 공고 확인")
    print(f"회사명: {company}")
    print(f"제목: {title}")
    print(f"링크: {link}")
else:
    print("❌ 공고 리스트를 찾을 수 없습니다")

driver.quit()
