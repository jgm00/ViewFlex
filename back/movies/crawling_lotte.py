import requests
from datetime import datetime
import json

def get_movie_times_by_id(movies):
    movie_dict = {}
    for movie in movies:
        movie_code = movie["MovieCode"]
        if movie_code not in movie_dict:
            movie_dict[movie_code] = {
                "movie_name": movie["MovieNameKR"],
                "screen": movie["ScreenNameKR"],
                "movie_type": movie.get("FilmNameKR", "2D") or movie.get("FilmNameUS", "2D"),
                "showing_times": []
            }
        movie_dict[movie_code]["showing_times"].append(movie["StartTime"])
    return movie_dict

def get_lotte_theaters():
    theaters_data = []
    pk_counter = 1272
    theaters = [
        # 대구/경북 지역
        {"id": "1|0005|5012", "name": "대구광장"},
        {"id": "1|0005|5006", "name": "대구율하"},
        {"id": "1|0005|9107", "name": "대구현풍"},
        {"id": "1|0005|5005", "name": "동성로"},
        {"id": "1|0005|5016", "name": "상인"},
        {"id": "1|0005|5004", "name": "성서"},
        {"id": "1|0005|9057", "name": "프리미엄칠곡"},
        {"id": "1|0005|9080", "name": "상주"},
        {"id": "1|0005|9082", "name": "거창"},
        {"id": "1|0005|5013", "name": "구미공단"},
        {"id": "1|0005|9067", "name": "프리미엄구미센트럴"},
        
        # 서울 지역
        {"id": "1|0005|1013", "name": "가산디지털"},
        {"id": "1|0005|9094", "name": "가양"},
        {"id": "1|0005|9010", "name": "강동"},
        {"id": "1|0005|1004", "name": "건대입구"},
        {"id": "1|0005|1003", "name": "노원"},
        {"id": "1|0005|1023", "name": "도곡"},
        {"id": "1|0005|1012", "name": "서울대입구"},
        {"id": "1|0005|9104", "name": "수유"},
        {"id": "1|0005|1015", "name": "신도림"},
        {"id": "1|0005|1007", "name": "신림"},
        {"id": "1|0005|1002", "name": "영등포"},
        {"id": "1|0005|1021", "name": "은평(롯데몰)"},
        {"id": "1|0005|1005", "name": "홍대입구"},
        {"id": "1|0005|1010", "name": "합정"},
        
        # 경기/인천 지역
        {"id": "1|0005|3027", "name": "광명(광명사거리)"},
        {"id": "1|0005|3048", "name": "동탄"},
        {"id": "1|0005|3011", "name": "부천(신중동역)"},
        {"id": "1|0005|3003", "name": "부평"},
        {"id": "1|0005|3008", "name": "부평역사"},
        {"id": "1|0005|3043", "name": "서수원"},
        {"id": "1|0005|3024", "name": "수원(수원역)"},
        {"id": "1|0005|3007", "name": "안양(안양역)"},
        {"id": "1|0005|3040", "name": "용인역북"},
        {"id": "1|0005|3039", "name": "용인기흥"},
        {"id": "1|0005|3047", "name": "판교(창조경제밸리)"},
        
        # 경상도 지역
        {"id": "1|0005|9080", "name": "상주"},
        {"id": "1|0005|9082", "name": "거창"},

        {"id": "1|0005|5002", "name": "창원"},
        {"id": "1|0005|5001", "name": "울산(백화점)"},

        {"id": "1|0005|2006", "name": "센텀시티"},
        {"id": "1|0005|9115", "name": "부산장림"},
        {"id": "1|0005|2004", "name": "부산본점"},

    ]
    
    url = "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx"
    today = datetime.now().strftime("%Y-%m-%d")
    
    for theater in theaters:
        dic = {
            "MethodName": "GetPlaySequence",
            "channelType": "MA",
            "osType": "",
            "osVersion": "",
            "playDate": today,
            "cinemaID": theater["id"],
            "representationMovieCode": ""
        }
        
        parameters = {"paramList": str(dic)}
        
        try:
            print(f"극장 {theater['name']} 데이터 요청 중...")
            response = requests.post(url, data=parameters)
            print(f"응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'PlaySeqs' in data and 'Items' in data['PlaySeqs']:
                    movies = data['PlaySeqs']['Items']
                    print(f"영화 데이터 수: {len(movies)}")
                    
                    if movies:
                        print(f"첫 번째 영화 데이터 구조: {movies[0].keys()}")
                    
                    grouped_movies = get_movie_times_by_id(movies)
                    print(f"그룹화된 영화 수: {len(grouped_movies)}")
                    
                    for movie_code, movie_info in grouped_movies.items():
                        theater_data = {
                            "model": "movies.theater",
                            "pk": pk_counter,
                            "fields": {
                                "movie_id": movie_code,
                                "movie_name": movie_info["movie_name"],
                                "chain": "롯데시네마",
                                "area": "경북",
                                "theater": theater["name"],
                                "screen": movie_info["screen"],
                                "showing_times": movie_info["showing_times"],
                                "movie_type": movie_info["movie_type"]
                            }
                        }
                        theaters_data.append(theater_data)
                        pk_counter += 1
                else:
                    print(f"극장 {theater['name']}의 데이터 구조가 예상과 다릅니다.")
                    
        except Exception as e:
            print(f"극장 {theater['name']} 처리 중 에러 발생: {str(e)}")
    
    print(f"총 수집된 데이터 수: {len(theaters_data)}")
    
    # JSON 파일로 저장
    if theaters_data:
        try:
            with open('lotte_theaters.json', 'w', encoding='utf-8') as f:
                json.dump(theaters_data, f, ensure_ascii=False, indent=2)
            print("JSON 파일 저장 완료!")
        except Exception as e:
            print(f"JSON 파일 저장 중 오류 발생: {e}")
    else:
        print("저장할 데이터가 없습니다.")

if __name__ == "__main__":
    get_lotte_theaters()