import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_detail_info(driver_detail, link):
    driver_detail.get(link)
    time.sleep(2)
    detail_info = {"주요업무": "없음", "자격요건": "없음"}
    try:
        dt_elements = driver_detail.find_elements(By.CSS_SELECTOR, "dt.sc-e76d2562-1")
        for dt in dt_elements:
            heading = dt.text.strip()
            if heading in detail_info:
                parent = dt.find_element(By.XPATH, "..")
                pre = parent.find_element(By.TAG_NAME, "pre")
                detail_info[heading] = pre.text.strip()
    except:
        pass
    return detail_info

job_list = []
keyword = "백엔드개발자"
base_url = "https://jumpit.saramin.co.kr"

driver_main = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver_detail = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

for page in range(1, 4):
    print(f"백엔드 (한글+영어) - 페이지 {page}")
    url = f"{base_url}/search?sort=relation&keyword={keyword}&page={page}"
    driver_main.get(url)
    time.sleep(3)

    cards = driver_main.find_elements(By.CSS_SELECTOR, "a[href^='/position/']")

    for card in cards:
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, "h2.position_card_info_title")
            full_title = title_elem.text.strip().replace("\n", " ")

            company_match = re.search(r'\[(.*?)\]', full_title)
            company = company_match.group(1) if company_match else "회사명 없음"
            title = full_title.replace(f"[{company}]", "").strip()

            # 제목 필터: '백엔드' or 'backend'
            title_lower = title.lower()
            if '백엔드' in title_lower or 'backend' in title_lower:
                href = card.get_attribute("href")
                if not href.startswith("http"):
                    href = base_url + href

                skill_items = card.find_elements(By.CSS_SELECTOR, "ul.sc-15ba67b8-1.iFMgIl li")
                skills = [skill.text.strip() for skill in skill_items]

                detail = get_detail_info(driver_detail, href)
                main_task = detail["주요업무"]
                qualification = detail["자격요건"]

                print(f"{company} / {title}")
                job_list.append([
                    company,
                    "백엔드 개발자",
                    title,
                    href,
                    ", ".join(skills),
                    main_task,
                    qualification
                ])

        except Exception as e:
            print(f"예외 발생: {e}")

driver_main.quit()
driver_detail.quit()

# CSV 저장
with open("jumpit_backend_all.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["회사명", "공고", "제목", "링크", "기술 스택", "주요업무", "자격요건"])
    writer.writerows(job_list)

print("백엔드(한글+영어) CSV 저장 완료: jumpit_backend_all.csv")
