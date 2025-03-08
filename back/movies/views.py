from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from accounts.models import User
from django.shortcuts import get_object_or_404
from .models import Movie, Review, Theater
from .serializers import (
    MovieSerializer, ReviewSerializer, LikedMoviesWithGenreStatsSerializer, 
    TheaterSerializer
)
from django.db.models import Count
from collections import Counter
import random
from datetime import datetime

RECOMMENDATIONS_COUNT = 21  # 추천 영화 개수
PLAYING_MOVIES_COUNT = 3    # 상영 중인 영화 개수
BOX_OFFICE_TOP = 10         # 박스오피스 상위 영화 개수

# 영화 관련련 엔드포인트

"""모든 영화 목록 조회"""
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list(request):
    movies = list(Movie.objects.all())
    random.shuffle(movies)
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


"""특정 영화의 상세 정보 조회"""
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# 리뷰 관련 엔드포인트

"""영화 리뷰 목록 조회 리뷰 작성"""
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review(request, movie_id):
    if request.method == 'GET':
        reviews = Review.objects.filter(movie_id=movie_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        movie = get_object_or_404(Movie, id=movie_id)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(movie=movie, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""특정 리뷰 조회, 수정, 삭제"""
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if review.user != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        data = {
            'content': request.data.get('content', review.content),
            'rating': request.data.get('rating', review.rating),
            'movie': review.movie.id 
        }
        
        serializer = ReviewSerializer(review, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 좋아요 관련 엔드포인트

"""영화 좋아요 """
@api_view(['POST'])
@permission_classes([AllowAny])
def movie_like(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    user = request.user

    # 이미 좋아요를 눌렀으면 취소, 아니면 추가
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

"""좋아요한 영화 목록 조회"""
@api_view(['GET'])
@permission_classes([AllowAny])
def liked(request):
    user = request.user
    liked_movies = user.like_movies.all() 
    serializer = MovieSerializer(liked_movies, many=True)
    return Response(serializer.data)


"""현재 사용자가 좋아요한 영화들의 장르 통계를 조회"""
@api_view(['GET'])
@permission_classes([AllowAny])
def liked_genre(request):
    user = request.user
    liked_movies = user.like_movies.all()
    
    serializer = LikedMoviesWithGenreStatsSerializer({'movies': liked_movies})
    genre_stats = serializer.data.get('genre_stats', [])
    
    return Response(genre_stats)

"""특정 사용자가 좋아요한 영화들의 장르 통계를 조회"""
@api_view(['GET'])
@permission_classes([AllowAny])
def liked_genre_by_username(request, username):
    user = get_object_or_404(User, username=username)
    liked_movies = user.like_movies.all()
    serializer = LikedMoviesWithGenreStatsSerializer({'movies': liked_movies})
    genre_stats = serializer.data.get('genre_stats', [])
    return Response(genre_stats)

# 영화 추천 관련 엔드포인트

"""사용자의 장르 선호도에 기반한 영화 추천 (TOP 3 장르르)"""
@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_genre(request):
    if not request.user.is_authenticated:
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[0:7])
        serializer = MovieSerializer(top_movies[0:7], many=True)
        return Response(serializer.data)
        
    user = request.user
    liked_movies = user.like_movies.all()

    if not liked_movies:
        random_movies = Movie.objects.order_by('?')[:RECOMMENDATIONS_COUNT]
        serializer = MovieSerializer(random_movies, many=True)
        return Response(serializer.data)
    
    genre_counter = Counter()
    for movie in liked_movies:
        genres = movie.genre_ids.all()
        genre_counter.update([genre.name for genre in genres])
    
    # 상위 3개 장르 선택
    top_genres = [genre for genre, _ in genre_counter.most_common(3)]
    
    playing_movies = set()
    for genre in top_genres:
        playing_movie = Movie.objects.filter(
            genre_ids__name=genre, 
            is_playing=True
        ).distinct().order_by('-vote_average').first()
        
        if playing_movie:
            playing_movies.add(playing_movie)
    

    remaining_count = RECOMMENDATIONS_COUNT - len(playing_movies)
    movies_per_genre = remaining_count // len(top_genres)
    extra_movies = remaining_count % len(top_genres)
    

    recommended_movies = list(playing_movies)
    seen_movies = {movie.id for movie in playing_movies}
    
    for i, genre in enumerate(top_genres):

        movies_to_get = movies_per_genre + (1 if i < extra_movies else 0)
        

        genre_movies = Movie.objects.filter(
            genre_ids__name=genre,
            is_playing=False
        ).exclude(
            id__in=seen_movies
        ).distinct().order_by('-vote_average')
        

        for movie in genre_movies:
            if len(recommended_movies) >= RECOMMENDATIONS_COUNT:
                break
            if movie.id not in seen_movies:
                recommended_movies.append(movie)
                seen_movies.add(movie.id)
                movies_to_get -= 1
                if movies_to_get <= 0:
                    break
    

    if len(recommended_movies) < RECOMMENDATIONS_COUNT:
        additional_movies = Movie.objects.exclude(
            id__in=seen_movies
        ).order_by('?')[:RECOMMENDATIONS_COUNT-len(recommended_movies)]
        recommended_movies.extend(additional_movies)
    
    serializer = MovieSerializer(recommended_movies, many=True)
    
    return Response({
        'top_genres': top_genres,
        'movies': serializer.data
    })


"""팔로우 중인 사용자가 좋아요한 영화를 추천"""
@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_following(request):
    if not request.user.is_authenticated:
        # 비인증 사용자의 경우 평점이 높은 영화를 무작위로 섞어서 추천
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[7:14])
        serializer = MovieSerializer(top_movies[7:14], many=True)
        return Response(serializer.data)
        
    user = request.user
    following_users = user.followings.all()

    # 팔로우 중인 사용자가 없으면 무작위 추천
    if not following_users:
        playing_movies = list(Movie.objects.filter(is_playing=True).order_by('?')[:PLAYING_MOVIES_COUNT])
        other_movies = list(Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=[movie.id for movie in playing_movies]
        ).order_by('?')[:RECOMMENDATIONS_COUNT-PLAYING_MOVIES_COUNT])
        
        recommended_movies = playing_movies + other_movies
        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)

    following_liked_movies = Movie.objects.filter(
        like_users__in=following_users
    ).distinct()
    playing_movies = list(following_liked_movies.filter(
        is_playing=True
    ).order_by('-vote_average', '?')[:PLAYING_MOVIES_COUNT])

    if len(playing_movies) < PLAYING_MOVIES_COUNT:
        additional_playing = Movie.objects.filter(
            is_playing=True
        ).exclude(
            id__in=[movie.id for movie in playing_movies]
        ).order_by('?')[:PLAYING_MOVIES_COUNT-len(playing_movies)]
        playing_movies.extend(additional_playing)

    selected_ids = {movie.id for movie in playing_movies}

    remaining_count = RECOMMENDATIONS_COUNT - len(playing_movies)
    remaining_following_movies = list(following_liked_movies.filter(
        is_playing=False
    ).exclude(
        id__in=selected_ids
    ).order_by('-vote_average', '?')[:remaining_count])

    recommended_movies = playing_movies
    for movie in remaining_following_movies:
        if movie.id not in selected_ids:
            recommended_movies.append(movie)
            selected_ids.add(movie.id)

    if len(recommended_movies) < RECOMMENDATIONS_COUNT:
        additional_movies = Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=selected_ids
        ).order_by('?')[:RECOMMENDATIONS_COUNT-len(recommended_movies)]
        recommended_movies.extend(additional_movies)

    recommended_movies = recommended_movies[:RECOMMENDATIONS_COUNT]

    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)


"""박스오피스 영화를 조회"""
@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_box_office(request):
    box_office_movies = Movie.objects.filter(
        id__range=(9999990, 9999999)
    ).order_by('-id')
    
    serializer = MovieSerializer(box_office_movies, many=True)
    return Response(serializer.data)

"""사용자가 리뷰한 영화의 배우가 출연한 영화를 추천"""
@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_reviewed_actors(request):
    if not request.user.is_authenticated:
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[14:21])
        serializer = MovieSerializer(top_movies[14:21], many=True)
        return Response(serializer.data)
    
    user_reviews = Review.objects.filter(user=request.user).select_related('movie')
    reviewed_movie_ids = set(review.movie.id for review in user_reviews)
    
    actors_set = set()
    for review in user_reviews:
        movie = review.movie
        if movie.actors:
            for actor in movie.actors[:3]:  
                actors_set.add(actor['name'])
    
 
    if not actors_set:
        playing_movies = list(Movie.objects.filter(
            is_playing=True
        ).exclude(
            id__in=reviewed_movie_ids
        ).order_by('?')[:PLAYING_MOVIES_COUNT])
        
        other_movies = list(Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=reviewed_movie_ids
        ).order_by('?')[:RECOMMENDATIONS_COUNT-PLAYING_MOVIES_COUNT])
        
        recommended_movies = playing_movies + other_movies
        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)
    
    playing_recommended = []
    all_playing_movies = Movie.objects.filter(is_playing=True).exclude(id__in=reviewed_movie_ids)
    
    for movie in all_playing_movies:
        if movie.actors:
            movie_actors = {actor['name'] for actor in movie.actors[:3]}
            if actors_set & movie_actors:  
                playing_recommended.append(movie)
    

    if len(playing_recommended) < PLAYING_MOVIES_COUNT:
        existing_ids = {m.id for m in playing_recommended}
        additional_playing = list(Movie.objects.filter(
            is_playing=True
        ).exclude(
            id__in=reviewed_movie_ids | existing_ids
        ).order_by('?')[:PLAYING_MOVIES_COUNT-len(playing_recommended)])
        playing_recommended.extend(additional_playing)
    
    other_recommended = []
    all_other_movies = Movie.objects.filter(
        is_playing=False
    ).exclude(
        id__in=reviewed_movie_ids
    )
    
    for movie in all_other_movies:
        if movie.actors:
            movie_actors = {actor['name'] for actor in movie.actors[:3]}
            if actors_set & movie_actors:  
                other_recommended.append(movie)
    

    playing_recommended = playing_recommended[:PLAYING_MOVIES_COUNT]
    
    other_count = RECOMMENDATIONS_COUNT - PLAYING_MOVIES_COUNT
    if len(other_recommended) > other_count:
        other_recommended = random.sample(other_recommended, other_count)
    elif len(other_recommended) < other_count:
        existing_ids = {m.id for m in other_recommended} | {m.id for m in playing_recommended}
        additional_movies = list(Movie.objects.filter(
            is_playing=False
        ).exclude(
            id__in=reviewed_movie_ids | existing_ids
        ).order_by('?')[:other_count-len(other_recommended)])
        other_recommended.extend(additional_movies)
    
    recommended_movies = playing_recommended + other_recommended
    
    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)


"""사용자가 관심을 보인 개봉 연도에 기반한 영화 추천"""
@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_with_release_date(request):
    if not request.user.is_authenticated:
        top_movies = list(Movie.objects.order_by('-vote_average')[:28])
        random.shuffle(top_movies[21:28])
        serializer = MovieSerializer(top_movies[21:28], many=True)
        return Response(serializer.data)

    liked_movies = request.user.like_movies.all()
    reviewed_movies = Review.objects.filter(user=request.user).select_related('movie')
    
    watched_movie_ids = set(movie.id for movie in liked_movies) | \
                       set(review.movie.id for review in reviewed_movies)
    
    recommended_movies = []
    
    if not liked_movies.exists() and not reviewed_movies.exists():
        current_year = datetime.now().year
        
        for i in range(5):
            period_start = current_year - (i * 10) - 10
            period_end = current_year - (i * 10)
            
            period_movies = Movie.objects.filter(
                release_date__year__range=(period_start, period_end)
            ).order_by('?')[:5]
            
            recommended_movies.extend(period_movies)
    else:
        year_preferences = {}
        
        for movie in liked_movies:
            if movie.release_date:
                year = str(movie.release_date.year)
                year_preferences[year] = year_preferences.get(year, 0) + 1
        
        for review in reviewed_movies:
            if review.movie.release_date:
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
    
    if len(recommended_movies) < RECOMMENDATIONS_COUNT:
        existing_ids = set(movie.id for movie in recommended_movies)
        additional_count = RECOMMENDATIONS_COUNT - len(recommended_movies)
        
        additional_movies = Movie.objects.exclude(
            id__in=existing_ids | watched_movie_ids
        ).order_by('?')[:additional_count]
        
        if len(additional_movies) + len(recommended_movies) < RECOMMENDATIONS_COUNT:
            more_movies = Movie.objects.exclude(
                id__in=existing_ids
            ).order_by('?')[:RECOMMENDATIONS_COUNT-len(recommended_movies)-len(additional_movies)]
            additional_movies = list(additional_movies) + list(more_movies)
        
        recommended_movies.extend(additional_movies)
    
    recommended_movies = recommended_movies[:RECOMMENDATIONS_COUNT]
    
    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)

# 극장 관련 엔드포인트


"""특정 영화를 상영 중인 극장 목록 조회"""
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
            {"error": f"상영관 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
"""모든 극장 목록 조회 체인과 지역으로 필터링"""
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

"""영화 정보와 해당 영화를 상영 중인 극장 정보 함께 반환"""
@api_view(['GET'])
def movie_detail_with_theaters(request, movie_id):
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        theaters = Theater.objects.filter(movie_id=movie_id)
        
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

# 검색 및 상영 중 영화화
"""현재 상영 중인 영화 목록을 반환"""
@api_view(['GET'])
@permission_classes([AllowAny])
def playing_movies(request):
    box_office_movies = Movie.objects.filter(
        is_playing=True
    ).order_by('-id')[:BOX_OFFICE_TOP]
    
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

"""제목이나 배우 이름으로 영화를 검색"""
@api_view(['GET'])
@permission_classes([AllowAny])
def search_movies(request):
    try:
        query = request.GET.get('query', '').strip()
        
        if not query:
            return Response([])

        # 검색어 정규화 (공백 제거, 소문자 변환)
        query_normalized = query.lower().replace(" ", "")
        
        movies = Movie.objects.all()
        
        # 제목으로 검색
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
        
        all_results = list(title_results | actor_results)
        
        serializer = MovieSerializer(all_results, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {"error": f"검색 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

"""장르 및 배우로 영화 필터링"""
@api_view(['GET'])
@permission_classes([AllowAny])
def filter_movies(request):
    try:
        genre_ids = request.GET.get('genre_ids')
        actors = request.GET.get('actors')
        
        movies = Movie.objects.all()
        
        # 장르 ID로 필터링
        if genre_ids:
            genre_id_list = [int(id) for id in genre_ids.split(',')]
            for genre_id in genre_id_list:
                movies = movies.filter(genre_ids__id=genre_id)
        
        # 배우로 필터링
        if actors:
            actor_list = actors.split(',')
            filtered_movies = []
            
            for movie in movies:
                if movie.actors:
                    movie_actor_names = [actor['name'].lower().strip() for actor in movie.actors]
                    if all(actor.lower().strip() in movie_actor_names for actor in actor_list):
                        filtered_movies.append(movie)
            
            movies = filtered_movies
                
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)
            
    except Exception as e:
        return Response(
            {"error": f"필터링 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )