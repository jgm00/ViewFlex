<template>
  <div class="home-container">
    <div v-if="isLoading" class="loading">
      Loading...
    </div>
    <div v-else>
      <div v-if="boxOfficeMovies.length" class="recommended-section">
        <h2 class="section-title">박스오피스 TOP 10</h2>
        <div class="movie-carousel">
          <button class="nav-button prev" @click="scrollCarousel('boxOffice', -1)">❮</button>
          <div class="movie-slider" ref="boxOfficeSliderRef">
            <template v-for="(set, setIndex) in 100" :key="setIndex">
              <div v-for="(movie, index) in boxOfficeMovies" 
                   :key="`${setIndex}-${movie.id}`" 
                   :class="['movie-rank-wrapper', {'rank-ten': index === 9}]"
              >
                <div class="rank-number">{{ index + 1 }}</div>
                <div class="movie-card-container">
                  <SimpleMovieCard 
                    :movie="movie"
                  />
                </div>
              </div>
            </template>
          </div>
          <button class="nav-button next" @click="scrollCarousel('boxOffice', 1)">❯</button>
        </div>
      </div>

      <div v-if="genreMovies.length" class="recommended-section">
        <h2 v-if="userStore.isLogin" class="section-title">당신의 취향을 저격할 영화들</h2>
        <div class="movie-carousel">
          <button class="nav-button prev" @click="scrollCarousel('genre', -1)">❮</button>
          <div class="movie-slider" ref="genreSliderRef">
            <SimpleMovieCard 
              v-for="movie in genreMovies" 
              :key="movie.id" 
              :movie="movie"
            />
          </div>
          <button class="nav-button next" @click="scrollCarousel('genre', 1)">❯</button>
        </div>
      </div>

      <div v-if="followingMovies.length" class="recommended-section">
        <h2 v-if="userStore.isLogin" class="section-title">친구가 좋아하는 영화</h2>
        <div class="movie-carousel">
          <button class="nav-button prev" @click="scrollCarousel('following', -1)">❮</button>
          <div class="movie-slider" ref="followingSliderRef">
            <SimpleMovieCard 
              v-for="movie in followingMovies" 
              :key="movie.id" 
              :movie="movie"
            />
          </div>
          <button class="nav-button next" @click="scrollCarousel('following', 1)">❯</button>
        </div>
      </div>

      <div v-if="actorMovies.length" class="recommended-section">
        <h2 v-if="userStore.isLogin" class="section-title">내가 본 영화에 출연한 배우들의 다른 작품</h2>
        <div class="movie-carousel">
          <button class="nav-button prev" @click="scrollCarousel('actor', -1)">❮</button>
          <div class="movie-slider" ref="actorSliderRef">
            <SimpleMovieCard 
              v-for="movie in actorMovies" 
              :key="movie.id" 
              :movie="movie"
            />
          </div>
          <button class="nav-button next" @click="scrollCarousel('actor', 1)">❯</button>
        </div>
      </div>

      <div v-if="releaseDateMovies.length" class="recommended-section">
        <h2 v-if="userStore.isLogin" class="section-title">당신이 사랑했던 그 시절의 영화들</h2>
        <!-- <h2 class="section-title">당신이 사랑했던 그 시절의 영화들</h2> -->
        <div class="movie-carousel">
          <button class="nav-button prev" @click="scrollCarousel('releaseDate', -1)">❮</button>
          <div class="movie-slider" ref="releaseDateSliderRef">
            <SimpleMovieCard 
              v-for="movie in releaseDateMovies" 
              :key="movie.id" 
              :movie="movie"
            />
          </div>
          <button class="nav-button next" @click="scrollCarousel('releaseDate', 1)">❯</button>
        </div>
      </div>

      <div v-if="userStore.isLogin && userStore.aiRecommendations?.length > 0" 
           class="recommended-section">
        <h2 class="section-title">AI가 발견한 당신의 숨은 취향 영화</h2>
        <div class="movie-carousel">
          <button class="nav-button prev" @click="scrollCarousel('ai', -1)">❮</button>
          <div class="movie-slider" ref="aiSliderRef">
            <SimpleMovieCard 
              v-for="movie in userStore.aiRecommendations" 
              :key="movie.id" 
              :movie="movie"
            />
          </div>
          <button class="nav-button next" @click="scrollCarousel('ai', 1)">❯</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import axios from 'axios'
