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
            actors = data.get('cast', [])[:5]  # 상위 5명의 배우만 가져오기
            result = []
            
            for actor in actors:
                if actor.get('profile_path'):  # 프로필 이미지가 있는 배우만 포함
                    korean_name = get_actor_korean_name(actor['id'])
                    time.sleep(0.2)  # API 호출 제한 고려
                    
                    result.append({
                        'id': actor['id'],
                        'name': korean_name or actor.get('name', ''),
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

def update_box_office_with_actors():
    input_file = 'movies/fixtures/box_office.json'
    backup_file = 'movies/fixtures/box_office_backup.json'
    
    # 백업 파일 생성
    with open(input_file, 'r', encoding='utf-8') as f:
        movies = json.load(f)
        with open(backup_file, 'w', encoding='utf-8') as backup:
            json.dump(movies, backup, ensure_ascii=False, indent=4)
    
    print(f"Backup created at {backup_file}")
    print(f"Total movies to process: {len(movies)}")
    
    # 각 영화에 배우 정보 추가
    total_movies = len(movies)
    processed_count = 0
    
    for i, movie in enumerate(movies, 1):
        movie_id = movie['fields']['id']
        title = movie['fields']['title']
        
        print(f"\nProcessing ({i}/{total_movies}): {title}")
        
        # 이미 배우 정보가 있는지 확인
        if 'actors' in movie['fields'] and movie['fields']['actors']:
            print(f"Skipping {title} - already has actor information")
            continue
            
        actors = get_movie_credits(movie_id)
        if actors:
            movie['fields']['actors'] = actors
            processed_count += 1
            print(f"✓ Added {len(actors)} actors for {title}")
        else:
            movie['fields']['actors'] = []
            print(f"✗ No actors found for {title}")
        
        # 진행률 표시
        progress = (i / total_movies) * 100
        print(f"Progress: {progress:.1f}%")
        
        time.sleep(0.5)  # API 호출 제한을 위한 딜레이
    
    # 업데이트된 데이터 저장
    try:
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully updated {processed_count} movies with actor information")
    except Exception as e:
        print(f"\nError saving file: {str(e)}")
        print("You can restore from backup if needed")

if __name__ == "__main__":
    update_box_office_with_actors()