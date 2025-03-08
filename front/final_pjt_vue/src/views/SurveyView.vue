<template>
  <div class="survey-container">
    <h2>영화 취향 설문조사</h2>
    <form @submit.prevent="submitSurvey">
      <div class="form-group">
        <label>선호하는 장르 (여러 개 선택 가능)</label>
        <div class="genre-buttons">
          <button
            v-for="genre in genres"
            :key="genre"
            type="button"
            :class="['genre-button', { active: survey.preferred_genres.includes(genre) }]"
            @click="toggleGenre(genre)"
          >
            {{ genre }}
          </button>
        </div>
      </div>

      <div class="form-group">
        <label for="viewing_reason">영화를 보는 주된 이유</label>
        <select v-model="survey.viewing_reason">
          <option value="artistic">스트레스 해소</option>
          <option value="fear">공포/스릴을 느끼기 위해</option>
          <option value="escapism">현실 도피</option>
          <option value="killing_time">킬링타임용</option> 
          <option value="actor_fandom">좋아하는 배우/감독의 작품</option>
          <option value="with_others">좋아하는 사람과 함께 영화 데이트</option>
          <option value="healing">힐링</option>
          <option value="other">기타</option>
        </select>
      </div>

      <div class="form-group">
        <label>주로 누구와 함께 보시나요?</label>
        <div class="choice-buttons">
          <button
            v-for="option in viewingWithOptions"
            :key="option"
            type="button"
            :class="['choice-button', { active: survey.viewing_with === option }]"
            @click="survey.viewing_with = option"
          >
            {{ option }}
          </button>
        </div>
      </div>

      <div class="form-group">
        <label for="favorite_actor">좋아하는 배우</label>
        <input 
          type="text" 
          v-model="survey.favorite_actor"
          placeholder="예: 송강호, Tom Cruise"
          class="input-field"
        >
      </div>

      <div class="form-group">
        <label>중요하게 생각하는 요소</label>
        <div class="choice-buttons">
          <button
            v-for="element in movieElements"
            :key="element"
            type="button"
            :class="['choice-button', { active: survey.movie_elements.includes(element) }]"
            @click="toggleElement(element)"
          >
            {{ element }}
          </button>
        </div>
      </div>

      <div class="form-group">
        <label>좋아하는 영화들 (최대 4개 선택)</label>
        <div class="movie-search">
          <input 
            type="text" 
            :value="searchQuery"
            @input="handleInput"
            placeholder="영화 제목을 검색하세요..."
          >
        </div>
        
        <!-- 선택된 영화들 표시 -->
        <div class="selected-movies" v-if="survey.favorite_movies.length">
          <div v-for="movie in survey.favorite_movies" :key="movie" class="selected-movie">
            <span>{{ movie }}</span>
            <button @click="removeMovie(movie)" class="remove-btn">&times;</button>
          </div>
        </div>

        <!-- 검색 결과가 있을 때 검색 결과 표시 -->
        <div v-if="searchQuery.trim() && searchResults.length" class="movie-grid">
          <div 
            v-for="movie in searchResults" 
            :key="movie.id" 
            class="movie-card"
            :class="{ 'selected': survey.favorite_movies.includes(movie.title) }"
            @click="toggleMovie(movie.title)"
          >
            <div class="movie-poster-wrapper">
              <img 
                :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`" 
                :alt="movie.title"
              >
              <div v-if="survey.favorite_movies.includes(movie.title)" class="check-overlay">
                <span class="check-icon">✓</span>
              </div>
            </div>
            <div class="movie-title">{{ movie.title }}</div>
          </div>
        </div>

        <!-- 검색 결과가 없을 때 기본 영화 목록 표시 -->
        <div v-else class="movie-grid">
          <div 
            v-for="movie in defaultMovies" 
            :key="movie.id" 
            class="movie-card"
            :class="{ 'selected': survey.favorite_movies.includes(movie.title) }"
            @click="toggleMovie(movie.title)"
          >
            <div class="movie-poster-wrapper">
              <img 
                :src="`https://image.tmdb.org/t/p/w200${movie.poster_path}`" 
                :alt="movie.title"
              >
              <div v-if="survey.favorite_movies.includes(movie.title)" class="check-overlay">
                <span class="check-icon">✓</span>
              </div>
            </div>
            <div class="movie-title">{{ movie.title }}</div>
          </div>
        </div>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? '제출 중...' : '제출하기' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, onMounted } from 'vue'
import axios from 'axios'
import { useMovieStore } from '@/stores/movie'
import { useRouter } from 'vue-router'

const router = useRouter()
const store = useMovieStore()
const error = ref('')
const isSubmitting = ref(false)

const survey = ref({
  preferred_genres: [],
  viewing_reason: '',
  viewing_with: '',
  favorite_actor: '',
  movie_elements: [],
  favorite_movies: []
})

const genres = [
  '액션', '코미디', '드라마', '모험', '애니메이션',
  '범죄', '다큐멘터리', '가족', '판타지', '역사',
  '공포', '음악', '미스터리', '로맨스', 'SF',
  'TV 영화', '스릴러', '전쟁', '서부'
]

const toggleGenre = (genre) => {
  if (survey.value.preferred_genres.includes(genre)) {
    survey.value.preferred_genres = survey.value.preferred_genres.filter(g => g !== genre)
  } else {
    survey.value.preferred_genres.push(genre)
  }
}

const validateSurvey = () => {
  if (!survey.value.preferred_genres.length) {
    throw new Error('선호하는 장르를 선택해주세요.')
  }
  if (!survey.value.viewing_reason) {
    throw new Error('영화를 보는 주된 이유를 선택해주세요.')
  }
  if (!survey.value.viewing_with) {
    throw new Error('함께 보는 사람을 선택해주세요.')
  }
  if (!survey.value.movie_elements.length) {
    throw new Error('중요하게 생각하는 요소를 선택해주세요.')
  }
  if (!survey.value.favorite_movies.length) {
    throw new Error('좋아하는 영화를 선택해주세요.')
  }
}

const searchQuery = ref('')
const searchResults = ref([])
const searchTimeout = ref(null)

const defaultMovies = ref([])

// 컴포넌트 생성 시 기본 영화 목록을 가져오는 함수
const fetchDefaultMovies = async () => {
  try {
    const response = await axios.get(`${store.API_URL}/movies/`, {
      headers: { Authorization: `Token ${store.token}` }
    })
    
    // 원하는 영화 ID 목록
    const wantedMovieIds = [575264, 299534, 22, 585, 857, 37165, 118, 597, 8966, 9999999, 496243, 12445, 475557, 955555, 313369, 109445]
    
    // ID에 해당하는 영화만 필터링
    defaultMovies.value = response.data
      .filter(movie => wantedMovieIds.includes(movie.id))
      .map(movie => ({
        id: movie.id,
        title: movie.title,
        poster_path: movie.poster_path
      }))
  } catch (error) {
    console.error('기본 영화 목록 가져오기 실패:', error)
  }
}

// 컴포넌트 생성 시 기본 영화 목록 가져오기
onMounted(() => {
  fetchDefaultMovies()
})

// 입력 핸들러
const handleInput = (event) => {
  searchQuery.value = event.target.value
  searchMovies()
}

// 디바운스된 검색 함수
const searchMovies = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }

  searchTimeout.value = setTimeout(async () => {
    if (!searchQuery.value.trim()) {
      searchResults.value = []
      return
    }

    try {
      const response = await axios.get(`${store.API_URL}/movies/`, {
        headers: { Authorization: `Token ${store.token}` }
      })
      
      const query = searchQuery.value.trim().toLowerCase().replace(/\s+/g, '')
      searchResults.value = response.data
        .filter(movie => movie.title.toLowerCase().replace(/\s+/g, '').includes(query))
        .slice(0, 8)
    } catch (error) {
      console.error('영화 검색 중 오류:', error)
    }
  }, 200)
}

// 컴포넌트 언마운트 시 타이머 정리
onUnmounted(() => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
})

// 영화 선택/해제 토글
const toggleMovie = (movieTitle) => {
  if (survey.value.favorite_movies.includes(movieTitle)) {
    removeMovie(movieTitle)
  } else if (survey.value.favorite_movies.length < 4) {
    survey.value.favorite_movies.push(movieTitle)
  }
}

// 선택된 영화 제거
const removeMovie = (movieTitle) => {
  survey.value.favorite_movies = survey.value.favorite_movies.filter(
    title => title !== movieTitle
  )
}

const submitSurvey = async () => {
  try {
    error.value = ''
    isSubmitting.value = true
    
    validateSurvey()

    const surveyData = {
      preferred_genres: survey.value.preferred_genres,
      viewing_reason: survey.value.viewing_reason,
      viewing_with: survey.value.viewing_with,
      favorite_actor: survey.value.favorite_actor || '',
      movie_elements: survey.value.movie_elements,
      favorite_movies: survey.value.favorite_movies.join(',')
    }

    await store.saveSurvey(surveyData)
    
    router.push({ name: 'RecommendationsView' })
  } catch (err) {
    error.value = err.response?.data?.message || err.message || '설문 제출 중 오류가 발생했습니다.'
    console.error('설문 제출 중 오류:', err)
    console.error('서버 응답:', err.response?.data)
  } finally {
    isSubmitting.value = false
  }
}

const viewingWithOptions = ['혼자', '가족', '친구', '연인']

const movieElements = [
  '연출', '연기', '스토리', '영상미', 
  '음악', '액션', '특수효과', '분위기'
]

const toggleElement = (element) => {
  if (survey.value.movie_elements.includes(element)) {
    survey.value.movie_elements = survey.value.movie_elements.filter(e => e !== element)
  } else {
    survey.value.movie_elements = [element] // 한 개만 선택되도록
  }
}
</script>

<style scoped>
.survey-container {
  max-width: 1000px;
  margin: 4rem auto;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #2c3e50;
  font-size: 2.8rem;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.form-group {
  margin-bottom: 3rem;
  padding: 2.5rem;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

label {
  display: block;
  margin-bottom: 1.2rem;
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
}

.input-field, .movie-search input {
  width: 100%;
  box-sizing: border-box;
  padding: 1.5rem 2rem;
  font-size: 1.4rem;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  background: #f8f9fa;
  color: #2c3e50;
  transition: all 0.3s ease;
}

.input-field:focus, .movie-search input:focus {
  outline: none;
  border-color: #74b9ff;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(116, 185, 255, 0.1);
}

.input-field::placeholder, .movie-search input::placeholder {
  color: #adb5bd;
  font-size: 1.1rem;
}

.genre-buttons, .choice-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 1rem;
}

.genre-button, .choice-button {
  padding: 0.8rem 1.5rem;
  font-size: 1.1rem;
  font-weight: 500;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  background: #fff;
  color: #2c3e50;
  cursor: pointer;
  transition: all 0.3s ease;
}

.genre-button:hover, .choice-button:hover {
  background: #f8f9fa;
  transform: translateY(-2px);
}

.genre-button.active, .choice-button.active {
  background: #74b9ff;
  color: white;
  border-color: #74b9ff;
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.3);
}

button[type="submit"] {
  width: 100%;
  padding: 1.2rem;
  font-size: 1.3rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  border: none;
  border-radius: 15px;
  margin-top: 3rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

button[type="submit"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(116, 185, 255, 0.4);
}

.error-message {
  background: #fff3f3;
  color: #e74c3c;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin: 1rem 0;
  font-size: 1.1rem;
  border-left: 4px solid #e74c3c;
}

/* 영화 선택 관련 스타일 */
.movie-search {
  margin-bottom: 2rem;
}

.movie-search input {
  width: 100%;
  box-sizing: border-box;
  padding: 1.5rem 2rem;
  font-size: 1.4rem;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  background: #f8f9fa;
  color: #2c3e50;
  transition: all 0.3s ease;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.movie-card {
  position: relative;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  background: white;
  aspect-ratio: 2/3;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.movie-card.selected {
  border: 3px solid #74b9ff;
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(116, 185, 255, 0.3);
}

.movie-poster-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.movie-poster-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.check-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(116, 185, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.check-icon {
  font-size: 4rem;
  color: white;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
  animation: scaleIn 0.2s ease;
}

.movie-title {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent);
  color: white;
  font-size: 1.1rem;
  font-weight: 500;
}

.selected-movies {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin: 1.5rem 0;
}

.selected-movie {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 1.2rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px solid #e9ecef;
  color: #2c3e50;
  font-size: 1.1rem;
}

.remove-btn {
  color: #e74c3c;
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  color: #c0392b;
  transform: scale(1.1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

@media (max-width: 768px) {
  .survey-container {
    margin: 2rem 1rem;
    padding: 2rem;
  }

  h2 {
    font-size: 2.2rem;
  }

  .form-group {
    padding: 1.5rem;
  }

  .genre-buttons, .choice-buttons {
    gap: 10px;
  }

  .genre-button, .choice-button {
    padding: 0.7rem 1.2rem;
    font-size: 1rem;
  }

  .input-field, .movie-search input {
    width: 100%;
    margin: 0;
    padding: 1.2rem 1.8rem;
    font-size: 1.2rem;
  }
}

/* select 요소 스타일 */
select {
  width: 100%;
  box-sizing: border-box;
  padding: 1.5rem 2rem;
  font-size: 1.4rem;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  background: #f8f9fa;
  color: #2c3e50;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%232c3e50' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1.5rem center;
  background-size: 1.5rem;
  transition: all 0.3s ease;
}

select:hover {
  border-color: #74b9ff;
  box-shadow: 0 2px 10px rgba(116, 185, 255, 0.1);
}

select:focus {
  outline: none;
  border-color: #74b9ff;
  box-shadow: 0 0 0 4px rgba(116, 185, 255, 0.1);
}

/* select 옵션 스타일링 */
select option {
  padding: 1rem;
  font-size: 1.3rem;
  background: white;
  color: #2c3e50;
}

@media (max-width: 768px) {
  select {
    padding: 1.2rem 1.8rem;
    font-size: 1.2rem;
  }
}
</style>