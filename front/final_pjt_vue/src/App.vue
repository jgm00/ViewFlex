<template>
  <header>
    <nav class="navbar">
      <div class="nav-links">
        <RouterLink :to="{ name: 'HomeView' }" class="logo-link">
          <Logo />
        </RouterLink>
        <RouterLink :to="{ name: 'MovieListView' }" class="nav-link">시리즈</RouterLink>
        <RouterLink :to="{ name: 'TheaterListView' }" class="nav-link">극장</RouterLink>
      </div>

      <div class="search-section">
        <input 
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text"
          placeholder="영화 제목 또는 배우 검색..."
          class="search-input"
        >
      </div>

      <div class="auth-links">
        <RouterLink :to="{name:'SignUpView'}" v-if="!store.isLogin" class="nav-link">회원가입</RouterLink>
        <RouterLink :to="{name:'LogInView'}" v-if="!store.isLogin" class="nav-link">로그인</RouterLink>
        <div class="user-section" v-if="store.isLogin">
          <RouterLink :to="{ name: 'MyPageView', params: { username: store.username }}" class="nav-link">
            {{ store.username }}
          </RouterLink>
          <form @submit.prevent="logOut" class="logout-form">
            <button type="submit" class="logout-btn">로그아웃</button>
          </form>
        </div>
      </div>
    </nav>
  </header>
  <div class="router-view-container" :class="{ 
    'movie-detail-page': $route.name === 'MovieDetailView',
    'mypage': $route.name === 'MyPageView'
  }">
    <RouterView />
  </div>

  <!-- 챗봇 버튼 수정 -->
  <div class="chat-wrapper">
    <div class="snow-effect">
      <span>❄</span>
      <span>❄</span>
      <span>❄</span>
      <span>⛄</span>
    </div>
    <div class="rudolph-sleigh">🦌🛷</div>
    <div class="chat-button" @click="toggleChatModal">
      <span class="chat-icon">🎅</span>
    </div>
  </div>

  <!-- 챗봇 모달 -->
  <div v-if="showChatModal" class="chat-modal">
    <div class="chat-header">
      <h3>ViewFlex</h3>
      <button @click="toggleChatModal" class="close-button">×</button>
    </div>
    <div class="chat-messages" ref="chatMessagesRef">
      <div v-for="(message, index) in chatMessages" 
           :key="index" 
           :class="['message', message.type]">
        <div v-if="message.html" v-html="message.text"></div>
        <div v-else>{{ message.text }}</div>
      </div>
    </div>
    <div class="chat-input">
      <input 
        v-model="userInput" 
        @keyup.enter="sendMessage"
        placeholder="메시지를 입력하세요..."
      >
      <button @click="sendMessage">전송</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterView, RouterLink, useRouter, useRoute } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import axios from 'axios'
import Logo from '@/components/Logo.vue'

const router = useRouter()
const store = useMovieStore()
const searchQuery = ref('')
const route = useRoute()

// 챗봇 관련 상태
const showChatModal = ref(false)
const userInput = ref('')
const chatMessagesRef = ref(null)
const chatMessages = ref([
  { type: 'bot', text: '안녕하세요! 크리스마스 영화 추천 AI 어시스턴트입니다. 어떤 영화를 찾으시나요? 🎄✨' }
])

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  try {
    store.isLoading = true
    const query = searchQuery.value.trim()
    const encodedQuery = encodeURIComponent(query)
    
    const headers = store.token 
      ? { Authorization: `Token ${store.token}` }
      : {}
    
    const response = await axios.get(
      `${store.API_URL}/movies/search/?query=${encodedQuery}`,
      { headers }
    )
    
    store.searchResults = response.data
    
    router.push({ 
      name: 'SearchResultsView',
      query: { q: query }
    })
    
    searchQuery.value = ''
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    store.isLoading = false
  }
}

const logOut = function () {
  store.logOut()
}

