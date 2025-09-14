import json
import requests
import time

def get_coordinates(place_name):
    KAKAO_API_KEY = "import.meta.env.VITE_KAKAO_MAP_KEY"
    
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "KA": "Origin",
        "Host": "dapi.kakao.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    
    search_query = f"{place_name} 영화관"
    print(f"Searching for: {search_query}")
    
    params = {
        "query": search_query,
        "size": 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("documents"):
                place = data["documents"][0]
                print(f"Found: {place['place_name']}, {place['address_name']}")
                return {
                    "lat": float(place["y"]),
                    "lng": float(place["x"])
                }
    except Exception as e:
        print(f"Error during API request: {str(e)}")
    
    return None

def collect_theater_coordinates():
    try:
        with open('fixtures/combined_theaters.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        unique_theaters = set()
        theater_coordinates = {}
        
        for item in data:
            if item['model'] == 'movies.theater':
                chain = item['fields']['chain']
                theater = item['fields']['theater']
                if theater.startswith(chain):
                    theater_name = theater
                else:
                    theater_name = f"{chain} {theater}"
                unique_theaters.add(theater_name)
        
        total = len(unique_theaters)
        print(f"총 {total}개의 극장 좌표를 수집합니다...")
        
        for i, theater in enumerate(unique_theaters, 1):
            print(f"\nCollecting coordinates for: {theater} ({i}/{total})")
            coords = get_coordinates(theater)
            if coords:
                theater_coordinates[theater] = coords
                print(f"Success: {theater} -> lat: {coords['lat']}, lng: {coords['lng']}")
            else:
                print(f"Failed to get coordinates for: {theater}")
            time.sleep(0.5)
        
        with open('fixtures/theater_coordinates.json', 'w', encoding='utf-8') as f:
            json.dump(theater_coordinates, f, ensure_ascii=False, indent=2)
        
        print(f"\n좌표 수집 완료! 총 {len(theater_coordinates)}개의 극장 좌표가 저장되었습니다.")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    collect_theater_coordinates()