from django.core.cache import cache
from redis import Redis
import json
from datetime import datetime
from django.conf import settings
from .models import Movie
from .serializers import MovieSerializer
import logging

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True
)


logger = logging.getLogger(__name__)

class TrendingMoviesService:
    
    # 가중치 설정
    ACTIVITY_WEIGHTS = {
        'view': 1,       
        'like': 5,      
        'review': 3,    
        'rating_high': 4,  
        'rating_mid': 2,  
        'rating_low': 1,   
    }
    
    KEYS = {
        'trending_all': 'trending:movies:all',     
        'trending_daily': 'trending:movies:daily',
        'trending_weekly': 'trending:movies:weekly'
    }
    
    @classmethod
    def track_movie_activity(cls, movie_id, activity_type, user_id=None):
        if activity_type not in cls.ACTIVITY_WEIGHTS:
            return False
            
        # 활동 가중치
        weight = cls.ACTIVITY_WEIGHTS[activity_type]
        
        try:
            # 전체 기간
            redis_client.zincrby(cls.KEYS['trending_all'], weight, movie_id)
            
            # 일간
            redis_client.zincrby(cls.KEYS['trending_daily'], weight, movie_id)
            redis_client.expire(cls.KEYS['trending_daily'], 86400)  # 24시간
            
            # 주간
            redis_client.zincrby(cls.KEYS['trending_weekly'], weight, movie_id)
            redis_client.expire(cls.KEYS['trending_weekly'], 604800)  # 7일
            
            # 사용자별 활동 기록
            if user_id:
                user_activity_key = f"user:{user_id}:activities"
                activity_data = json.dumps({
                    'movie_id': movie_id,
                    'activity_type': activity_type,
                    'timestamp': datetime.now().isoformat()
                })
                redis_client.lpush(user_activity_key, activity_data)
                redis_client.ltrim(user_activity_key, 0, 99)
        except Exception as e:
            logger.error(f"Error tracking movie activity for movie {movie_id}, user {user_id}: {str(e)}")
            return False
        
        return True
    
    @classmethod
    def get_trending_movies(cls, timeframe='all', limit=10):

        limit = min(max(int(limit), 1), 50) 

        if timeframe not in ['all', 'daily', 'weekly']:
            timeframe = 'all'
        
        key = cls.KEYS[f'trending_{timeframe}']
        
        # 캐싱된 결과 확인
        cache_key = f"trending_movies:{timeframe}:{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        trending_movie_data = redis_client.zrevrange(key, 0, limit-1, withscores=True)
        
        if not trending_movie_data:
            top_movies = Movie.objects.filter(is_playing=True).order_by('-vote_average')[:limit]
            serializer = MovieSerializer(top_movies, many=True)
            result = serializer.data
            
            # 캐시에 5분 동안 저장
            cache.set(cache_key, result, 60*5) 
            return result
        
        # Redis에서 가져온 영화 ID 리스트
        movie_ids = [int(movie_id) for movie_id, _ in trending_movie_data]
        
        try:
            movies = Movie.objects.filter(id__in=movie_ids).order_by('id')
            
            movie_dict = {movie.id: movie for movie in movies}
            
            trending_movies = []
            for movie_id, score in trending_movie_data:
                movie = movie_dict.get(int(movie_id))
                if movie:
                    serializer = MovieSerializer(movie)
                    movie_data = serializer.data
                    movie_data['trending_score'] = int(score)
                    trending_movies.append(movie_data)
            
            if len(trending_movies) < limit:
                existing_ids = {movie['id'] for movie in trending_movies}
                additional_movies = Movie.objects.filter(is_playing=True).exclude(
                    id__in=existing_ids
                ).order_by('-vote_average')[:limit-len(trending_movies)]
                
                for movie in additional_movies:
                    serializer = MovieSerializer(movie)
                    movie_data = serializer.data
                    movie_data['trending_score'] = 0
                    trending_movies.append(movie_data)
            
            # 캐시에 5분
            cache.set(cache_key, trending_movies, 60*5) 
        except Exception as e:
            logger.error(f"Error fetching trending movies for timeframe {timeframe}: {str(e)}")
            return []

        return trending_movies
    
    @classmethod
    def reset_trending_data(cls, timeframe=None):
        try:
            if timeframe:
                if timeframe in ['all', 'daily', 'weekly']:
                    redis_client.delete(cls.KEYS[f'trending_{timeframe}'])
            else:
                redis_client.delete(*cls.KEYS.values()) 
        except Exception as e:
            logger.error(f"Error resetting trending data: {str(e)}")
            return False
        
        return True
