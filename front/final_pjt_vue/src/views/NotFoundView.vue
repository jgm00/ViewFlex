<template>
  <div class="not-found">
    <h1>404</h1>
    <h2>페이지를 찾을 수 없습니다</h2>
    <p>요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.</p>
    <router-link to="/" class="home-link">
      <i class="fas fa-home"></i>
      홈으로 돌아가기
    </router-link>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('NotFoundView mounted')
  document.title = '404 - 페이지를 찾을 수 없습니다'
})
</script>

<style scoped>
.not-found {
  text-align: center;
  padding: 50px 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #1a1d29;
  color: #fff;
  position: relative;
  overflow: hidden;
}

.not-found::before {
  content: "404";
  position: absolute;
  font-size: 25vw;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.03);
  z-index: 0;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

h1 {
  font-size: 8rem;
  margin: 0;
  background: linear-gradient(45deg, #ff4757, #0072d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(255, 71, 87, 0.3);
  position: relative;
  z-index: 1;
  font-weight: 900;
  letter-spacing: -2px;
}

h2 {
  font-size: 2.5rem;
  margin: 20px 0;
  color: #ffffff;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  position: relative;
  z-index: 1;
}

p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 30px;
  font-size: 1.2rem;
  max-width: 600px;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.home-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 15px 30px;
  background: linear-gradient(45deg, #0072d2, #00a8ff);
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  box-shadow: 0 4px 15px rgba(0, 114, 210, 0.3);
}

.home-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 114, 210, 0.4);
}

.home-link:active {
  transform: translateY(1px);
}

@media (max-width: 768px) {
  h1 {
    font-size: 6rem;
  }
  
  h2 {
    font-size: 2rem;
  }
  
  p {
    font-size: 1rem;
    padding: 0 20px;
  }
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
  100% {
    transform: translateY(0px);
  }
}
</style>