import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_detail_info(driver_detail, link):
    driver_detail.get(link)
    time.sleep(5)
    
    # 회사명 추출 시도
    company = "회사명 추출 실패"
    try:
        # 상세 페이지에서 회사명 추출 시도 (여러 선택자 시도)
        selectors = [
            ".company_name", 
            "[class*='company']",
            ".header_top_company",
            ".company",
            "h1.company",
            ".sc-*[class*='company']",
            ".logo_company"
        ]
        
        for selector in selectors:
            try:
                company_elem = driver_detail.find_element(By.CSS_SELECTOR, selector)
                company = company_elem.text.strip()
                if company:
                    print(f"회사명: {company} (선택자: {selector})")
                    break
            except:
                continue
        
        # 선택자로 찾지 못한 경우, 페이지 소스에서 회사명 찾기 시도
        if company == "회사명 추출 실패":
            # 페이지 소스 확인
            page_source = driver_detail.page_source
            print("상세 페이지 HTML 일부:")
            print(page_source[:1000])  # 처음 1000자만 출력
            
            # 페이지의 모든 텍스트 요소 확인
            elements = driver_detail.find_elements(By.XPATH, "//*[text()]")
            print("\n상세 페이지의 모든 텍스트 요소:")
            for elem in elements[:30]:  # 처음 30개 요소만 출력
                try:
                    text = elem.text.strip()
                    if text and len(text) < 30:  # 짧은 텍스트만 출력 (회사명일 가능성이 높음)
                        tag_name = elem.tag_name
                        class_name = elem.get_attribute("class")
                        print(f"태그: {tag_name}, 클래스: {class_name}, 텍스트: {text}")
                except:
                    continue
    except Exception as e:
        print(f"회사명 추출 중 예외 발생: {e}")
    
    # 기존 상세 정보 추출
    detail_info = {"주요업무": "없음", "자격요건": "없음", "회사명": company}
    try:
        dt_elements = driver_detail.find_elements(By.CSS_SELECTOR, "dt.sc-e76d2562-1")
        for dt in dt_elements:
            heading = dt.text.strip()
            if heading in ["주요업무", "자격요건"]:
                parent = dt.find_element(By.XPATH, "..")
                pre = parent.find_element(By.TAG_NAME, "pre")
                detail_info[heading] = pre.text.strip()
    except:
        pass
    
    return detail_info

job_list = []
keyword = "백엔드개발자"
base_url = "https://jumpit.saramin.co.kr"

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")

driver_main = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver_detail = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

for page in range(1, 2):
    print(f"백엔드 (한글+영어) - 페이지 {page}")
    url = f"{base_url}/search?sort=relation&keyword={keyword}&page={page}"
    driver_main.get(url)
    time.sleep(5)

    cards = driver_main.find_elements(By.CSS_SELECTOR, "a[href^='/position/']")
    print(f"찾은 카드 수: {len(cards)}")

    for card in cards:
        try:
            # 제목만 카드에서 추출
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.position_card_info_title")
                title = title_elem.text.strip().replace("\n", " ")
            except:
                try:
                    title_elem = card.find_element(By.TAG_NAME, "h2")
                    title = title_elem.text.strip().replace("\n", " ")
                except:
                    title = "제목 추출 실패"
            
            print(f"공고명: {title}")
            
            # 제목 필터링: '백엔드' or 'backend'
            title_lower = title.lower()
            if '백엔드' in title_lower or 'backend' in title_lower:
                href = card.get_attribute("href")
                if not href.startswith("http"):
                    href = base_url + href
                
                # 기술 스택 카드에서 추출
                try:
                    skill_items = card.find_elements(By.CSS_SELECTOR, "ul.sc-15ba67b8-1.iFMgIl li")
                    skills = [skill.text.strip() for skill in skill_items]
                except:
                    try:
                        skill_items = card.find_elements(By.CSS_SELECTOR, "ul li")
                        skills = [skill.text.strip() for skill in skill_items]
                    except:
                        skills = ["기술 스택 정보 없음"]
                
                # 상세 페이지에서 회사명과 추가 정보 추출
                detail = get_detail_info(driver_detail, href)
                company = detail["회사명"]
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
            print(f"카드 처리 중 예외 발생: {e}")

driver_main.quit()
driver_detail.quit()

# CSV 저장
with open("jumpit_backend_data.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["회사명", "공고", "제목", "링크", "기술 스택", "주요업무", "자격요건"])
    writer.writerows(job_list)

print("백엔드(한글+영어) CSV 저장 완료: jumpit_backend_all.csv")