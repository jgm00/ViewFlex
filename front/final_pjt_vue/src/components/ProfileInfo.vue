<template>
  <div class="profile-header">
    <div class="profile-main">
      <div class="profile-left">
        <div class="profile-image-container">
          <img :src="profileImage" alt="프로필 이미지" class="profile-pic">
          <div v-if="store.username === userInfo.person.username" class="image-upload-overlay">
            <label for="profile-upload" class="upload-label">
              <span class="upload-icon">📷</span>
            </label>
            <input 
              type="file" 
              id="profile-upload" 
              accept="image/*"
              @change="handleImageUpload" 
              class="file-input"
            >
          </div>
        </div>
      </div>
      <div class="profile-right">
        <h2>{{ userInfo.person.username }}</h2>
        <div class="stats-section">
          <div class="stat-box">
            <span class="stat-number">{{ userInfo.person.liked_movies_count }}</span>
            <span class="stat-value">찜한 영화</span>
          </div>
          <div class="stat-box clickable" @click="showFollowingModal = true">
            <span class="stat-number">{{ userInfo.followings.length }}</span>
            <span class="stat-value">팔로잉</span>
          </div>
          <div class="stat-box clickable" @click="showFollowerModal = true">
            <span class="stat-number">{{ userInfo.followers.length }}</span>
            <span class="stat-value">팔로워</span>
          </div>
        </div>
        <button 
          v-if="store.isLogin && store.username !== userInfo.person.username"
          @click="$emit('follow')" 
          class="follow-button"
        >
          {{ userInfo.is_followed ? '팔로우 취소' : '팔로우' }}
        </button>
      </div>
    </div>
  </div>

  <!-- 팔로잉 모달 -->
  <div v-if="showFollowingModal" class="modal-overlay" @click="showFollowingModal = false">
    <div class="modal-content" @click.stop>
      <h2>팔로잉 목록</h2>
      <div class="modal-list">
        <div class="user-tags">
          <div 
            v-for="following in userInfo.followings" 
            :key="following.id"
            class="user-tag"
            @click="goToUserPage(following.username)"
          >
            {{ following.username }}
          </div>
        </div>
      </div>
      <button class="modal-close" @click="showFollowingModal = false">닫기</button>
    </div>
  </div>

  <!-- 팔로워 모달 -->
  <div v-if="showFollowerModal" class="modal-overlay" @click="showFollowerModal = false">
    <div class="modal-content" @click.stop>
      <h2>팔로워 목록</h2>
      <div class="modal-list">
        <div class="user-tags">
          <div 
            v-for="follower in userInfo.followers" 
            :key="follower.id"
            class="user-tag"
            @click="goToUserPage(follower.username)"
          >
            {{ follower.username }}
          </div>
        </div>
      </div>
      <button class="modal-close" @click="showFollowerModal = false">닫기</button>
    </div>
  </div>
</template>

<script setup>
import { useMovieStore } from '@/stores/movie'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import defaultProfile from '@/assets/default_profile.png'  // 기본 이미지 import

const router = useRouter()
const store = useMovieStore()
const showFollowingModal = ref(false)
const showFollowerModal = ref(false)

const props = defineProps({
  userInfo: {
    type: Object,
    required: true
  }
})

// computed 대신 ref 사용
const profileImage = ref(props.userInfo.person.profile_image || defaultProfile)

// 이미지 업로드 처리 수정
const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 파일 크기 체크 (5MB 제한)
  if (file.size > 5 * 1024 * 1024) {
    alert('파일 크기는 5MB 이하여야 합니다.')
    return
  }

  // 이미지 파일 형식 체크
  if (!file.type.startsWith('image/')) {
    alert('이미지 파일만 업로드 가능합니다.')
    return
  }

  const formData = new FormData()
  formData.append('profile_image', file)

  try {
    const response = await axios({
      method: 'put',
      url: `${store.API_URL}/users/${store.username}/profile/image/`,
      headers: {
        'Authorization': `Token ${store.token}`,
        'Content-Type': 'multipart/form-data'
      },
      data: formData
    })

    // 서버 응답에서 이미지 URL을 받아서 업데이트
    if (response.data && response.data.profile_image) {
      profileImage.value = response.data.profile_image
      props.userInfo.person.profile_image = response.data.profile_image
    } else {
      // 서버에서 URL을 받지 못한 경우 임시 URL 생성
      const tempUrl = URL.createObjectURL(file)
      profileImage.value = tempUrl
      props.userInfo.person.profile_image = tempUrl
    }
    
    alert('프로필 이미지가 변경되었습니다.')
  } catch (error) {
    console.error('이미지 업로드 실패:', error)
    alert('이미지 업로드에 실패했습니다.')
  }
}

