import requests
import json
import time

def get_actor_korean_name(actor_id):
    api_key = '20175ca098192d680b06f256a904f0db'
    url = f'https://api.themoviedb.org/3/person/{actor_id}?api_key={api_key}&language=ko-KR'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('name', '')  # 한국어 이름이 있으면 반환
    except Exception as e:
        print(f"Error fetching Korean name for actor {actor_id}: {str(e)}")
    return None

def get_movie_credits(movie_id):
    api_key = '20175ca098192d680b06f256a904f0db'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=ko-KR'
    
    headers = {
        'accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            actors = data.get('cast', [])[:5]
            result = []
            
            for actor in actors:
                if actor.get('profile_path'):
                    korean_name = get_actor_korean_name(actor['id'])
                    time.sleep(0.2)  # API 호출 제한 고려
                    
                    result.append({
                        'id': actor['id'],
                        'name': korean_name or actor.get('name', ''),  # 한국어 이름이 없으면 원어 이름 사용
                        'character': actor.get('character', ''),
                        'profile_path': actor.get('profile_path', '')
                    })
            return result
        else:
            print(f"Error fetching data for movie {movie_id}: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception occurred for movie {movie_id}: {str(e)}")
    return None

def update_movies_with_actors():
    # 기존 fixtures 파일 읽기
    input_file = 'movies/fixtures/movies.json'
    backup_file = 'movies/fixtures/movies_backup.json'
    
    # 백업 파일 생성
    with open(input_file, 'r', encoding='utf-8') as f:
        movies = json.load(f)
        with open(backup_file, 'w', encoding='utf-8') as backup:
            json.dump(movies, backup, ensure_ascii=False, indent=4)
    
    print(f"Backup created at {backup_file}")
    
    # 각 영화에 배우 정보 추가
    total_movies = len(movies)
    for i, movie in enumerate(movies, 1):
        if 'actors' not in movie['fields']:  # 배우 정보가 없는 경우에만 추가
            movie_id = movie['fields']['id']
            print(f"Processing movie {i}/{total_movies}: {movie['fields']['title']}")
            
            actors = get_movie_credits(movie_id)
            if actors:
                movie['fields']['actors'] = actors
                print(f"Added {len(actors)} actors")
            else:
                movie['fields']['actors'] = []
                print("No actors found or error occurred")
            
            # API 호출 제한을 위한 딜레이
            time.sleep(0.5)  # 0.5초 대기
    
    # 업데이트된 데이터 저장
    try:
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)
        print("\nSuccessfully updated movies.json with actor information")
    except Exception as e:
        print(f"\nError saving file: {str(e)}")
        print("You can restore from backup if needed")

if __name__ == "__main__":
    update_movies_with_actors()