import SimpleMovieCard from '@/components/SimpleMovieCard.vue'
import { useMovieStore } from '@/stores/movie'
import { useRouter } from 'vue-router'

const userStore = useMovieStore()
const genreMovies = ref([])
const followingMovies = ref([])
const topGenres = ref([])
const isLoading = ref(true)
const genreSliderRef = ref(null)
const followingSliderRef = ref(null)
const boxOfficeMovies = ref([])
const boxOfficeSliderRef = ref(null)
const router = useRouter()
const actorMovies = ref([])
const actorSliderRef = ref(null)
const releaseDateMovies = ref([])
const releaseDateSliderRef = ref(null)
const aiSliderRef = ref(null)

// 영화 배열을 랜덤하게 섞는 함수
const shuffleArray = (array) => {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

const scrollCarousel = (type, direction) => {
  const sliderRefs = {
    boxOffice: boxOfficeSliderRef,
    genre: genreSliderRef,
    following: followingSliderRef,
    actor: actorSliderRef,
    releaseDate: releaseDateSliderRef,
    ai: aiSliderRef
  }
  
  const sliderRef = sliderRefs[type].value
  if (sliderRef) {
    if (type === 'boxOffice') {
      const cardWidth = 400 // 카드 너비 + gap
      const setWidth = cardWidth * boxOfficeMovies.value.length // 한 세트의 너비
      const totalWidth = setWidth * 100 // 100세트의 전체 너비
      const currentScroll = sliderRef.scrollLeft

      // 일반적인 스크롤
      sliderRef.scrollBy({ 
        left: cardWidth * 5 * direction, 
        behavior: 'smooth' 
      })

      // 스크롤 애니메이션이 끝난 후 위치 체크
      setTimeout(() => {
        const newScroll = sliderRef.scrollLeft
        if (newScroll >= totalWidth - (cardWidth * 5)) {
          // 마지막 세트에서 다음으로 넘어가면 처음으로
          sliderRef.scrollTo({
            left: 0,
            behavior: 'auto' // 순간 이동
          })
        } else if (newScroll <= 0 && direction < 0) {
          // 처음에서 이전으로 가면 마지막으로
          sliderRef.scrollTo({
            left: totalWidth - setWidth,
            behavior: 'auto' // 순간 이동
          })
        }
      }, 500) // 스크롤 애니메이션이 끝나길 기다림
    } else {
      // 다른 섹션은 기존 로직 유지
      const cardWidth = sliderRef.offsetWidth / 7
      sliderRef.scrollBy({ 
        left: cardWidth * 7 * direction, 
        behavior: 'smooth' 
      })
    }
  }
}

const fetchData = async () => {
  try {
    isLoading.value = true
    const headers = userStore.token ? { Authorization: `Token ${userStore.token}` } : {}

    const [boxOfficeResponse, genreResponse, followingResponse, actorResponse, releaseDateResponse] = await Promise.all([
      axios.get('http://127.0.0.1:8000/movies/recommended/box_office/', { headers }),
      axios.get('http://127.0.0.1:8000/movies/recommended/genre/', { headers }),
      axios.get('http://127.0.0.1:8000/movies/recommended/following/', { headers }),
      axios.get('http://127.0.0.1:8000/movies/recommended/reviewed_actors/', { headers }),
      axios.get('http://127.0.0.1:8000/movies/recommended/release_date/', { headers })
    ])

    boxOfficeMovies.value = boxOfficeResponse.data
    if (genreResponse.data.top_genres) {
      genreMovies.value = shuffleArray([...genreResponse.data.movies])
      topGenres.value = genreResponse.data.top_genres
    } else {
      genreMovies.value = shuffleArray([...genreResponse.data])
      topGenres.value = []
    }

    followingMovies.value = shuffleArray([...followingResponse.data])
    actorMovies.value = shuffleArray([...actorResponse.data])
    releaseDateMovies.value = shuffleArray([...releaseDateResponse.data])
  } catch (error) {
    console.error('데이터 로딩 실패:', error)
    // 401 에러 리다이렉트 제거
    boxOfficeMovies.value = []
    genreMovies.value = []
    followingMovies.value = []
    topGenres.value = []
    actorMovies.value = []
    releaseDateMovies.value = []
  } finally {
    isLoading.value = false
  }
}


// 컴포넌트 마운트 시 데이터 로드
onMounted(async () => {
  try {
    // 저장된 추천 데이터 로드
    userStore.loadRecommendedMovies()
    console.log('Loaded AI recommendations:', userStore.aiRecommendations)
    
    // 다른 데이터 로드
    await fetchData()
  } catch (error) {
    console.error('데이터 로딩 실패:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.home-container {
  padding: 0 2rem;
  max-width: 2050px;
  margin: 0 auto;
  margin-top: 50px;
  position: relative;
  min-height: 100vh;
}

/* 배경 효과 추가 */
.home-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(to bottom, 
      rgba(26, 29, 41, 1) 0%,
      rgba(26, 29, 41, 0.98) 20%,
      rgba(26, 29, 41, 0.97) 40%,
      rgba(26, 29, 41, 0.95) 60%,
      rgba(26, 29, 41, 0.98) 80%,
      rgba(26, 29, 41, 1) 100%
    ),
    radial-gradient(
      circle at center,
      rgba(31, 35, 48, 1) 0%,
      rgba(26, 29, 41, 1) 100%
    );
  z-index: -2;
}

/* 움직이는 그라데이션 효과 */
.home-container::after {
  content: '';
  position: fixed;
  top: -50%;
  left: -50%;
  right: -50%;
  bottom: -50%;
  width: 200%;
  height: 200%;
  background: transparent;
  background-image: 
    radial-gradient(circle at center, rgba(62, 71, 97, 0.1) 0%, transparent 60%),
    radial-gradient(circle at 60% 40%, rgba(106, 120, 209, 0.05) 0%, transparent 70%);
  animation: gradientBG 15s ease infinite;
  z-index: -1;
  pointer-events: none;
}

/* 배경 애니메이션 */
@keyframes gradientBG {
  0% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(-5%, 5%);
  }
  50% {
    transform: translate(-10%, 0);
  }
  75% {
    transform: translate(-5%, -5%);
  }
  100% {
    transform: translate(0, 0);
  }
}

/* 섹션 타이틀에 효과 추가 */
.section-title {
  font-size: 1.25rem;
  margin: 2.5rem 0 1rem;
  color: #ffffff;
  font-weight: 600;
  letter-spacing: 0.5px;
  position: relative;
  display: inline-block;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}

.section-title::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -5px;
  width: 100%;
  height: 2px;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0.1) 100%
  );
}

