<template>
  <div class="login-container">
    <div class="login-box">
      <!-- <img src="@/assets/logo.png" alt="MINICINEMA" class="logo"> -->
      <h1>로그인</h1>
      <form @submit.prevent="logIn">
        <div class="form-group">
          <input 
            type="text" 
            id="username" 
            v-model.trim="username"
            placeholder="사용자 이름"
            required
          >
        </div>

        <div class="form-group">
          <input 
            type="password" 
            id="password" 
            v-model.trim="password"
            placeholder="비밀번호"
            required
          >
        </div>

        <button type="submit" class="login-btn">계속하기</button>
      </form>
      
      <div class="signup-link">
        ViewFlex가 처음이신가요? 
        <router-link to="/signup">지금 가입하세요</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMovieStore } from '@/stores/movie'
import { useRouter } from 'vue-router'

const username = ref(null)
const password = ref(null)
const router = useRouter()
const store = useMovieStore()

// Initialize store with router
store.initialize(router)

const logIn = function () {
  const payload = {
    username: username.value,
    password: password.value
  }
  store.logIn(payload)
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: radial-gradient(circle at 50% 30%, #2f3b5a 0%, #1a1d29 45%);
  padding-top: 18vh;
  animation: fadeIn 0.8s ease-out forwards;
}

.login-box {
  background: #1e2230;
  padding: 40px;
  border-radius: 12px;
  width: 100%;
  max-width: 380px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  opacity: 0;
  transform: translateY(20px);
}

.logo {
  width: 180px;
  margin-bottom: 24px;
}

h1 {
  color: white;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 20px;
  width: 91%;
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

.form-group:nth-child(1) {
  animation-delay: 0.3s;
}

.form-group:nth-child(2) {
  animation-delay: 0.4s;
}

input {
  width: 100%;
  height: 48px;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #2c3142;
  background: #2c3142;
  color: white;
  font-size: 15px;
  transition: all 0.3s ease;
}

input::placeholder {
  color: #8b8b8b;
}

input:focus {
  outline: none;
  border-color: #0072d2;
  background: #2c3142;
}

.login-btn {
  width: 100%;
  height: 48px;
  background: #0072d2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
  animation-delay: 0.5s;
}

.login-btn:hover {
  background: #0066bd;
  transform: translateY(-1px);
}

.signup-link {
  color: #cacaca;
  margin-top: 24px;
  font-size: 14px;
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
  animation-delay: 0.6s;
}

.signup-link a {
  color: #0072d2;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 600;
}

.signup-link a:hover {
  text-decoration: underline;
}

/* 페이드인 애니메이션 */
@keyframes fadeIn {
  from {
    opacity: 0;
    background: radial-gradient(circle at 50% 30%, #1a1d29 0%, #1a1d29 45%);
  }
  to {
    opacity: 1;
    background: radial-gradient(circle at 50% 30%, #2f3b5a 0%, #1a1d29 45%);
  }
}

/* 슬라이드업 애니메이션 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 폼 요소들 순차적 페이드인 */
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
</style>
