from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from movies.models import Review, Movie, Genre
from .models import User, Survey
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .serializers import SurveyResponseSerializer
from django.conf import settings
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_page(request, username):
    person = get_object_or_404(User, username=username)
    
    is_followed = person.followers.filter(pk=request.user.pk).exists()
    
    reviews = person.movie_reviews.select_related('movie').values(
        'id', 'content', 'rating', 'created_at', 'updated_at', 'movie__title', 'movie__id'
    )
    
    followings = person.followings.values('username', 'id')
    followers = person.followers.values('username', 'id')
    
    liked_movies = person.like_movies.all()
    unique_liked_movies = {movie.id: movie for movie in liked_movies}.values()

    data = {
        'person': {
            'username': person.username,
            'id': person.id,
            'liked_movies_count': person.like_movies.count(),
        },
        'is_followed': is_followed,
        'reviews': list(reviews),
        'followings': list(followings),
        'followers': list(followers),
        'followings_count': person.followings.count(),
        'followers_count': person.followers.count(),
        'liked_movies': [
            {
                'id': movie.id,
                'title': movie.title,
                'poster_path': movie.poster_path,
                'vote_average': movie.vote_average,
                'overview': movie.overview,
                'release_date': movie.release_date,
                'original_language': movie.original_language,
                'adult' : movie.adult,
                'runtime' : movie.runtime,
                'genres': [genre.name for genre in movie.genre_ids.all()],
                'backdrop_path' : movie.backdrop_path,
                'is_playing' : movie.is_playing,
                'youtube_url' : movie.youtube_url,
            }
            for movie in unique_liked_movies
        ],
    }
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow(request, username):
    User = get_user_model()
    you = get_object_or_404(User, username=username)
    me = request.user

    if me != you:
        if you.followers.filter(pk=me.pk).exists():
            you.followers.remove(me)
            is_followed = False
        else:
            you.followers.add(me)
            is_followed = True
        
        context = {
            'is_followed': is_followed,
            'followings_count': you.followings.count(),
            'followers_count': you.followers.count(),
        }
        return Response(context)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_image(request, username):
    if request.user.username != username:
        return Response(status=403)
    
    user = request.user
    if 'profile_image' in request.FILES:
        user.profile_image = request.FILES['profile_image']
        user.save()
        return Response({'message': 'Profile image updated'})
    return Response({'error': 'No image provided'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_survey(request):
    try:
        survey, created = Survey.objects.get_or_create(user=request.user)
        serializer = SurveyResponseSerializer(
            survey, 
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

# 영화 보는 이유와 동반자에 대한 매핑 추가
reason_mapping = {
    'artistic': '스트레스 해소',
    'fear': '공포/스릴을 느끼기 위해',
    'escapism': '현실 도피',
    'killing_time': '킬링타임용',
    'actor_fandom': '좋아하는 배우/감독의 작품',
    'with_others': '좋아하는 사람과 함께 영화 데이트',
    'healing': '힐링',
    'other': '기타'
}

companion_mapping = {
    '혼자': '혼자',
    '가족': '가족',
    '친구': '친구',
    '연인': '연인'
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    try:
        survey = Survey.objects.get(user=request.user)
        
        # 데이터베이스에서 영화 목록 가져오기
        all_movies = Movie.objects.all()
        
        # 사용자가 선호하는 장르의 영화들 필터링
        preferred_genres = survey.preferred_genres.split(',')
        genre_movies = Movie.objects.filter(genre_ids__name__in=preferred_genres).distinct()

        # 영화 정보를 포함한 문자열 생성
        movie_info_list = []
        for movie in genre_movies[:20]:  # 상위 20개 영화만 사용
            genres = ', '.join([genre.name for genre in movie.genre_ids.all()])
            movie_info = f"{movie.title} (장르: {genres})"
            movie_info_list.append(movie_info)

        # GPT 프롬프트 수정
        prompt = f"""
        다음은 사용자의 영화 취향 데이터입니다:
        
        - 선호하는 장르: {survey.preferred_genres}
        - 영화를 보는 주된 이유: {reason_mapping.get(survey.viewing_reason, survey.viewing_reason)}
        - 함께 보는 사람: {companion_mapping.get(survey.viewing_with, survey.viewing_with)}
        - 좋아하는 배우: {survey.favorite_actor}
        - 중요하게 생각하는 요소: {survey.movie_elements}
        - 좋아하는 영화들: {survey.favorite_movies}
        
        다음은 추천 가능한 영화 목록입니다:
        {' | '.join(movie_info_list)}
        
        위 영화들 중에서만 사용자의 취향을 분석하여, 구체적인 이유와 함께 7개의 영화를 추천해주세요.
        각 영화에 대해 제목과 함께 이 사용자가 좋아할 만한 이유를 자세히 설명해주세요.
        
        다음 형식으로 응답해주세요:
        
        [사용자 취향 분석]
        사용자의 전반적인 취향에 대한 분석
        
        [추천 영화]
        1. [영화 제목]
        - 추천 이유: (1-2줄 설명)
        
        (이하 동일한 형식으로 7개)
        """
        
        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 영화 전문가입니다. 사용자의 취향을 분석하여 최적의 영화를 추천해주세요. 한국어로 응답해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        recommendations = response.choices[0].message.content
        
        # 응답을 더 예쁘게 포맷팅
        formatted_recommendations = {
            'analysis': '',
            'movies': []
        }
        
        # GPT 응답 파싱
        sections = recommendations.split('[추천 영화]')
        if len(sections) == 2:
            analysis = sections[0].replace('[사용자 취향 분석]', '').strip()
            formatted_recommendations['analysis'] = analysis
            
            movies_section = sections[1].strip().split('\n\n')
            for movie in movies_section:
                if movie.strip():
                    lines = movie.strip().split('\n')
                    if len(lines) >= 2:
                        title = lines[0].replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '').replace('6. ', '').replace('7. ', '').strip()
                        reason = lines[1].replace('- 추천 이유: ', '').strip()
                        formatted_recommendations['movies'].append({
                            'title': title,
                            'reason': reason
                        })

        return Response(formatted_recommendations)

    except Survey.DoesNotExist:
        return Response(
            {'error': '설문 데이터가 없습니다. 먼저 설문을 완료해주세요.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'추천 생성 중 오류가 발생했습니다: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )