<template>
  <div class="movie-detail">
    <div class="movie-header" :style="{ backgroundImage: `url(https://image.tmdb.org/t/p/original${movie.backdrop_path})` }">
      <div class="header-content">
        <div class="poster">
          <img :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`" :alt="movie.title">
          <div v-if="movie.adult" class="adult-badge"></div>
          <div v-if="movie.is_playing" class="playing-badge">
            <svg class="camera-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
              <path d="M4 4h10a2 2 0 0 1 2 2v3.382l4-2.667V17.285l-4-2.667V18a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>
            </svg>
            <span class="now-text">NOW</span>
          </div>
        </div>
        <div class="movie-info">
          <h1>{{ movie.title }}</h1>
          <div class="meta">
            <span class="rating">⭐ {{ movie.vote_average.toFixed(1) }}</span>
            <span class="runtime">🕒 {{ movie.runtime }}분</span>
            <span class="release-date">📅 {{ movie.release_date }}</span>
          </div>
          <div class="genres">
            <span v-for="genre in genres" :key="genre.id" class="genre-tag">
              {{ genre.name }}
            </span>
          </div>
          <p class="overview">{{ movie.overview }}</p>
          <div class="movie-actions">
            <button 
              v-if="store.isLogin"
              @click="handleLike"
              class="like-button"
              :class="{ 'liked': store.isLiked(route.params.movieId) }"
              :disabled="isLoading"
            >
              <i class="fas fa-heart"></i>
            </button>
            <button 
              v-if="hasTrailer"
              @click="playTrailerWithAnimation"
              class="trailer-button"
            >
              🎬 예고편 보기
            </button>
            <button 
              v-if="movie.is_playing"
              @click="checkTheaterAvailability"
            >
              🎥 극장 보기
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showTrailer" class="trailer-modal" @click="showTrailer = false">
      <div class="trailer-content" @click.stop>
        <button class="close-button" @click="showTrailer = false">×</button>
        <div class="video-container">
          <iframe
            v-if="embedUrl"
            :src="embedUrl"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    </div>

    <div class="cast-section" v-if="movie.actors && movie.actors.length">
      <div class="section-header">
        <h2>출연진</h2>
        <div class="divider"></div>
      </div>
      <div class="cast-grid">
        <div v-for="actor in movie.actors" :key="actor.id" class="actor-card">
          <div class="card-inner" @click="searchActor(actor.name)">
            <!-- 앞면 -->
            <div class="card-front">
              <img 
                :src="`https://image.tmdb.org/t/p/w185${actor.profile_path}`" 
                :alt="actor.name"
                class="actor-image"
              >
            </div>
            <!-- 뒷면 -->
            <div class="card-back">
              <img 
                :src="`https://image.tmdb.org/t/p/w185${actor.profile_path}`" 
                :alt="actor.name"
                class="actor-image"
              >
              <div class="actor-info">
                <h3 class="actor-name">{{ actor.name }}</h3>
                <p class="character-name">{{ actor.character }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="glasses-animation" ref="glassesAnim">
      <div class="glasses">
        <div class="glasses-frame">
          <div class="lens left-lens"></div>
          <div class="lens right-lens"></div>
          <div class="bridge"></div>
          <div class="temple left"></div>
          <div class="temple right"></div>
        </div>
      </div>
    </div>
    <div class="screen-dimmer" ref="dimmer"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useMovieStore } from '@/stores/movie'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const path = ref('T')

const showTrailer = ref(false)

const props = defineProps({
  movie: {
    type: Object,
    required: true,
    validator(value) {
      return value && (
        Array.isArray(value.genres) || 
        Array.isArray(value.genre_ids)
      )
    }
  }
})

const store = useMovieStore()
const isLiked = ref(false)
const likeCount = ref(0)
const isLoading = ref(false)