onMounted(() => {
  if (store.token) {
    store.LikedMovies()
  }
})

// 챗봇 관련 메서드
const toggleChatModal = () => {
  showChatModal.value = !showChatModal.value
}

const scrollToBottom = () => {
  if (chatMessagesRef.value) {
    setTimeout(() => {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }, 100)
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim()) return

  chatMessages.value.push({ 
    type: 'user', 
    text: userInput.value.trim() 
  })
  
  const userQuestion = userInput.value
  userInput.value = ''
  scrollToBottom()

  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: "당신은 크리스마스 분위기의 영화 전문가입니다. 사용자에게 크리스마스와 겨울에 어울리는 영화를 추천해주고, 영화에 대한 정보를 제공합니다. 대화할 때 이모지를 적절히 사용하여 친근한 분위기를 만듭니다."
          },
          {
            role: "user",
            content: userQuestion
          }
        ],
        temperature: 0.7,
        max_tokens: 200
      },
      {
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    )

    const botResponse = response.data.choices[0].message.content
    const formattedResponse = botResponse
      // 영화 제목 포맷팅
      .replace(/\*\*(.*?)\*\*/g, '<span class="movie-title">$1</span>')
      // 개봉연도 포맷팅
      .replace(/(\d{4})/g, '<span class="year">$1</span>')
      // 추천 포인트 포맷팅
      .replace(/(추천 포인트|줄거리|감독|출연|장르):/g, '<span class="label">$1:</span>')
      // 구분선 추가
      .split('\n').join('<br>')

    chatMessages.value.push({ 
      type: 'bot', 
      text: formattedResponse,
      html: true
    })
    scrollToBottom()
  } catch (error) {
    console.error('ChatGPT API 오류:', error)
    chatMessages.value.push({ 
      type: 'bot', 
      text: '죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요. 🙏' 
    })
    scrollToBottom()
  }
}
</script>

<style>
/*   역 스타일 */
body {
  margin: 0;
  padding: 0;
  background-color: rgb(26, 29, 41) !important;
  min-height: 100vh;
}

#app {
  background-color: rgb(26, 29, 41);
  min-height: 100vh;
}

/* Navbar 스타일 */
.navbar {
  background-color: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 0.5rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 52px;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  text-decoration: none;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  font-size: 0.95rem;
  letter-spacing: 0.5px;
  padding: 0.5rem 0;
  position: relative;
  transition: all 0.3s ease;
}

.nav-link:hover {
  color: #ffffff;
}

