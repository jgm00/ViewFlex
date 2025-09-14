import json

def merge_coordinates():
    # 극장 좌표 데이터 읽기
    with open('fixtures/theater_coordinates.json', 'r', encoding='utf-8') as f:
        coordinates = json.load(f)
    
    # 기존 극장 데이터 읽기
    with open('fixtures/combined_theaters.json', 'r', encoding='utf-8') as f:
        theaters = json.load(f)
    
    # 좌표 데이터 병합
    for item in theaters:
        if item['model'] == 'movies.theater':
            theater_name = f"{item['fields']['chain']} {item['fields']['theater']}"
            if theater_name in coordinates:
                item['fields']['lat'] = coordinates[theater_name]['lat']
                item['fields']['lng'] = coordinates[theater_name]['lng']
    
    # 병합된 데이터 저장
    with open('fixtures/theaters_with_coordinates.json', 'w', encoding='utf-8') as f:
        json.dump(theaters, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    merge_coordinates()