const handleLike = async () => {
  try {
    if (!store.isLogin) {
      alert('로그인이 필요한 서비스입니다.')
      router.push('/login')
      return
    }
    isLoading.value = true
    await store.Like(route.params.movieId)
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const navigateTo = (path) => {
  router.push({
    name: 'TheaterMapView',
    params: { movieId: route.params.movieId }
  })
}

const embedUrl = computed(() => {
  if (!props.movie.youtube_url) return null
  
  let videoId = null
  const url = props.movie.youtube_url
  
  // youtube.com/watch?v= 형식
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('watch?v=')[1].split('&')[0]
  }
  // youtu.be/ 식
  else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]
  }
  
  return videoId ? `https://www.youtube.com/embed/${videoId}` : null
})

const hasTrailer = computed(() => {
  return !!embedUrl.value
})

const checkTheaterAvailability = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/movies/${props.movie.id}/theaters/`)
    
    if (response.data && response.data.length > 0) {
      router.push({
        name: 'TheaterMapView',
        params: { movieId: props.movie.id }
      })
    } else {
      alert(`"${props.movie.title}" 이(가) 상영 중인 영화관이 없습니다.`)
      router.push({ name: 'TheaterListView' })
    }
  } catch (error) {
    console.error('상영 시간표 확인 실패:', error)
    router.push({ name: 'TheaterListView' })
  }
}

const genres = computed(() => {
  return props.movie.genre_ids || []
})

const searchActor = async (actorName) => {
  if (!actorName) return
  
  try {
    const headers = store.token 
      ? { Authorization: `Token ${store.token}` }
      : {}
    
    const response = await axios({
      method: 'get',
      url: `${store.API_URL}/movies/search/`,
      params: { query: actorName.trim() },
      headers: headers
    })
    
    store.searchResults = response.data
    
    router.push({
      name: 'SearchResultsView',
      query: { q: actorName.trim() }
    })
  } catch (error) {
    console.error('Search error:', error)
  }
}

const playTrailerWithAnimation = async () => {
  const glassesAnim = document.querySelector('.glasses-animation')
  const glasses = document.querySelector('.glasses')
  const dimmer = document.querySelector('.screen-dimmer')
  
  // 안경 애니메이션 시작
  glassesAnim.style.display = 'block'
  glasses.classList.add('animate')
  
  // 화면 어둡게 (안경이 중간까지 왔을 때)
  setTimeout(() => {
    dimmer.classList.add('dim')
  }, 1200)
  
  // 애니메이션 완료 후 예고편 표시 (2.4초에서 1.4초로 단축)
  setTimeout(() => {
    showTrailer.value = true
    glassesAnim.style.display = 'none'
    glasses.classList.remove('animate')
    setTimeout(() => {
      dimmer.classList.remove('dim')
    }, 500)
  }, 1400)  // 2400ms에서 1400ms로 변경
}

</script>


<style scoped>

.movie-detail {
  min-height: 100vh;
  background: rgb(26, 29, 41);
  margin: 0;
  padding: 0;
  width: 100%;
  position: relative;
  overflow-x: hidden;
}

@keyframes fadeInDetail {
  from {
    opacity: 0;
    transform: scale(1.02) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.movie-header {
  background-size: cover;
  background-position: center;
  position: relative;
  padding: 6rem 3rem;
  margin: 0;
  width: 100%;
  box-sizing: border-box;
  margin-top: -2rem;
  animation: zoomBackground 1.2s ease-out forwards;
  overflow-x: hidden !important;
}

@keyframes zoomBackground {
  from {
    transform: scale(1.1);
    filter: brightness(0.5) blur(10px);
  }
  to {
    transform: scale(1);
    filter: brightness(1) blur(0);
  }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 4rem;
  position: relative;
  color: white;
  z-index: 1;
  padding: 0 1rem;
}

/* 포스터 */
.poster {
  position: relative;
}

.poster img {
  width: 100%;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
  animation: slideInPoster 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  animation-delay: 0.2s;
  opacity: 0;
}

@keyframes slideInPoster {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.now-text {
  opacity: 0.8;
}

.adult-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 40px;
  height: 40px;
  background-color: #d32f2f;
  border-radius: 6px;
  z-index: 2;
  box-shadow: 0 3px 6px rgba(0,0,0,0.3);
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><text x="50%" y="50%" font-family="Arial" font-size="18" font-weight="bold" text-anchor="middle" dy=".35em">19</text></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.playing-badge {
  position: absolute;
  top: 15px;
  left: 15px;
  background-color: #2671BC;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: bold;
  z-index: 2;
  box-shadow: 0 3px 6px rgba(0,0,0,0.3);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.5px;
}

.camera-icon {
  filter: drop-shadow(0 0 1px rgba(255, 255, 255, 0.5));
  color: #ffffff;
}

.now-text {
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 영화 정보 */
.movie-info {
  padding: 1rem 0;
}

.movie-info h1 {
  font-size: 3.2rem;
  font-weight: 700;
  margin-bottom: 1.8rem;
  color: #ffffff;
  letter-spacing: -0.5px;
  line-height: 1.2;
  text-shadow: 
    2px 2px 4px rgba(0, 0, 0, 0.5),
    0 0 10px rgba(0, 0, 0, 0.3),
    0 0 20px rgba(0, 0, 0, 0.2);
  -webkit-text-stroke: 0.5px rgba(0, 0, 0, 0.3);
}

.meta {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2rem;
  font-size: 1.2rem;
  opacity: 0.9;
  animation: slideInRight 0.8s ease-out forwards;
  animation-delay: 0.4s;
  opacity: 0;
}

.meta span {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.6rem 1.2rem;
  border-radius: 12px;
  backdrop-filter: blur(4px);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.meta span:hover {
  background: rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin: 1.5rem 0;
  animation: slideInRight 0.8s ease-out forwards;
  animation-delay: 0.5s;
  opacity: 0;
}

.genre-tag {
  background: linear-gradient(135deg, rgba(0, 116, 210, 0.267), rgba(0, 200, 255, 0.664));
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.7rem 1.4rem;
  border-radius: 25px;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  letter-spacing: 0.5px;
}

.genre-tag:hover {
  background: linear-gradient(135deg, rgba(0, 138, 255, 0.95), rgba(0, 213, 255, 0.95));
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 114, 210, 0.4);
  border-color: rgba(255, 255, 255, 0.3);
}

.genre-tag:before {
  content: '#';
  margin-right: 4px;
  opacity: 0.8;
}

.overview {
  font-size: 1.15rem;
  line-height: 1.8;
  margin: 2rem 0;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.2px;
  text-shadow: 
    1px 1px 2px rgba(0, 0, 0, 0.8),
    0 0 8px rgba(0, 0, 0, 0.3);
}
.movie-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  animation: slideInRight 0.8s ease-out forwards;
  animation-delay: 0.7s;
  opacity: 0;
}

.movie-actions .like-button {
  all: unset !important;
  position: relative !important;
  cursor: pointer !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.movie-actions .like-button i {
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.8);
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
}

/* 호버 시 크기만 변경 */
.movie-actions .like-button:hover {
  transform: scale(1.15);
}

/* 클릭 시 약간 눌리는 효과 */
.movie-actions .like-button:active {
  transform: scale(0.95);
}

/* 좋아요 상태일 때의 스타일 */
.movie-actions .like-button.liked i {
  color: #ff4d6d;
}

/* 하트 파티클 애니메이션 */
.movie-actions .like-button.liked::after {
  content: '♥';
  position: absolute;
  color: #ff4d6d;
  font-size: 1rem;
  pointer-events: none;
  animation: floatingHeart 0.8s ease-out forwards;
}

@keyframes floatingHeart {
  0% {
    opacity: 1;
    transform: translate(-50%, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50px) scale(0.5);
  }
}

/* 여러 개의 하트 파티클 */
.movie-actions .like-button.liked::before {
  content: '♥';
  position: absolute;
  color: #ff4d6d;
  font-size: 0.8rem;
  pointer-events: none;
  animation: floatingHeartRight 0.8s ease-out forwards;
}

@keyframes floatingHeartRight {
  0% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(20px, -40px) scale(0.5);
  }
}

.like-count {
  display: none;
}


.like-button:active {
  transform: scale(0.95);
}

.like-content {
  display: flex;
  align-items: center;
  gap: 8px;
}


.like-button.liked .heart {
  color: white;
}

.like-button .heart {
  color: #ccc;
}

.like-button.liked:hover {
  background: #ff6b81;
  border-color: #ff6b81;
}

.like-button:active {
  transform: scale(0.95);
}

.like-text {
  font-weight: 500;
}

/* 리뷰 섹션 */
.reviews-section {
  background: rgb(13, 17, 23);
  color: white;
  padding: 4rem 2rem;
}

.reviews-section h2 {
  color: white;
  font-size: 2rem;
  text-align: center;
  margin-bottom: 1rem;
}

.review-form {
  background: rgb(26, 29, 41);
  border-radius: 10px;
  padding: 2rem;
  margin-bottom: 3rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.review-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.review-header h3 {
  color: white;
}

.review-count {
  color: #0072d2;
}

.rating-label {
  color: white;
}

.review-editor {
  background: rgb(31, 35, 45);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.review-editor::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.editor-footer {
  background: rgb(31, 35, 45);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.char-count {
  color: rgba(255, 255, 255, 0.6);
}

.submit-btn {
  background: #0072d2;
  color: white;
  font-weight: 500;
  padding: 0.8rem 2rem;
  border-radius: 25px;
  transition: all 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background: #0066bb;
  transform: scale(1.05);
}

.submit-btn:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.3);
}

/* 리뷰 카드 */
.reviews-list {
  display: grid;
  gap: 2rem;
}

.review-card {
  background: rgb(26, 29, 41);
  border-radius: 10px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.review-card h3 {
  color: white;
}

.review-meta {
  color: rgba(255, 255, 255, 0.6);
}

.author {
  color: #0072d2;
}

.review-content {
  color: rgba(255, 255, 255, 0.9);
}

.delete-button {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
}

.delete-button:hover {
  background: rgba(255, 71, 87, 0.3);
  transform: scale(1.05);
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .header-content {
    grid-template-columns: 300px 1fr;
    gap: 3rem;
  }

  .movie-info h1 {
    font-size: 2.8rem;
  }
}

@media (max-width: 768px) {
  .movie-header {
    padding: 4rem 1.5rem;
  }

  .header-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .poster {
    max-width: 300px;
    margin: 0 auto;
  }

  .movie-info h1 {
    font-size: 2.5rem;
    text-shadow: 
      1px 1px 3px rgba(0, 0, 0, 0.7),
      0 0 8px rgba(0, 0, 0, 0.4);
  }

  .overview {
    font-size: 1.1rem;
    text-shadow: 
      1px 1px 2px rgba(0, 0, 0, 0.9),
      0 0 6px rgba(0, 0, 0, 0.4);
  }

  .meta {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .genres {
    justify-content: center;
  }

  .overview {
    text-align: center;
  }

  .like-button {
    display: block;
    margin: 0 auto;
  }

  .form-header {
    flex-direction: column;
  }

  .review-card {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .movie-info h1 {
    font-size: 1.8rem;
  }

  .review-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .review-meta {
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
  }
}

.button-container {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.trailer-button,
.movie-actions button:not(.like-button) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 24px;
  height: 48px;
  border: none;
  border-radius: 24px;
  background: linear-gradient(135deg, 
    rgba(0, 114, 210, 0.9),
    rgba(0, 138, 255, 0.9)
  );
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(4px);
}

.trailer-button:hover,
.movie-actions button:not(.like-button):hover {
  background: linear-gradient(135deg, 
    rgba(0, 138, 255, 1),
    rgba(0, 162, 255, 1)
  );
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 114, 210, 0.4);
}

.trailer-button:active,
.movie-actions button:not(.like-button):active {
  transform: translateY(1px);
  box-shadow: 0 2px 10px rgba(0, 114, 210, 0.3);
}

/* 모바일 대응 */
@media (max-width: 768px) {
  .meta {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .meta span {
    width: 100%;
    justify-content: center;
    max-width: 250px;
  }

  .genre-tag {
    font-size: 0.9rem;
    padding: 0.6rem 1.2rem;
  }

  .trailer-button,
  .movie-actions button:not(.like-button) {
    width: 100%;
    max-width: 250px;
    margin: 0 auto;
  }
}

.trailer-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.trailer-content {
  position: relative;
  width: 90%;
  max-width: 1000px;
  background: black;
  border-radius: 12px;
  overflow: hidden;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  font-size: 32px;
  cursor: pointer;
  z-index: 1;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.video-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 비율 */
  height: 0;
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* 모바일 반응형 추가 */
@media (max-width: 768px) {
  .button-container {
    flex-direction: column;
    align-items: center;
  }

  .trailer-button {
    width: 100%;
    max-width: 200px;
    justify-content: center;
  }
}

.cast-section {
  background: rgb(26, 29, 41);
  padding: 1rem 2rem 3.5rem 2rem;
  color: white;
  text-align: center;
  margin: 0 auto;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.cast-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.actor-card {
  position: relative;
  width: 100%;
  height: 300px;
  perspective: 1500px;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  cursor: pointer;
}

.actor-card:hover .card-inner {
  transform: rotateY(180deg);
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  overflow: hidden;
}

.card-front {
  background-color: rgb(26, 29, 41);
}

.card-back {
  background-color: rgb(26, 29, 41);
  transform: rotateY(180deg);
}

.actor-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 카드 뒷면의 오버레이 수정 */
.card-back::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(26, 29, 41, 0.9);
  z-index: 1;
}

.actor-info {
  position: absolute;
  top: 20%;
  left: -11%;
  transform: translate(-50%, -50%);
  width: 100%;
  padding: 1.5rem;
  text-align: center;
  z-index: 2;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards 0.3s;
}

.actor-name {
  font-size: 1.4rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.character-name {
  font-size: 1.1rem;
  color: #0072d2;
  font-weight: 500;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -40%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .actor-card {
    height: 250px;
  }

  .actor-name {
    font-size: 1.2rem;
  }

  .character-name {
    font-size: 1rem;
  }
}

/* 호버 효과 추가 */
.card-front::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(26, 29, 41, 0.8) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.actor-card:hover .card-front::after {
  opacity: 1;
}

/* 애니메이션 추가 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.actor-info {
  animation: fadeIn 0.5s ease forwards;
  animation-delay: 0.4s;
  opacity: 0;
}

/* 별점 스타일 수정 */
.star {
  color: rgba(255, 255, 255, 0.2);
}

.star.active,
.star.hover {
  color: #0072d2;
}

.rating-text {
  color: rgba(255, 255, 255, 0.8);
}

.like-button {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer !important;
  color: rgba(255, 255, 255, 0.5);
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.like-button i {
  transition: all 0.3s ease;
  cursor: pointer;
  transform-origin: center;
}

/* 호버 효과 수정 */
.like-button:hover:not(:disabled) i {
  transform: scale(1.2);
}

.like-button:active:not(:disabled) i {
  transform: scale(0.95);
}

.like-button:disabled {
  opacity: 0.5;
  cursor: not-allowed !important;
}

.like-button:disabled i {
  animation: none;
  transform: none;
  cursor: not-allowed;
}

.like-button.liked {
  color: #ff4d4d;
}

.like-button.liked i {
  animation: heartBeat 1.2s ease-in-out;
}

@keyframes heartBeat {
  0% {
    transform: scale(1);
  }
  14% {
    transform: scale(1.3);
  }
  28% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.3);
  }
  70% {
    transform: scale(1);
  }
}

.like-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.like-button:disabled i {
  animation: none;
  transform: none;
}

/* 호버 효과 추가 */
.like-button:hover:not(:disabled) {
  transform: scale(1.2);
}

.like-button:active:not(:disabled) {
  transform: scale(0.95);
}

/* 모바일 반응 대응 */
@media (max-width: 768px) {
  .genres {
    justify-content: center;
  }
  
  .genre-tag {
    font-size: 0.9rem;
    padding: 0.6rem 1.2rem;
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 3D 안경 컨테이너 */
.glasses-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 999;
  display: none;
  overflow: hidden;
  transform: translateZ(0);  /* 하드웨어 가속 활성화 */
}

.glasses {
  position: fixed;
  width: 460px;
  height: 180px;
  bottom: -100px;
  left: 50%;
  transform: translateX(-50%) scale(0.5);
  opacity: 0;
}

.glasses.animate {
  animation: flyGlasses 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.glasses-frame {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 12px solid #1a1a1a;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  padding: 0 15px;
  background: #1a1a1a;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.lens {
  width: 200px;
  height: 140px;
  background: linear-gradient(135deg,
    rgba(0, 162, 255, 0.2) 0%,
    rgba(255, 0, 0, 0.2) 100%
  );
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 8px;
}

.lens::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0.3) 0%,
    transparent 40%,
    rgba(0, 89, 255, 0.2) 100%
  );
  backdrop-filter: blur(4px);
}

.bridge {
  width: 30px;
  height: 12px;
  background: #1a1a1a;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 2px;
}

.temple {
  display: none;
}

@keyframes flyGlasses {
  0% {
    transform: translate(-50%, 200px) scale(0.5) rotate(15deg);
    opacity: 0;
  }
  30% {
    transform: translate(-50%, -30vh) scale(1.2) rotate(5deg);
    opacity: 1;
  }
  60% {
    transform: translate(-50%, -45vh) scale(2.5) rotate(0deg);
    opacity: 1;
  }
  85% {
    transform: translate(-50%, -50vh) scale(6);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50vh) scale(12);
    opacity: 0;
  }
}

/* 화면 어두워지는 효과 */
.screen-dimmer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: black;
  opacity: 0;
  z-index: 998;
  pointer-events: none;
  transition: opacity 0.8s ease;
}

.screen-dimmer.dim {
  opacity: 1;
}

.left-lens {
  background: rgba(255, 0, 0, 0.4) !important;
}

.right-lens {
  background: rgba(0, 162, 255, 0.4) !important;
}

/* body 전체에 overflow 방지 */
body.modal-open {
  overflow: hidden;
}

body {
  overflow-x: hidden;
  width: 100%;
  position: relative;
}

body.modal-open {
  overflow: hidden;
  padding-right: 0 !important;
}

/* 스크롤바 관련 스타일 추가 */
html {
  scrollbar-width: thin;  /* Firefox */
  scrollbar-gutter: stable;  /* 스크롤바 공간 예약 */
}

body {
  margin-right: calc(100vw - 100%);  /* 스크롤바 너비만큼 여백 추가 */
  overflow-y: scroll;  /* 항상 스크롤바 표시 */
  overflow-x: hidden;
  width: 100%;
  position: relative;
}

/* 모달 열릴 때 body 스타일 */
body.modal-open {
  overflow: hidden !important;
  /* margin-right 유지 */
  margin-right: calc(100vw - 100%) !important;
  padding-right: 0 !important;
}

</style>