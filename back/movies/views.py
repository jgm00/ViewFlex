from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from accounts.models import User
from django.shortcuts import get_object_or_404, get_list_or_404
from .models import Movie, Review, Theater
from .serializers import MovieSerializer, ReviewSerializer, LikedMoviesWithGenreStatsSerializer, TheaterSerializer, MovieWithTheatersSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Count
from collections import Counter
import random
from random import shuffle
from django.db.models.functions import ExtractYear
from datetime import datetime

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list(request):
    if request.method == 'GET':
        movies = list(Movie.objects.all())
        shuffle(movies)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review(request, movie_id):
    if request.method == 'GET':
        reviews = Review.objects.filter(movie__id=movie_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        movie = get_object_or_404(Movie, id=movie_id)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                movie=movie, 
                user=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # 리뷰 작성자와 요청 사용자가 동일한지 확인
    if review.user != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # 기존 데 로운 데이터를 병합
        data = {
            'content': request.data.get('content', review.content),
            'rating': request.data.get('rating', review.rating),
            'movie': review.movie.id  # 기존 movie ID 유지
        }
        
        serializer = ReviewSerializer(review, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def movie_like(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    user = request.user

    if movie.like_users.filter(pk=user.pk).exists():
        movie.like_users.remove(user)
        is_liked = False
    else:
        movie.like_users.add(user)
        is_liked = True

    return Response({
        'is_liked': is_liked,
        'like_count': movie.like_users.count()
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def liked(request):
    user = request.user
    liked_movies = user.like_movies.all() 
    serializer = MovieSerializer(liked_movies, many=True)
    return Response(serializer.data)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def liked_genre(request):
    user = request.user
    liked_movies = user.like_movies.all()
    
    serializer = LikedMoviesWithGenreStatsSerializer({'movies': liked_movies})
    
    genre_stats = serializer.data.get('genre_stats', [])
    
    return Response(genre_stats)

@api_view(['GET'])
@permission_classes([AllowAny])
def liked_genre_by_username(request, username):
    user = get_object_or_404(User, username=username)
    liked_movies = user.like_movies.all()
    serializer = LikedMoviesWithGenreStatsSerializer({'movies': liked_movies})
    genre_stats = serializer.data.get('genre_stats', [])
    return Response(genre_stats)

@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_genre(request):
    if not request.user.is_authenticated:
        # 첫 번째 그룹 (0-6) 섞기
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[0:7])
        serializer = MovieSerializer(top_movies[0:7], many=True)
        return Response(serializer.data)
    user = request.user
    liked_movies = user.like_movies.all()

    # 찜한 영화가 없으면 랜덤 추천
    if not liked_movies:
        random_movies = Movie.objects.order_by('?')[:21]
        serializer = MovieSerializer(random_movies, many=True)
        return Response(serializer.data)
    
    # 사용자가 좋아요한 영화들의 장르 카운팅
    genre_counter = Counter()
    for movie in liked_movies:
        genres = movie.genre_ids.all()
        genre_counter.update([genre.name for genre in genres])
    
    # 상위 3개 장르 선택
    top_genres = [genre for genre, _ in genre_counter.most_common(3)]
    
    # 현재 상영작 먼저 선택 (중복 제거)
    playing_movies = set()
    for genre in top_genres:
        playing_movie = Movie.objects.filter(
            genre_ids__name=genre, 
            is_playing=True
        ).distinct().order_by('-vote_average').first()
        
        if playing_movie:
            playing_movies.add(playing_movie)
    
    # 남은 영화 수 계산 (21 - 현재 상영작 수)
    remaining_count = 21 - len(playing_movies)
    movies_per_genre = remaining_count // len(top_genres)
    extra_movies = remaining_count % len(top_genres)
    
    # 장르별로 영화 수집 (중복 제거)
    recommended_movies = list(playing_movies)
    seen_movies = {movie.id for movie in playing_movies}
    
    for i, genre in enumerate(top_genres):
        # 이 장르에서 가져올 영화 수
        movies_to_get = movies_per_genre + (1 if i < extra_movies else 0)
        
        # 해당 장르의 영화 가져오기 (현재 상영작 제외)
        genre_movies = Movie.objects.filter(
            genre_ids__name=genre,
            is_playing=False
        ).exclude(
            id__in=seen_movies
        ).distinct().order_by('-vote_average')
        
        # 필요한 만큼만 가져오기
        for movie in genre_movies:
            if len(recommended_movies) >= 21:
                break
            if movie.id not in seen_movies:
                recommended_movies.append(movie)
                seen_movies.add(movie.id)
                movies_to_get -= 1
                if movies_to_get <= 0:
                    break
    
    # 혹시 21개가 안 되면 다른 장르에서 추가
    if len(recommended_movies) < 21:
        additional_movies = Movie.objects.exclude(
            id__in=seen_movies
        ).order_by('?')[:21-len(recommended_movies)]
        recommended_movies.extend(additional_movies)
    
    serializer = MovieSerializer(recommended_movies, many=True)
    
    return Response({
        'top_genres': top_genres,
        'movies': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_following(request):
    if not request.user.is_authenticated:
        # 두 번째 그룹 (7-13) 섞기
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[7:14])
        serializer = MovieSerializer(top_movies[7:14], many=True)
        return Response(serializer.data)
    user = request.user
    following_users = user.followings.all()

    # 팔로잉하는 유저가 없으면 랜덤 추천
    if not following_users:
        # 현재 상영작 3개
        playing_movies = list(Movie.objects.filter(is_playing=True).order_by('?')[:3])
        # 나머지 18개 (현재 상영작 제외)
        other_movies = list(Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=[movie.id for movie in playing_movies]
        ).order_by('?')[:18])
        recommended_movies = playing_movies + other_movies
        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)

    # 팔로잉하는 유저들이 좋아요한 영화들 수집 (중복 제거)
    following_liked_movies = Movie.objects.filter(
        like_users__in=following_users
    ).distinct()

    # 현재 상영작 중에서 팔로잉하는 유저들이 좋아요한 영화 먼저 선택
    playing_movies = list(following_liked_movies.filter(
        is_playing=True
    ).order_by('-vote_average', '?')[:3])

    # 3개가 안되면 다른 현재 상영작로 채우기 (중복 제거)
    if len(playing_movies) < 3:
        additional_playing = Movie.objects.filter(
            is_playing=True
        ).exclude(
            id__in=[movie.id for movie in playing_movies]
        ).order_by('?')[:3-len(playing_movies)]
        playing_movies.extend(additional_playing)

    # 이미 선택된 영화 ID 집합
    selected_ids = {movie.id for movie in playing_movies}

    # 팔로잉 유저가 좋아요한 영화 중 남은 영화 선택 (현재 상영작과 중복 제외)
    remaining_count = 21 - len(playing_movies)
    remaining_following_movies = list(following_liked_movies.filter(
        is_playing=False
    ).exclude(
        id__in=selected_ids
    ).order_by('-vote_average', '?')[:remaining_count])

    # 필요한 만큼만 선택하고 ID 추가
    recommended_movies = playing_movies
    for movie in remaining_following_movies:
        if movie.id not in selected_ids:
            recommended_movies.append(movie)
            selected_ids.add(movie.id)

    # 21개가 안되면 다른 영화로 채우기 (모든 이전 선택 제외)
    if len(recommended_movies) < 21:
        additional_movies = Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=selected_ids
        ).order_by('?')[:21-len(recommended_movies)]
        recommended_movies.extend(additional_movies)

    # 최종적으로 21개만 선택
    recommended_movies = recommended_movies[:21]

    # 결과 반환
    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_box_office(request):
    box_office_movies = Movie.objects.filter(
        id__range=(9999990, 9999999)
    ).order_by('-id')
    
    serializer = MovieSerializer(box_office_movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def movie_theaters(request, movie_id):
    try:
        theaters = Theater.objects.filter(movie_id=movie_id)
        
        # 체인과 지역으로 필터링
        chain = request.GET.get('chain')
        area = request.GET.get('area')
        
        if chain:
            theaters = theaters.filter(chain=chain)
        if area:
            theaters = theaters.filter(area=area)
        
        serializer = TheaterSerializer(theaters, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {"error": f"상영 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def theater_list(request):
    try:
        # 체인과 지역으로 필터링
        chain = request.GET.get('chain')
        area = request.GET.get('area')
        
        theaters = Theater.objects.all()
        
        if chain:
            theaters = theaters.filter(chain=chain)
        if area:
            theaters = theaters.filter(area=area)
            
        # 중복 제거 (같은 극장은 한 번만)
        unique_theaters = {}
        for theater in theaters:
            key = f"{theater.chain} {theater.theater}"
            if key not in unique_theaters:
                unique_theaters[key] = theater
        
        serializer = TheaterSerializer(unique_theaters.values(), many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {"error": f"극장 목록을 가져오는 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def movie_detail_with_theaters(request, movie_id):
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        theaters = Theater.objects.filter(movie_id=movie_id)
        
        # 영화 정보와 극장 정보를 함께 반환
        movie_serializer = MovieSerializer(movie)
        theater_serializer = TheaterSerializer(theaters, many=True)
        
        return Response({
            'movie': movie_serializer.data,
            'theaters': theater_serializer.data
        })
        
    except Exception as e:
        return Response(
            {"error": f"영화와 상영관 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def playing_movies(request):
    box_office_movies = Movie.objects.filter(
        is_playing=True
    ).order_by('-id')[:10]
    
    box_office_ids = set(movie.id for movie in box_office_movies)
    box_office_titles = set(movie.title for movie in box_office_movies)
    
    other_playing_movies = Movie.objects.filter(
        is_playing=True
    ).exclude(
        id__in=box_office_ids
    ).exclude(
        title__in=box_office_titles
    ).order_by('-release_date')
    
    all_movies = list(box_office_movies) + list(other_playing_movies)
    
    serializer = MovieSerializer(all_movies, many=True)
    return Response(serializer.data)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_reviewed_actors(request):
    if not request.user.is_authenticated:
        # 세 번째 그룹 (14-20) 섞기
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[14:21])
        serializer = MovieSerializer(top_movies[14:21], many=True)
        return Response(serializer.data)

    # 사용자가 리뷰한 영화들 가져오기
    user_reviews = Review.objects.filter(user=request.user).select_related('movie')
    reviewed_movie_ids = set(review.movie.id for review in user_reviews)
    
    # 배우 목록 수집
    actors_set = set()
    for review in user_reviews:
        movie = review.movie
        if movie.actors:
            for actor in movie.actors[:3]:
                actors_set.add(actor['name'])
    
    if not actors_set:
        # 배우 정보가 없는 경우 랜덤 추천
        playing_movies = list(Movie.objects.filter(
            is_playing=True
        ).exclude(
            id__in=reviewed_movie_ids
        ).order_by('?')[:3])
        
        other_movies = list(Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=reviewed_movie_ids
        ).order_by('?')[:18])
        
        recommended_movies = playing_movies + other_movies
        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)
    
    # 재 상영작 중에서 배우가 출연한 영화 찾기
    playing_recommended = []
    all_playing_movies = Movie.objects.filter(is_playing=True).exclude(id__in=reviewed_movie_ids)
    
    for movie in all_playing_movies:
        if movie.actors:
            movie_actors = {actor['name'] for actor in movie.actors[:3]}
            if actors_set & movie_actors:  # 교집합이 있는 경우
                playing_recommended.append(movie)
    
    # 상영작이 3개 미만인 경우 다른 상영작으로 채우기
    if len(playing_recommended) < 3:
        existing_ids = {m.id for m in playing_recommended}
        additional_playing = list(Movie.objects.filter(
            is_playing=True
        ).exclude(
            id__in=reviewed_movie_ids | existing_ids
        ).order_by('?')[:3-len(playing_recommended)])
        playing_recommended.extend(additional_playing)
    
    # 비상영작 중에서 배우가 출연한 영화 찾기
    other_recommended = []
    all_other_movies = Movie.objects.filter(
        is_playing=False
    ).exclude(
        id__in=reviewed_movie_ids
    )
    
    for movie in all_other_movies:
        if movie.actors:
            movie_actors = {actor['name'] for actor in movie.actors[:3]}
            if actors_set & movie_actors:  # 교집합이 있는 경우
                other_recommended.append(movie)
    
    # 최종 추천 목록 만들기
    playing_recommended = playing_recommended[:3]  # 상영작 3개
    
    # 비상영작 처리
    if len(other_recommended) > 18:
        other_recommended = random.sample(other_recommended, 18)
    elif len(other_recommended) < 18:
        existing_ids = {m.id for m in other_recommended} | {m.id for m in playing_recommended}
        additional_movies = list(Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=reviewed_movie_ids | existing_ids
        ).order_by('?')[:18-len(other_recommended)])
        other_recommended.extend(additional_movies)
    
    # 최종 추천 목록 합치기
    recommended_movies = playing_recommended + other_recommended
    
    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_release_date(request):
    if not request.user.is_authenticated:
        # 네 번째 그룹 (21-27) 섞기
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[21:28])
        serializer = MovieSerializer(top_movies[21:28], many=True)
        return Response(serializer.data)

    # 사용자가 좋아요한 영화들의 개봉 연도 수집
    liked_movies = request.user.like_movies.all()
    reviewed_movies = Review.objects.filter(user=request.user).select_related('movie')
    
    # 이미 본 영화 ID 목록
    watched_movie_ids = set(movie.id for movie in liked_movies) | \
                       set(review.movie.id for review in reviewed_movies)
    
    recommended_movies = []
    
    # 좋아요나 리뷰가 없는 경우, 다양한 연도의 영화 추천
    if not liked_movies.exists() and not reviewed_movies.exists():
        current_year = datetime.now().year
        
        # 5개 구간으로 나누어 추천
        for i in range(5):
            period_start = current_year - (i * 10) - 10
            period_end = current_year - (i * 10)
            
            period_movies = Movie.objects.filter(
                release_date__year__range=(period_start, period_end)
            ).order_by('?')[:5]
            
            recommended_movies.extend(period_movies)
    else:
        # 연도별 선호도 계산 및 기존 로직 실행
        year_preferences = {}
        
        for movie in liked_movies:
            year = str(movie.release_date.year)
            year_preferences[year] = year_preferences.get(year, 0) + 1
        
        for review in reviewed_movies:
            year = str(review.movie.release_date.year)
            weight = 1.5 if review.rating >= 7 else 1
            year_preferences[year] = year_preferences.get(year, 0) + weight
        
        if year_preferences:
            favorite_years = sorted(
                year_preferences.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            favorite_years = [int(year) for year, _ in favorite_years]
            
            for base_year in favorite_years:
                period_start = (base_year // 5) * 5
                period_end = period_start + 4
                
                year_movies = Movie.objects.filter(
                    release_date__year__range=(period_start, period_end)
                ).exclude(
                    id__in=watched_movie_ids
                ).order_by('?')[:7]
                
                recommended_movies.extend(year_movies)
    
    # 무조건 21개 채우기
    if len(recommended_movies) < 21:
        existing_ids = set(movie.id for movie in recommended_movies)
        additional_count = 21 - len(recommended_movies)
        
        # 남은 모든 영화 중에서 랜덤으로 선택
        additional_movies = Movie.objects.exclude(
            id__in=existing_ids | watched_movie_ids
        ).order_by('?')[:additional_count]
        
        # 그래도 부족하다면 이미 본 영화도 포함하여 선택
        if len(additional_movies) + len(recommended_movies) < 21:
            more_movies = Movie.objects.exclude(
                id__in=existing_ids
            ).order_by('?')[:21-len(recommended_movies)-len(additional_movies)]
            additional_movies = list(additional_movies) + list(more_movies)
        
        recommended_movies.extend(additional_movies)
    
    # 정확히 21개로 제한
    recommended_movies = recommended_movies[:21]
    
    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def search_movies(request):
    try:
        query = request.GET.get('query', '').strip()  # 공백 제거
        
        if not query:
            return Response([])

        # 검색어에서 모든 공백 제거하고 소문자로 변환
        query_normalized = query.lower().replace(" ", "")
        
        # 기본 쿼리셋
        movies = Movie.objects.all()
        
        # 제목으로 검색된 영화들 (정규화된 제목으로 비교)
        title_results = set()
        for movie in movies:
            movie_title_normalized = movie.title.lower().replace(" ", "")
            if query_normalized in movie_title_normalized:
                title_results.add(movie)
        
        # 배우 이름으로 검색
        actor_results = set()
        for movie in movies:
            if movie.actors:
                movie_actor_names = [actor['name'].lower().replace(" ", "") 
                                   for actor in movie.actors]
                if any(query_normalized in actor_name for actor_name in movie_actor_names):
                    actor_results.add(movie)
        
        # 제목 검색 결과와 배우 검색 결과 합치기
        all_results = list(title_results | actor_results)
        
        serializer = MovieSerializer(all_results, many=True)
        return Response(serializer.data)

    except Exception as e:
        print(f"Error in search_movies: {str(e)}")
        return Response(
            {"error": f"검색 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def filter_movies(request):
    try:
        genre_ids = request.GET.get('genre_ids')
        actors = request.GET.get('actors')
        
        movies = Movie.objects.all()
        
        if genre_ids:
            genre_id_list = [int(id) for id in genre_ids.split(',')]
            # 각 장르에 대해 개별적으로 필터링 (AND 조건)
            for genre_id in genre_id_list:
                movies = movies.filter(genre_ids__id=genre_id)
        
        if actors:
            actor_list = actors.split(',')
            filtered_movies = []
            
            for movie in movies:
                if movie.actors:  # actors 필드가 None이 아닌 경우에만 처리
                    # 모든 배우가 영화에 포함되어 있는지 확인
                    movie_actor_names = [actor['name'].lower().strip() for actor in movie.actors]
                    if all(actor.lower().strip() in movie_actor_names for actor in actor_list):
                        filtered_movies.append(movie)
            
            movies = filtered_movies
                
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)
            
    except Exception as e:
        print(f"Error in filter_movies: {str(e)}")  # 디버깅을 위한 로그
        return Response(
            {"error": f"필터링 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )