<template>
  <div class="recommendations-container">
    <h2 class="main-title">🎬 맞춤 영화 추천</h2>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>당신의 취향을 분석하여 영화를 추천하고 있습니다...</p>
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else class="recommendations">
      <div class="analysis-section">
        <h3 class="section-title">✨ 취향 분석</h3>
        <div class="analysis-points">
          <p v-for="(point, index) in analysisPoints" 
             :key="index" 
             class="analysis-point">
            {{ point }}
          </p>
        </div>
      </div>

      <div class="movies-section">
        <h3 class="section-title">🎯 추천 영화</h3>
        <div class="movie-grid">
          <div v-for="(movie, index) in recommendations.movies" 
               :key="index" 
               class="movie-item">
            <div class="movie-card">
              <div class="movie-number">{{ index + 1 }}</div>
              <img :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`" 
                   :alt="movie.title" 
                   class="movie-poster">
              <div class="movie-content">
                <h4 class="movie-title">{{ movie.title }}</h4>
                <div class="movie-reason">
                  <div class="reason-bubble">
                    <div class="bubble-tail"></div>
                    <p class="reason-text">{{ movie.reason }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="movie-item">
            <div class="movie-card home-link-card" @click="goToHome">
              <div class="home-icon">🏠</div>
              <p class="home-text">
                홈 화면에서 더 많은<br>맞춤 추천 영화를<br>만나보세요!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMovieStore } from '@/stores/movie'
import MovieCard from '@/components/MovieCard.vue'
import { useRouter } from 'vue-router'

const store = useMovieStore()
const recommendations = ref({
  analysis: '',
  movies: []
})
const loading = ref(false)
const error = ref('')
const router = useRouter()

// 분석 텍스트를 bullet points로 분리
const analysisPoints = computed(() => {
  if (!recommendations.value.analysis) return []
  return recommendations.value.analysis
    .split('-')
    .filter(point => point.trim())
    .map(point => point.trim())
})

const getRecommendations = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${store.API_URL}/users/recommendations/`, {
      headers: {
        Authorization: `Token ${store.token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('추천을 가져오는데 실패했습니다.')
    }
    
    const data = await response.json()
    
    if (data.movies && Array.isArray(data.movies)) {
      // 먼저 전체 영화 목록을 가져옵니다
      const allMoviesResponse = await fetch(`${store.API_URL}/movies/`, {
        headers: {
          Authorization: `Token ${store.token}`
        }
      })
      
      if (!allMoviesResponse.ok) {
        throw new Error('영화 목록을 가져오는데 실패했습니다.')
      }
      
      const allMovies = await allMoviesResponse.json()
      
      // 제목 정규화 함수
      const normalizeTitle = (title) => {
        return title
          .toLowerCase()
          .replace(/[:\-–—]/g, '') // 특수문자 제거
          .replace(/\(.*?\)/g, '') // 괄호와 그 안의 내용 제거
          .replace(/\s+/g, '') // 공백 제거
          .trim()
      }

      // 추천된 영화들의 상세 정보를 찾습니다
      const moviesWithDetails = data.movies.map(recommendedMovie => {
        console.log('Looking for movie:', recommendedMovie.title)
        
        const movieDetails = allMovies.find(m => {
          const normalizedDBTitle = normalizeTitle(m.title)
          const normalizedRecommendedTitle = normalizeTitle(recommendedMovie.title)
          
          return normalizedDBTitle.includes(normalizedRecommendedTitle) || 
                 normalizedRecommendedTitle.includes(normalizedDBTitle)
        })
        
        if (movieDetails) {
          console.log('Found match:', movieDetails.title)
          return {
            ...movieDetails,
            reason: recommendedMovie.reason
          }
        }
        
        console.warn('Movie not found:', recommendedMovie.title)
        return null
      }).filter(movie => movie !== null)
      
      recommendations.value = {
        ...data,
        movies: moviesWithDetails
      }
      
      // store에 저장
      store.setRecommendedMovies(moviesWithDetails)
      console.log('Recommendations stored in store:', store.aiRecommendations)
    }

  } catch (err) {
    error.value = err.message
    console.error('Error fetching recommendations:', err)
  } finally {
    loading.value = false
  }
}

const goToHome = () => {
  router.push({ name: 'HomeView' })
}

onMounted(() => {
  getRecommendations()
})
</script>

<style scoped>
.recommendations-container {
  max-width: 1200px;
  margin: 4rem auto;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.main-title {
  color: #2c3e50;
  font-size: 2.8rem;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.section-title {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 2rem;
  letter-spacing: -0.5px;
}

.loading {
  text-align: center;
  padding: 5rem;
  background: white;
  border-radius: 20px;
  color: #2c3e50;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #74b9ff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 2rem;
}

.analysis-section {
  background: #fff;
  padding: 2.5rem;
  border-radius: 20px;
  margin-bottom: 3rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
}

.analysis-points {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.analysis-point {
  background: #f8f9fa;
  padding: 1.5rem 2rem;
  border-radius: 15px;
  font-size: 1.15rem;
  line-height: 1.7;
  color: #2c3e50;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.analysis-point:hover {
  transform: translateX(5px);
  background: #fff;
  border-color: #74b9ff;
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.2);
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3rem;
  padding: 2rem;
  margin: 0 auto;
  max-width: 1400px;
}

.movie-item {
  display: flex;
  justify-content: center;
}

.movie-card {
  position: relative;
  border-radius: 20px;
  width: 100%;
  max-width: 380px;
  height: 600px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.movie-poster {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
  transition: transform 0.3s ease;
}

.movie-content {
  position: relative;
  z-index: 2;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(0, 0, 0, 0.8) 30%,
    rgba(0, 0, 0, 0.4) 60%,
    rgba(0, 0, 0, 0.2) 75%,
    rgba(0, 0, 0, 0) 100%
  );
  height: 100%;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: 45%;
  padding-bottom: 2rem;
}

.movie-title {
  color: white;
  font-size: 1.4rem;
  margin: 0;
  padding-bottom: 0.8rem;
  font-weight: 800;
  text-align: center;
  line-height: 1.3;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.movie-number {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  width: 45px;
  height: 45px;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(5px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.3rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  z-index: 3;
  transition: all 0.3s ease;
}

.reason-bubble {
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1.2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.reason-text {
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.5;
  font-size: 0.95rem;
  text-align: center;
  margin: 0;
  font-weight: 400;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

/* 홈 링크 카드 스타일 수정 */
.home-link-card {
  height: 380px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.home-icon {
  font-size: 3rem;
  color: #3498db;
  margin-bottom: 0.5rem;
  animation: bounce 2s infinite;
}

.home-text {
  color: #2c3e50;
  font-size: 1.2rem;
  text-align: center;
  line-height: 1.6;
  margin: 0;
}

.home-link-card:hover {
  background: #fff;
  border-color: #3498db;
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(52, 152, 219, 0.15);
}

.home-link-card:hover .home-icon {
  transform: scale(1.1);
}

/* movie-content 내부의 reason-bubble 위치 조정 */
.movie-reason {
  position: relative;
  margin-top: 0.5rem;
  padding: 0 0.5rem;
}

/* 호버 효과 */
.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
}

.movie-card:hover .movie-poster {
  transform: scale(1.05);
}

.home-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@media (max-width: 1200px) {
  .movie-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 3rem;
  }
}

@media (max-width: 768px) {
  .movie-grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
  
  .movie-card {
    max-width: 400px;
  }
}

/* 호버 효과 수정 */
.movie-card:hover .movie-content {
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.98) 0%,
    rgba(0, 0, 0, 0.95) 35%,
    rgba(0, 0, 0, 0.7) 50%,
    rgba(0, 0, 0, 0) 70%
  );
}

.movie-card:hover .reason-bubble {
  background: rgba(255, 255, 255, 0.98);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.movie-card:hover .reason-bubble::before {
  border-bottom-color: rgba(255, 255, 255, 0.98);
}

.movie-card:hover .movie-number {
  background: rgba(0, 0, 0, 0.85);
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.05);
}

.movie-card:hover .reason-bubble {
  background: rgba(0, 0, 0, 0.85);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
}
</style> 