.movie-carousel {
  position: relative;
  margin: 1rem 0;
}

.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(249, 249, 249, 0.2);
  border: none;
  width: 50px;
  height: calc(100% - 2rem);
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.movie-carousel:hover .nav-button {
  opacity: 1;
}

.nav-button:hover {
  background: rgba(249, 249, 249, 0.3);
}

.nav-button.prev {
  left: 0;
}

.nav-button.next {
  right: 0;
}

.loading {
  text-align: center;
  padding: 5rem 2rem;
  font-size: 1.2rem;
  color: #f9f9f9;
  min-height: calc(20px);
  display: flex;
  justify-content: center;
  align-items: center;
}

@media (max-width: 768px) {
  .home-container {
    padding: 1rem;
  }
  
  .movie-carousel {
    padding: 0 25px;
  }
  
  .movie-slider {
    gap: 150px;
  }
  
  .movie-slider > * {
    flex: 0 0 150px;
    min-width: 150px;
  }
  
  .nav-button {
    width: 28px;
    height: calc(100% - 2rem);
    font-size: 14px;
  }
}

.recommended-section {
  margin-bottom: 3rem;  /* 섹션 간 간격 추가 */
  opacity: 0;  /* 초기 상태는 투명 */
  animation: fadeInUp 0.8s ease forwards;  /* forwards는 애니메이션 끝난 상태 유지 */
}