/* 밑줄 애니메이션 제거하고 디즈니+ 스타일로 변경 */
.nav-link::after {
  display: none;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logout-btn {
  background-color: #0072d2;
  color: #ffffff;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background-color: #0056c7;
  transform: scale(1.05);
}

/* 활성 링크 스타일 */
.router-link-active {
  color: #0072d2;
  font-weight: 600;
}

/* RouterView 컨테이너 */
.router-view-container {
  margin-top: 50px;
  min-height: calc(100vh - 50px);
  padding: 2rem 3rem;
}

/* MovieDetail 페이지와 MyPage 패딩 제거 */
.router-view-container.movie-detail-page,
.router-view-container.mypage {
  padding: 0;
}

/* 로고 크기 조정 */
.logo img {
  height: 35px;
}

/* 검색 섹션 스타일 수정 */
.search-section {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.9rem;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-input:focus {
  outline: none;
  border-color: #0072d2;
  background: rgba(255, 255, 255, 0.15);
}

/* 챗봇 관련 스타일 */
.chat-wrapper {
  position: fixed;
  bottom: 20px;
  right: 40px;
  width: 200px;
  height: 200px;
  pointer-events: none;
  z-index: 999;
}

.chat-button {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 65px;
  height: 65px;
  background: #e74d3c98;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
  z-index: 1000;
  animation: float 3s ease-in-out infinite;
  pointer-events: auto;
}

/* 눈 내리는 효과 */
.snow-effect::before,
.snow-effect::after,
.snow-effect span {
  position: absolute;
  animation: snowfall 3s linear infinite;
  opacity: 0;
  font-size: 20px;
  text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}

/* 기존 눈송이 위치 수정 */
.snow-effect::before { 
  content: '❄'; 
  right: 25px; 
  animation-delay: 0s; 
}
.snow-effect::after { 
  content: '⛄'; 
  right: 65px; 
  animation-delay: 1.5s;
  font-size: 22px; 
}

/* 추가 눈송이와 눈사람 위치 수정 */
.snow-effect span:nth-child(1) { 
  content: '❄'; 
  right: 15px; 
  animation-delay: 0.5s; 
}
.snow-effect span:nth-child(2) { 
  content: '❄'; 
  right: 45px; 
  animation-delay: 1s; 
}
.snow-effect span:nth-child(3) { 
  content: '❄'; 
  right: 75px; 
  animation-delay: 2s; 
}
.snow-effect span:nth-child(4) { 
  content: '⛄'; 
  right: 85px; 
  animation-delay: 2.5s;
  font-size: 22px;
}

/* 눈 내리는 애니메이션 수정 - 더 자연스러운 좌우 흔들림 */
@keyframes snowfall {
  0% {
    transform: translateY(-20px) translateX(-5px) rotate(0deg);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  100% {
    transform: translateY(80px) translateX(15px) rotate(360deg); 
    opacity: 0;
  }
}

/* 루돌프와 썰매 스타일 수정 */
.rudolph-sleigh {
  position: absolute;
  font-size: 24px;
  opacity: 0;
  bottom: 100px;
  right: -100px;
  transition: all 0.3s ease;
}

.rudolph-sleigh::after {
  content: '🎁';
  position: absolute;
  font-size: 18px;
  top: -10px;
  right: 2px;
  opacity: 1;
  transition: all 0.3s ease;
}

/* 호버 효과 수정 */
.chat-wrapper:hover .rudolph-sleigh {
  opacity: 1;
  animation: sleighRide 8s ease-in-out infinite;
}

.chat-wrapper:hover .rudolph-sleigh::after {
  animation: giftDrop 8s ease-in-out infinite;
}

/* 썰매 애니메이션 수정 */
@keyframes sleighRide {
  0% {
    right: -100px;
    bottom: 100px;
    transform: scaleX(1);
  }
  30% {
    right: 50px;
    bottom: 100px;
    transform: scaleX(1);
  }
  40% {
    right: 80px;
    bottom: 180px;  /* 높이 점프 */
    transform: scaleX(1);
  }
  50% {
    right: 120px;
    bottom: 180px;  /* 최고점에서 방향 전환 */
    transform: scaleX(-1);
  }
  60% {
    right: 150px;
    bottom: 100px;  /* 부드럽게 착지 */
    transform: scaleX(-1);
  }
  70% {
    right: 100px;
    bottom: 100px;
    transform: scaleX(-1);
  }
  100% {
    right: -100px;
    bottom: 100px;
    transform: scaleX(1);
  }
}

/* 선물 떨어지는 애니메이션 수정 */
@keyframes giftDrop {
  0%, 35% {
    opacity: 1;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(0);
  }
  45% {
    opacity: 1;
    transform: translateY(30px) rotate(45deg);
  }
  50% {
    opacity: 1;
    transform: translateY(60px) rotate(90deg);
  }
  55% {
    opacity: 1;
    transform: translateY(90px) rotate(180deg);
  }
  60% {
    opacity: 0;
    transform: translateY(100px) rotate(360deg);
  }
  100% {
    opacity: 0;
    transform: translateY(100px) rotate(360deg);
  }
}

/* 부드러운 움직임을 위한 float 애니메이션 추가 */
@keyframes float {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0);
  }
}

.chat-modal {
  position: fixed;
  bottom: 110px;
  right: 60px;
  width: 350px;
  height: 500px;
  background: #1a1d29;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  animation: modalAppear 0.3s ease-out;
}

@keyframes modalAppear {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.chat-icon {
  font-size: 30px;
  animation: wave 2s ease-in-out infinite;
  display: inline-block;
  z-index: 2;  /* 눈과 루돌프 위에 보이도록 */
  position: relative;  /* z-index가 적용되도록 */
}

@keyframes wave {
  0%, 100% {
    transform: rotate(-10deg);
  }
  50% {
    transform: rotate(10deg);
  }
}

.chat-header {
  padding: 20px;
  background: #e74c3c;
  color: white;
  border-radius: 15px 15px 0 0;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.chat-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.close-button {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: white;
  font-size: 25px;
  cursor: pointer;
}

.chat-messages {
  flex-grow: 1;
  padding: 15px;
  overflow-y: auto;
  background: #f8f9fa;
}

.message {
  margin: 12px 0;
  padding: 15px;
  border-radius: 12px;
  max-width: 85%;
  line-height: 1.5;
  white-space: pre-wrap;
}

.message.user {
  background: #2c3e50;
  color: white;
  margin-left: auto;
}

.message.bot {
  background: white;
  border: 1px solid #dee2e6;
  margin-right: auto;
  font-size: 0.95rem;
}

.message.bot .movie-title {
  color: #e74c3c;
  font-weight: 600;
}

.message.bot .year {
  color: #666;
  font-size: 0.9em;
}

.message.bot .rating {
  color: #f39c12;
  font-weight: 600;
}

.message.bot .description {
  margin-top: 5px;
  color: #2c3e50;
}

.message.bot .separator {
  color: #95a5a6;
  margin: 0 5px;
}

.chat-input {
  padding: 15px;
  display: flex;
  gap: 10px;
  border-top: 1px solid #dee2e6;
}

.chat-input input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #dee2e6;
  border-radius: 5px;
}

.chat-input button {
  padding: 8px 15px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.chat-input button:hover {
  background: #c0392b;
}

.auth-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-left: auto;
}

/* 눈 내리는 효과를 위한 컨테이너 */
.snow-container {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s;
}

/* 눈송이 스타일 */
.snow-container::before,
.snow-container::after {
  content: '❄';
  position: absolute;
  color: white;
  animation: snowfall 2s linear infinite;
  opacity: 0;
}

.snow-container::before { left: 30%; top: -20px; }
.snow-container::after { left: 60%; top: -20px; animation-delay: 1s; }

/* 루돌프 스타일 */
.rudolph {
  position: absolute;
  font-size: 24px;
  left: -50px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  transition: opacity 0.3s;
}

/* 호버 효과 */
.chat-button:hover .snow-container {
  opacity: 1;
}

.chat-button:hover .rudolph {
  opacity: 1;
  animation: rudolphRun 2s linear infinite;
}

/* 눈 내리는 애니메이션 */
@keyframes snowfall {
  0% {
    transform: translateY(-20px) rotate(0deg);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  100% {
    transform: translateY(80px) rotate(360deg);
    opacity: 0;
  }
}

/* 루돌프가 달리는 애니메이션 */
@keyframes rudolphRun {
  0% {
    left: -50px;
    transform: translateY(-50%) scaleX(1);
  }
  45% {
    left: 50%;
    transform: translateY(-50%) scaleX(1);
  }
  50% {
    left: 50%;
    transform: translateY(-50%) scaleX(-1);
  }
  95% {
    left: -50px;
    transform: translateY(-50%) scaleX(-1);
  }
  100% {
    left: -50px;
    transform: translateY(-50%) scaleX(1);
  }
}

.logo-link {
  text-decoration: none;
  padding: 0.3rem 0;
  margin-right: 1rem;
  display: flex;
  align-items: center;
  transform: translateY(-4.5px);
}

.logo-link:hover {
  text-decoration: none;
}
</style>