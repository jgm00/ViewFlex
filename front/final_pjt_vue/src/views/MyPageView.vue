<template>
  <div class="christmas-container">
      <!-- 눈 내리는 효과 증가 -->
      <div class="christmas-container">
      <!-- 눈 내리는 효과 -->
      <div class="snowflakes" aria-hidden="true">
        <div v-for="n in 15" :key="n" class="snowflake" 
             :style="{ 
               left: Math.random() * 100 + '%',
               fontSize: (Math.random() * 1 + 1.2) + 'em',
               opacity: Math.random() * 0.4 + 0.4,
               animationDelay: -(Math.random() * 20) + 's',
               animationDuration: 10 + Math.random() * 15 + 's'
             }">
          {{ SNOW_FLAKES[Math.floor(Math.random() * SNOW_FLAKES.length)] }}
        </div>
      </div>
  
      <div v-if="userInfo" class="mypage-container">
        <div class="user-info">
          <ProfileInfo :userInfo="userInfo" @follow="Follow" />
        </div>
  
        <div class="reviews-section">
          <UserReview :reviews="userInfo.reviews" />
        </div>
  
        <div class="chart-section">
          <GenreChart :genreStats="genreStats" />
        </div>
  
        <div class="recommendations-section">
          <h2 class="section-title">✨ AI가 발견한 당신의 숨은 취향 영화</h2>
          <div v-if="isLoading" class="loading">
            Loading...
          </div>
          <div v-else-if="userStore.aiRecommendations?.length > 0" class="movie-grid">
            <SimpleMovieCard 
              v-for="movie in displayedAiMovies" 
              :key="movie.id" 
              :movie="movie"
            />
            <button 
              v-if="!showAllAi && userStore.aiRecommendations.length > initialAiDisplayCount" 
              @click="showAllAi = true" 
              class="show-more-btn"
            >
              더보기
            </button>
            <button 
              v-if="showAllAi && userStore.aiRecommendations.length > initialAiDisplayCount" 
              @click="showAllAi = false" 
              class="show-less-btn"
            >
              접기
            </button>
          </div>
          <div v-else class="empty-state">
            <div class="empty-state-content">
              <div class="empty-state-icon">🎬</div>
              <h3>아직 AI 추천이 준비되지 않았어요!</h3>
              <p>영화 취향 설문에 참여하고 맞춤 추천을 받아보세요.</p>
              <router-link 
                to="/survey" 
                class="survey-link-btn"
              >
                설문 참여하기
              </router-link>
            </div>
          </div>
        </div>
  
        <div class="liked-movies">
          <LikedMovie :likedMovies="likedMovies" />
        </div>
      </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { useMovieStore } from '@/stores/movie'
  import { useRoute, useRouter } from 'vue-router'
  import axios from 'axios'
  import Chart from 'chart.js/auto'
  import ProfileInfo from '@/components/ProfileInfo.vue'
  import LikedMovie from '@/components/LikedMovie.vue'
  import UserReview from '@/components/UserReview.vue'
  import GenreChart from '@/components/GenreChart.vue'
  import MovieCard from '@/components/MovieCard.vue'
  import SimpleMovieCard from '@/components/SimpleMovieCard.vue'
  
  const store = useMovieStore()
  const route = useRoute()
  const router = useRouter()
  
  const userInfo = ref(null)
  const genreStats = ref([])
  let chartInstance = null
  
  const showFollowingModal = ref(false)
  const showFollowerModal = ref(false)
  
  // 눈송이 상수 정의
  const SNOW_FLAKES = ['❅', '❆', '❄', '✻', '❋'];
  
  const userStore = useMovieStore()
  const aiSliderRef = ref(null)
  const isLoading = ref(true)
  
  watch(() => route.params.username, (newUsername) => {
    if (newUsername) {
      getPerson(newUsername)
      getGenreStats(newUsername)
    }
  })
  
  const getPerson = (username) => {
    axios({
      method: 'get',
      url: `${store.API_URL}/users/${username}/mypage/`,
      headers: {
        Authorization: `Token ${store.token}`
      }
    })
      .then((res) => {
        userInfo.value = res.data
        console.log(userInfo)
      })
      .catch((err) => {
        console.log(err)
      })
  }
  
  const getGenreStats = (username) => {
    axios({
      method: 'get',
      url: `${store.API_URL}/movies/liked_genre/${username}/`,
      headers: {
        Authorization: `Token ${store.token}`
      }
    })
      .then((res) => {
        genreStats.value = res.data
        renderChart()
      })
      .catch((err) => {
        console.log(err)
      })
  }
  
  const renderChart = () => {
    const ctx = document.getElementById('genreChart').getContext('2d')
  
    if (chartInstance) {
      chartInstance.destroy()
    }
  
    chartInstance = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: genreStats.value.map(item => item.genre),
        datasets: [{
          data: genreStats.value.map(item => item.count),
          backgroundColor: [
            '#FF6384', // Red
            '#36A2EB', // Blue
            '#FFCE56', // Yellow
            '#4BC0C0', // Teal
            '#9966FF', // Purple
            '#FF9F40', // Orange
            '#FFCD94', // Peach
            '#B39DDB', // Lavender
            '#F06292', // Pink
            '#81C784', // Light Green
            '#FFD54F', // Light Orange
            '#64B5F6', // Light Blue
            '#BA68C8', // Light Purple
            '#E57373', // Light Red
            '#AED581', // Light Lime
            '#DCE775', // Light Yellow
            '#FF8A65', // Coral
            '#A1887F', // Brown
            '#90A4AE', // Gray
            '#F48FB1']
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: '장르 통계'
          }
        }
      }
    })
  }
  
  const likedMovies = computed(() => {
    if (!userInfo.value?.person.id) return []
    return store.movies.filter(movie => {
      return movie.like_users?.includes(userInfo.value.person.id)
    })
  })
  
  watch(() => store.likes.value, () => {
    getPerson(route.params.username)
  }, { deep: true })
  
  const Follow = async () => {
    try {
      const response = await axios({
        method: 'post',
        url: `${store.API_URL}/users/${route.params.username}/follow/`,
        headers: {
          Authorization: `Token ${store.token}`
        }
      })
      
      // userInfo 업데이트
      userInfo.value.is_followed = response.data.is_followed
      
      // 팔로우 상태에 따른 알림 메시지 표시
      if (response.data.is_followed) {
        alert(`${route.params.username}님을 팔로우했습니다.`)
      } else {
        alert(`${route.params.username}님을 팔로우 취소했습니다.`)
      }
      
      // 팔로워 수 업데이트를 위해 사용자 정보 다시 불러오기
      getPerson(route.params.username)
      
    } catch (error) {
      console.error('팔로우 처리 실패:', error)
      alert('팔로우 처리 중 오류가 발생했습니다.')
    }
  }
  
  const goToUserPage = (username) => {
    router.push({ name: 'MyPageView', params: { username: username }})
    showFollowingModal.value = false
    showFollowerModal.value = false
  }
  
  onMounted(async () => {
    try {
      isLoading.value = true
      const username = route.params.username
      
      // AI 추천 영화 로드
      await userStore.loadRecommendedMovies()
      console.log('AI Recommendations:', userStore.aiRecommendations) // 디버깅용
      
      await store.LikedMovies()
      await getPerson(username)
      await getGenreStats(username)
      if (!store.movies.length) {
        await store.getMovies()
      }
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      isLoading.value = false
    }
  })
  
  const scrollCarousel = (type, direction) => {
    const sliderRef = aiSliderRef.value
    if (sliderRef) {
      const cardWidth = sliderRef.offsetWidth / 7
      sliderRef.scrollBy({ 
        left: cardWidth * 7 * direction, 
        behavior: 'smooth' 
      })
    }
  }
  
  const showAllAi = ref(false)
  const initialAiDisplayCount = 7 // 처음에 보여줄 AI 추천 영화 개수
  
  const displayedAiMovies = computed(() => {
    return showAllAi.value 
      ? userStore.aiRecommendations 
      : userStore.aiRecommendations?.slice(0, initialAiDisplayCount)
  })
  </script>
  <style scoped>
  .mypage-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    display: grid;
    gap: 2rem;
    grid-template-areas:
      "profile profile"
      "reviews chart"
      "recommendations recommendations"
      "liked liked";
    grid-template-columns: 1fr 1fr;
    animation: fadeIn 0.6s ease-out;
    will-change: opacity, transform;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .user-info {
    animation: slideUp 0.5s ease-out 0.1s both;
  }
  
  .reviews-section {
    animation: slideUp 0.5s ease-out 0.2s both;
  }
  
  .chart-section {
    animation: slideUp 0.5s ease-out 0.3s both;
  }
  
  .recommendations-section {
    animation: slideUp 0.5s ease-out 0.4s both;
  }
  
  .liked-movies {
    animation: slideUp 0.5s ease-out 0.5s both;
  }
  
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .user-info {
    grid-area: profile;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }
  
  .user-info :deep(.profile-header) {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 2rem;
    align-items: start;
  }
  
  .user-info :deep(.profile-image) {
    width: 200px;
  }
  
  .user-info :deep(.stats-section) {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  
  .user-info :deep(.stat-box) {
    padding: 1rem;
    min-width: auto;
  }
  
  .reviews-section {
    grid-area: reviews;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }
  
  .chart-section {
    grid-area: chart;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }
  
  .recommendations-section {
    grid-area: recommendations;
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #e74c3c;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }
  
  .recommendations-section h2 {
    color: #2c3e50;
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    font-weight: 600;
  }
  
  .recommendations-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .analysis-box {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .analysis-text {
    color: #2c3e50;
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }
  
  .recommended-movies {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin-top: 1rem;
  }
  
  .movie-recommendation {
    width: 100%;
    aspect-ratio: 2/3;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease;
  }
  
  .movie-recommendation:hover {
    transform: translateY(-5px);
  }
  
  .recommendation-card {
    width: 100%;
    aspect-ratio: 2/3;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease;
  }
  
  .recommendation-card:hover {
    transform: translateY(-5px);
  }
  
  .recommendation-reason {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .reason-text {
    color: #2c3e50;
    font-size: 1rem;
  }
  
  .loading-recommendations {
    text-align: center;
    color: #666;
    font-size: 1rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 10px;
    border: 1px dashed #ddd;
  }
  
  .liked-movies {
    grid-area: liked;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 1rem;
  }
  
  /* 추가할 스타일 */
  .liked-movies :deep(.movie-grid) {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin-top: 1rem;
  }
  
  .liked-movies :deep(.movie-card) {
    width: 100%;
    aspect-ratio: 2/3;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease;
  }
  
  .liked-movies :deep(.movie-card:hover) {
    transform: translateY(-5px);
  }
  
  @media (max-width: 968px) {
    .mypage-container {
      grid-template-areas:
        "profile"
        "reviews"
        "chart"
        "liked";
      grid-template-columns: 1fr;
    }
  
    .user-info :deep(.profile-header) {
      grid-template-columns: 1fr;
      text-align: center;
    }
  
    .user-info :deep(.profile-image) {
      margin: 0 auto;
    }
  }
  
  @media (max-width: 480px) {
    .user-info :deep(.stats-section) {
      grid-template-columns: 1fr;
    }
  }
  
  .follows-container {
    grid-area: follows;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
  
  .section-container {
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }
  
  .section-container h2 {
    color: #2c3e50;
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    font-weight: 600;
  }
  
  .follow-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 1rem;
  }
  
  .follow-card {
    background: #f8f9fa;
    padding: 0.8rem;
    border-radius: 8px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    color: #2c3e50;
    font-weight: 500;
    border: 1px solid #eee;
  }
  
  .follow-card:hover {
    background: #42b883;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(66, 184, 131, 0.2);
  }
  
  .empty-message {
    text-align: center;
    color: #666;
    font-size: 1rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 10px;
    border: 1px dashed #ddd;
  }
  
  @media (max-width: 968px) {
    .mypage-container {
      grid-template-areas:
        "profile"
        "reviews"
        "chart"
        "liked"
        "follows";
    }
  
    .follows-container {
      grid-template-columns: 1fr;
    }
  
    .section-container {
      padding: 1.5rem;
    }
  }
  
  @media (max-width: 480px) {
    .mypage-container {
      padding: 1rem;
    }
  
    .follow-grid {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    }
  
    .section-container h2 {
      font-size: 1.3rem;
    }
  }
  
  .clickable-header {
    cursor: pointer;
    transition: color 0.3s ease;
  }
  
  .clickable-header:hover {
    color: #42b883;
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    width: 90%;
    max-width: 500px;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .modal-list {
    margin: 1.5rem 0;
  }
  
  .modal-item {
    padding: 1rem;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: background 0.3s ease;
  }
  
  .modal-item:hover {
    background: #f5f5f5;
    color: #42b883;
  }
  
  .modal-close {
    width: 100%;
    padding: 0.8rem;
    background: #42b883;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s ease;
  }
  
  .modal-close:hover {
    background: #3aa876;
  }
  
  .christmas-container {
    min-height: 100vh;
    background: linear-gradient(to bottom, #1a2a3a, #2c3e50);
    position: relative;
    overflow: hidden;
  }
  
  /* 눈 내리는 효과 스타일 */
  .snowflakes {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
  }
  
  .snowflake {
    color: #fff;
    position: fixed;
    top: -10%;
    animation: snowfall linear infinite;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.4);
    z-index: 1;
    pointer-events: none;
  }
  
  @keyframes snowfall {
    0% {
      transform: translateY(0) rotate(0deg);
    }
    25% {
      transform: translateY(25vh) translateX(-10px) rotate(90deg);
    }
    50% {
      transform: translateY(50vh) translateX(10px) rotate(180deg);
    }
    75% {
      transform: translateY(75vh) translateX(-10px) rotate(270deg);
    }
    100% {
      transform: translateY(110vh) translateX(10px) rotate(360deg);
    }
  }
  
  /* 산타 스타일 수정 */
  .decoration.bottom-right {
    position: fixed;
    font-size: 5rem;
    right: 2rem;
    bottom: 2rem;
    width: 150px;  /* 산타 크기 조절 */
    height: auto;
    animation: santaBounce 2s ease-in-out infinite;
    filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.3));
    z-index: 1;
  }
  
  @keyframes santaBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }
  
  /* 크리스마스 전구 효과 */
  .lights {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-around;
    padding: 10px;
  }
  
  .light {
    width: 15px;
    height: 15px;
    border-radius: 50%;
    animation: twinkle 1s ease-in-out infinite alternate;
  }
  
  .light:nth-child(odd) {
    background: #e74c3c;
    animation-delay: 0.5s;
  }
  
  .light:nth-child(even) {
    background: #2ecc71;
    animation-delay: 1s;
  }
  
  /* 컴포넌트 스타일 크리스마스 테마로 수정 */
  .user-info, .reviews-section, .chart-section, .liked-movies {
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #e74c3c;
    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.2);
    position: relative;
  }
  
  .user-info::before, .reviews-section::before, 
  .chart-section::before {
    /* content: '🎀'; */
    position: absolute;
    top: -35px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 4rem;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  }
  
  /* 애니메이션 키프레임 */
  @keyframes sway {
    0%, 100% { transform: rotate(-5deg); }
    50% { transform: rotate(5deg); }
  }
  
  @keyframes twinkle {
    0% { opacity: 0.3; transform: scale(0.8); }
    100% { opacity: 1; transform: scale(1.2); }
  }
  
  /* 눈이 쌓이는 효과를 위한 컨테이너 추가 */
  .christmas-container {
    min-height: 100vh;
    background: linear-gradient(to bottom, #1a2a3a, #2c3e50);
    position: relative;
    overflow: hidden;
  }
  
  /* 쌓인 눈 효과 수정 */
  .christmas-container::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background: linear-gradient(to bottom, 
      transparent 0%,
      rgba(255, 255, 255, 0.1) 10%,
      rgba(255, 255, 255, 0.2) 20%,
      rgba(255, 255, 255, 0.4) 40%,
      rgba(255, 255, 255, 0.6) 60%,
      rgba(255, 255, 255, 0.8) 80%,
      rgba(255, 255, 255, 0.9) 90%,
      rgba(255, 255, 255, 1) 100%
    );
    filter: blur(8px);
    z-index: 2;
    transform: scaleY(1.2);
  }
  
  /* 양쪽 끝에 눈 더미 효과 수정 */
  .christmas-container::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 80px;
    background: 
      radial-gradient(ellipse at 20% 100%, 
        rgba(255, 255, 255, 0.8) 0%,
        rgba(255, 255, 255, 0.4) 40%,
        transparent 70%
      ),
      radial-gradient(ellipse at 80% 100%, 
        rgba(255, 255, 255, 0.8) 0%,
        rgba(255, 255, 255, 0.4) 40%,
        transparent 70%
      );
    filter: blur(5px);
    z-index: 2;
  }
  
  /* 눈이 쌓이는 애니메이션 수정 */
  .snowflake {
    color: #fff;
    position: fixed;
    top: -10%;
    animation: snowfall-and-pile linear infinite;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.4);
    z-index: 1;
    pointer-events: none;
  }
  
  @keyframes snowfall-and-pile {
    0% {
      transform: translateY(0) rotate(0deg);
      opacity: 0.8;
    }
    85% {
      opacity: 0.8;
    }
    95% {
      opacity: 0.4;
    }
    100% {
      transform: translateY(calc(100vh - 40px)) translateX(10px) rotate(360deg);
      opacity: 0;
    }
  }
  
  /* 눈이 쌓이는 효과를 위한 개별 눈송이 */
  .snow-pile {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: 40px;
    background: white;
    opacity: 0;
    animation: snow-accumulate 3s ease-out forwards;
    z-index: 1;
  }
  
  @keyframes snow-accumulate {
    from {
      opacity: 0;
      transform: translateY(40px);
    }
    to {
      opacity: 0.8;
      transform: translateY(0);
    }
  }
  
  /* 찜한 영화 섹션의 리본만 크기 수정 */
  .liked-movies::before {
    /* content: '🎀'; */
    position: absolute;
    top: -90px;  /* 위치 약간 더 위로 */
    left: 50%;
    transform: translateX(-50%);
    font-size: 10rem;  /* 다른 리본보다 더 크게 */
    filter: drop-shadow(0 3px 6px rgba(0,0,0,0.15));  /* 그림자도 약간 강화 */
    z-index: 10;
  }
  
  .movie-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr); /* 한 줄에 7개씩 */
    gap: 1rem;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .show-more-btn, .show-less-btn {
    display: block;
    width: 100%;
    max-width: 200px;
    margin: 1.5rem auto 0;
    padding: 0.8rem;
    background: rgba(49, 52, 62, 0.7);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.3s ease;
  }
  
  .show-more-btn:hover {
    background: #3aa876;
  }
  
  .show-less-btn {
    background: #666;
  }
  
  .show-less-btn:hover {
    background: #555;
  }
  
  /* 반응형 디자인 */
  @media (max-width: 1400px) {
    .movie-grid {
      grid-template-columns: repeat(5, 1fr);
    }
  }
  
  @media (max-width: 1100px) {
    .movie-grid {
      grid-template-columns: repeat(4, 1fr);
    }
  }
  
  @media (max-width: 900px) {
    .movie-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }
  
  @media (max-width: 600px) {
    .movie-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  /* SimpleMovieCard 크기 조절을 위한 스타일 */
  .movie-grid :deep(.movie-card) {
    width: 100%;
    aspect-ratio: 2/3;
    max-width: 180px; /* 최대 너비 제한 */
    margin: 0 auto;
  }
  
  .movie-item {
    position: relative;
    transition: transform 0.3s ease;
  }
  
  .movie-item:hover {
    transform: translateY(-5px);
  }
  
  .movie-number {
    position: absolute;
    top: -15px;
    left: -15px;
    width: 30px;
    height: 30px;
    background: #e74c3c;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 1rem;
    box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
    z-index: 2;
  }
  
  .movie-reason {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 0.8rem;
    font-size: 0.9rem;
    border-radius: 8px 8px 0 0;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 1;
  }
  
  .movie-item:hover .movie-reason {
    opacity: 1;
  }
  
  .reason-text {
    margin: 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* SimpleMovieCard 크기 조절을 위한 스타일 수정 */
  .movie-grid :deep(.movie-card) {
    width: 100%;
    aspect-ratio: 2/3;
    max-width: 180px;
    margin: 0 auto;
    transition: transform 0.3s ease;
  }
  
  .movie-grid :deep(.movie-card:hover) {
    transform: none; /* SimpleMovieCard의 기존 hover 효과 제거 */
  }
  
  .empty-state {
    text-align: center;
    padding: 3rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    backdrop-filter: blur(10px);
  }
  
  .empty-state-content {
    max-width: 400px;
    margin: 0 auto;
  }
  
  .empty-state-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    animation: bounce 2s infinite;
  }
  
  .empty-state h3 {
    color: #2c3e50;
    font-size: 1.8rem;
    margin-bottom: 1rem;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  
  .empty-state p {
    color: #2c3e50;
    font-size: 1.2rem;
    margin-bottom: 2rem;
    line-height: 1.6;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  
  .survey-link-btn {
    display: inline-block;
    padding: 0.8rem 2rem;
    background:  rgba(37, 99, 235, 0.8);
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
  }
  
  .survey-link-btn:hover {
    background: #2d8b61;
    transform: translateY(-2px);
  }
  
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }
  </style>