.recommended-section:nth-child(1) {
  animation-delay: 0.2s;
}

.recommended-section:nth-child(2) {
  animation-delay: 0.4s;
}

.recommended-section:nth-child(3) {
  animation-delay: 0.6s;
}

.recommended-section:nth-child(4) {
  animation-delay: 0.8s;
}

.recommended-section:nth-child(5) {
  animation-delay: 0.8s;
}

.movie-rank-wrapper, 
.movie-slider > .movie-card {
  opacity: 0;
  animation: fadeInUp 0.8s ease forwards;
}

.movie-rank-wrapper:nth-child(1),
.movie-slider > .movie-card:nth-child(1) {
  animation-delay: 0.1s;
}

.movie-rank-wrapper:nth-child(2),
.movie-slider > .movie-card:nth-child(2) {
  animation-delay: 0.2s;
}

.movie-rank-wrapper:nth-child(3),
.movie-slider > .movie-card:nth-child(3) {
  animation-delay: 0.3s;
}

.movie-rank-wrapper:nth-child(4),
.movie-slider > .movie-card:nth-child(4) {
  animation-delay: 0.4s;
}

.movie-rank-wrapper:nth-child(5),
.movie-slider > .movie-card:nth-child(5) {
  animation-delay: 0.5s;
}

.movie-rank-wrapper:nth-child(6),
.movie-slider > .movie-card:nth-child(6) {
  animation-delay: 0.6s;
}

.movie-rank-wrapper:nth-child(7),
.movie-slider > .movie-card:nth-child(7) {
  animation-delay: 0.7s;
}

.movie-rank-wrapper:nth-child(8),
.movie-slider > .movie-card:nth-child(8) {
  animation-delay: 0.8s;
}

.movie-rank-wrapper:nth-child(9),
.movie-slider > .movie-card:nth-child(9) {
  animation-delay: 0.9s;
}

.movie-rank-wrapper:nth-child(10),
.movie-slider > .movie-card:nth-child(10) {
  animation-delay: 1s;
}

.movie-rank-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 0 0 200px;
  min-width: 200px;
}

.rank-number {
  position: absolute;
  left: -170px;
  font-size: 20rem;
  font-weight: 900;
  color: rgba(51, 51, 51, 0.2);
  /* -webkit-text-stroke: 2px rgba(128, 128, 128, 0.5); */
  line-height: 1;
  z-index: 1;
  font-family: Franklin Gothic, sans-serif;
  letter-spacing: -5px;
}

.movie-rank-wrapper:nth-child(10) .rank-number {
  font-size: 15rem;
  left: -190px;
  letter-spacing: -45px;
}

.movie-card-container {
  position: relative;
  z-index: 2;
  width: 100%;
  margin-left: 0;
}

@media (max-width: 768px) {
  .movie-slider > * {
    flex: 0 0 150px;
    min-width: 150px;
  }

  .movie-rank-wrapper {
    min-width: 150px;
  }

  .rank-number {
    font-size: 10rem;
    left: -130px;
    letter-spacing: -3px;
  }

  .movie-rank-wrapper:nth-child(10) .rank-number {
    font-size: 8rem;
    left: -180px;
    letter-spacing: -50px;
  }
}

/* 박스오피스 섹션에만 적 특별 스타일 수정 */
.recommended-section:first-child .movie-slider {
  display: flex;
  gap: 200px;
  padding-left: 175px;
  padding-right: 50px;
  overflow-y: hidden;
  overflow-x: scroll;
  scroll-behavior: smooth;
  height: auto;
}