const goToUserPage = (username) => {
  router.push({ name: 'MyPageView', params: { username: username }})
  showFollowingModal.value = false
  showFollowerModal.value = false
}


</script>

<style scoped>
.profile-header {
  padding: 2rem;
  background: rgb(26, 29, 41);
  border-radius: 15px;
}

.profile-main {
  display: flex;
  align-items: flex-start;
  gap: 4rem;
  padding: 0 2rem;
}

.profile-left {
  flex-shrink: 0;
}

.profile-right {
  flex-grow: 1;
}

.profile-image-container {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
}

.image-upload-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  /* background: rgba(0, 0, 0, 0.6); */
  background: white;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.profile-image-container:hover .image-upload-overlay {
  opacity: 1;
}

.upload-label {
  cursor: pointer;
  color: white;
  padding: 5px;
}

.upload-icon {
  font-size: 1.5rem;
}

.file-input {
  display: none;
}

.profile-pic {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.profile-image-container:hover .profile-pic {
  transform: scale(1.05);
}

h2 {
  font-size: 1.5rem;
  margin: 0 0 1.5rem 0;
  color: white;
}

.stats-section {
  display: flex;
  gap: 3rem;
  margin-bottom: 1.5rem;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.stat-value {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.stat-number {
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
}

.stat-box.clickable {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.stat-box.clickable:hover {
  transform: translateY(-2px);
}

.follow-button {
  padding: 0.8rem 2rem;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: white;
}

/* 팔로우 버튼 (기본 상태) */
.follow-button:not(.liked) {
  background: rgba(37, 99, 235, 0.85); /* 파란색 */
}

/* 팔로우 취소 버튼 */
.follow-button.liked,
.follow-button:has(span:contains('팔로우 취소')) {
  background: rgba(220, 38, 38, 0.85) !important; /* 빨간색 */
}

/* 호버 효과 - 팔로우 */
.follow-button:not(.liked):hover {
  background: rgba(59, 130, 246, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
}

/* 호버 효과 - 팔로우 취소 */
.follow-button.liked:hover,
.follow-button:has(span:contains('팔로우 취소')):hover {
  background: rgba(239, 68, 68, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 38, 38, 0.3);
}

/* 클릭 효과 */
.follow-button:active {
  transform: translateY(1px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .profile-main {
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    padding: 0;
  }

  .profile-right {
    width: 100%;
    text-align: center;
  }

  .stats-section {
    justify-content: center;
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: linear-gradient(135deg, 
    rgb(26, 29, 41) 0%,
    rgb(30, 34, 47) 100%
  );
  color: white;
  padding: 2.5rem;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideUp 0.4s ease;
  position: relative;
}

.modal-content h2 {
  font-size: 1.8rem;
  margin-bottom: 2rem;
  color: white;
  text-align: center;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.modal-list {
  margin: 1.5rem 0;
}

.user-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.user-tag {
  background: rgba(37, 99, 235, 0.2);
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(4px);
  font-weight: 500;
  font-size: 0.95rem;
  letter-spacing: 0.3px;
}

.user-tag:hover {
  background: rgba(37, 99, 235, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

.modal-close {
  width: 100%;
  padding: 1rem;
  background: rgba(37, 99, 235, 0.8);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 1rem;
  margin-top: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-close:hover {
  background: rgba(59, 130, 246, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

.modal-close:active {
  transform: translateY(1px);
}

/* 스크롤바 스타일링 */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 애니메이션 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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

/* 모바일 대응 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    padding: 2rem;
  }

  .modal-content h2 {
    font-size: 1.5rem;
  }

  .user-tag {
    padding: 0.7rem 1.2rem;
    font-size: 0.9rem;
  }
}
</style>