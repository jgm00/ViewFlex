<template>
  <div class="signup-container">
    <div class="signup-box">
      <!-- <img src="@/assets/logo.png" alt="MINICINEMA" class="logo"> -->
      <h1>회원가입</h1>
      <form @submit.prevent="signUp">
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
            id="password1" 
            v-model.trim="password1"
            placeholder="비밀번호"
            required
          >
        </div>

        <div class="form-group">
          <input 
            type="password" 
            id="password2" 
            v-model.trim="password2"
            placeholder="비밀번호 확인"
            required
          >
        </div>

        <button type="submit" class="signup-btn">가입하기</button>
      </form>

      <div class="login-link">
        이미 ViewFlex 계정이 있으신가요? 
        <router-link to="/login">로그인</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useMovieStore } from '@/stores/movie';
import { useRouter } from 'vue-router';
import { ref } from 'vue';

const username = ref(null)
const password1 = ref(null)
const password2 = ref(null)

const router = useRouter()
const store = useMovieStore()
store.initialize(router)

const signUp = function () {
  const payload = {
    username: username.value,
    password1: password1.value,
    password2: password2.value
  }
  store.signUp(payload)
}

</script>

<style scoped>
.signup-container {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: radial-gradient(circle at 50% 30%, #2f3b5a 0%, #1a1d29 45%);
  padding-top: 18vh;
  animation: fadeIn 0.8s ease-out forwards;
}

.signup-box {
  background: #1e2230;
  padding: 40px;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
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

.form-group:nth-child(3) {
  animation-delay: 0.5s;
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
  color: #989898;
}

input:focus {
  outline: none;
  border-color: #0072d2;
  background: #31343e;
}

.signup-btn {
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
  animation-delay: 0.6s;
}

.signup-btn:hover {
  background: #0066bd;
  transform: translateY(-1px);
}

.login-link {
  color: #cacaca;
  margin-top: 24px;
  font-size: 14px;
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
  animation-delay: 0.7s;
}

.login-link a {
  color: #0072d2;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 600;
}

.login-link a:hover {
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