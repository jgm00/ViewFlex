from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
from datetime import datetime

def get_movie_theaters():
    url = "https://www.megabox.co.kr/booking/timetable"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get(url)
        time.sleep(15)
        
        selectors = [
            "button[date-data='2024.11.26']",
            "button.on[date-data='2024.11.26']",
            "button[date-data='2024.11.26'].on"
        ]
        
        data_button = None
        for selector in selectors:
            try:
                data_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue
                
        if data_button:
            driver.execute_script("arguments[0].click();", data_button)
            time.sleep(3)
        else:
            print("날짜 버튼을 찾을 수 없습니다.")
            return
        
        # 부산/대구/경상 지역 탭 클릭
        region_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn[data-area-cd='55']"))
        )
        actions = webdriver.ActionChains(driver)
        actions.move_to_element(region_button).click().perform()
        time.sleep(2)
        
        # 극장 목록 가져오기
        theater_elements = driver.find_elements(By.CSS_SELECTOR, ".theater-area-click a")
        theater_elements2 = driver.find_elements(By.CSS_SELECTOR, ".theater-type-box .theater-type .theater-name")
        
        theaters_data = []
        
        print("\n부산/대구/경상 지역 극장 목록:")
        try:
            # 각 극장별로 처리
            for i in range(len(theater_elements)):
                theater_name = theater_elements[i].text
                theater_name_detail = theater_elements2[i].text if i < len(theater_elements2) else "정보 없음"
                
                # 현재 선택된 극장의 첫 번째 상영 정보만 가져오기
                theater_time_div = driver.find_element(By.CSS_SELECTOR, ".theater-time")  # 첫 번째 요소만 선택
                
                # 영화 타입 정보 수집
                movie_type_element = theater_time_div.find_element(By.CSS_SELECTOR, ".theater-type-area")
                movie_type = movie_type_element.text # 2D, 2D ATMOS 등만 남김
                
                # 해당 타입의 상영 시간 정보 수집
                time_elements = theater_time_div.find_elements(By.CSS_SELECTOR, ".time-list-table td .time")
                showing_times = [time_element.text for time_element in time_elements]
                
                theater_data = {
                    "model": "movies.theater",
                    "pk": None,
                    "fields": {
                        "movie_id": 9999996,
                        "movie_name": "나의 히어로 아카데미아 더 무비: 유어 넥스트",
                        "chain": "메가박스",
                        "area": "대구/경북/경남/부산",
                        "theater": theater_name,
                        "screen": theater_name_detail,
                        "showing_times": showing_times,
                        "movie_type": movie_type
                    }
                }
                theaters_data.append(theater_data)
                
                print(f"극장명: {theater_name}")
                print(f"상세정보: {theater_name_detail}")
                print(f"상영타입: {movie_type}")
                print(f"상영시간: {showing_times}")
                print("-" * 30)
                
        except Exception as e:
            print(f"극장 데이터 처리 중 오류 발생: {e}")
        
        print("JSON 파일 저장 시도...")
        # 기존 JSON 파일이 있다면 읽어오기
        try:
            existing_data = []
            try:
                with open('combined_theaters.json', 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                # 기존 데이터의 마지막 pk 값을 찾음
                last_pk = max(item['pk'] for item in existing_data) if existing_data else 0
            except FileNotFoundError:
                last_pk = 0  # 파일이 없는 경우 pk를 0부터 시작
            
            # theaters_data 생성 시 pk 수정
            for idx, theater_data in enumerate(theaters_data):
                theater_data['pk'] = last_pk + idx + 1
            
            # 새로운 데이터를 기존 데이터에 추가
            combined_data = existing_data + theaters_data
            
            # 전체 데이터를 다시 저장
            with open('combined_theaters.json', 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            print("JSON 파일 저장 완료!")
        except Exception as e:
            print(f"JSON 파일 저장 중 오류 발생: {e}")

    except Exception as e:
        print(f"전체 프로세스 에러 발생: {e}")
    finally:
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    get_movie_theaters()