.recommended-section:first-child .movie-rank-wrapper {
  flex: 0 0 200px;
  min-width: 200px;
}

/* 숫자 스타일 수정 */
/* .recommended-section:first-child .rank-number {
  position: absolute;
  font-size: 20rem;
  left: -120px;
  transform: translateX(10%);
  color: #000000;
  z-index: 1;
  font-family: 'Oswald', 'Impact', 'Franklin Gothic', sans-serif;
  font-weight: 900;
  letter-spacing: -15px;
  -webkit-text-outline-stroke: 20px #666666;
} */

/* 10번 숫자 특별 처리 */
/* .recommended-section:first-child .movie-rank-wrapper:nth-child(10) .rank-number {
  font-size: 17rem;
  left: -150px;
  letter-spacing: -10px;
  transform: translateX(-8%);
  -webkit-text-stroke: 2px #666666;
} */

.recommended-section:first-child .rank-number {
  position: absolute;
  font-size: 20rem;
  left: -120px;
  transform: translateX(10%);
  color: #000000;
  z-index: 1;
  font-family: 'Oswald', 'Impact', 'Franklin Gothic', sans-serif;
  font-weight: 900;
  letter-spacing: -15px;

  /* 텍스트 테두리 효과 */
  text-shadow:
    8px 8px 8px #666666, /* 오른쪽 아래 */
    -8px -8px 8px #666666, /* 왼쪽 위 */
    -8px 8px 8px #666666, /* 왼쪽 아래 */
    8px -8px 8px #666666, /* 오른쪽 위 */
    8px 8px 8px #666666, /* 오른쪽 */
    -8px 8px 8px #666666, /* 왼쪽 */
    8px 8px 8px #666666, /* 아래 */
    8px -8px 8px #666666; /* 위 */
}

/* 10번 숫자 특별 처리 */
.recommended-section:first-child .rank-ten .rank-number {
  font-size: 17rem;
  left: -150px;
  letter-spacing: -8px;
  transform: translateX(-8%);
  /* 텍스트 테두리 효과 */
  text-shadow:
    8px 8px 8px #666666,
    -8px -8px 8px #666666,
    -8px 8px 8px #666666,
    8px -8px 8px #666666,
    8px 8px 8px #666666,
    -8px 8px 8px #666666,
    8px 8px 8px #666666,
    8px -8px 8px #666666;
}

/* 스크롤 관련 스타일 제거 */
.recommended-section:first-child .movie-slider::-webkit-scrollbar {
  display: none;
}

/* 모바일 반응형 수정 */
@media (max-width: 768px) {
  .recommended-section:first-child .movie-slider {
    gap: 200px;
    padding-left: 150px;
  }

  .recommended-section:first-child .movie-slider > * {
    flex: 0 0 200px;
    min-width: 200px;
  }

  .recommended-section:first-child .rank-number {
    font-size: 15rem;
    left: -170px;
  }

  .recommended-section:first-child .rank-ten .rank-number {
    font-size: 12rem;
    left: -200px;
    letter-spacing: -20px;
    z-index: 3;
  }
}

/* 일반 영화 슬라이더 스타일 수정 */
.movie-slider {
  display: flex;
  gap: 20px; /* 간격 조정 */
  padding: 1rem 0;
  overflow-x: scroll;
  scroll-behavior: smooth;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.movie-slider > * {
  flex: 0 0 calc((100% - (20px * 6)) / 7); /* 7개 정확히 표시 */
  min-width: calc((100% - (20px * 6)) / 7);
}

/* 애니메이션 keyframes 추가 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-rank {
  position: absolute;
  top: -15px;
  left: -15px;
  width: 30px;
  height: 30px;
  background: #4CAF50;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  z-index: 2;
}

.ai-reason {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 0.9rem;
  color: #ffffff;
}
</style>