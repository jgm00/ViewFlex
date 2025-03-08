<template>
  <div class="review-list">
    <div class="review-header">
      <h1>리뷰 목록</h1>
      <span class="review-count">총 {{ store.reviews.length }}개의 리뷰</span>
    </div>
    <div v-if="reviews.length > 0">
      <div v-for="(review, index) in reviews" :key="index" class="review-item">
        <!-- 수정 모드일 때 -->
        <div v-if="editingReview === review.id" class="edit-form">
          <div class="rating-section">
            <label class="rating-label">평점</label>
            <div class="star-rating">
              <div v-for="n in 5" :key="n" class="star">
                <i 
                  class="fas fa-star-half"
                  :class="{ 
                    'active': (n * 2 - 1) <= editRating * 2,
                    'hover': (n * 2 - 1) <= hoverRating * 2
                  }"
                  @mouseover="hoverRating = (n * 2 - 1) / 2"
                  @mouseleave="hoverRating = 0"
                  @click="editRating = (n * 2 - 1) / 2"
                ></i>
                <i 
                  class="fas fa-star-half fa-flip-horizontal"
                  :class="{ 
                    'active': (n * 2) <= editRating * 2,
                    'hover': (n * 2) <= hoverRating * 2
                  }"
                  @mouseover="hoverRating = n"
                  @mouseleave="hoverRating = 0"
                  @click="editRating = n"
                ></i>
              </div>
              <span v-if="editRating" class="rating-text">
                {{ formatRating(editRating) }}점
              </span>
            </div>
          </div>
          <div class="editor-wrapper">
            <div class="editor-container">
              <textarea 
                v-model="editContent" 
                class="edit-textarea"
                maxlength="500"
              ></textarea>
            </div>
            <div class="editor-footer">
              <span class="char-count">{{ editContent.length }}/500</span>
            </div>
          </div>
          <div class="button-group">
            <button @click="updateReview(review.id)" class="btn-save">저장</button>
            <button @click="cancelEdit" class="btn-cancel">취소</button>
          </div>
        </div>
        <!-- 일반 모드일 때 -->
        <div v-else>
          <div class="review-header-content">
            <div class="star-display">
              <div v-for="n in 5" :key="n" class="star">
                <i 
                  class="fas fa-star-half"
                  :class="{ 'active': (n * 2 - 1) <= review.rating * 2 }"
                ></i>
                <i 
                  class="fas fa-star-half fa-flip-horizontal"
                  :class="{ 'active': (n * 2) <= review.rating * 2 }"
                ></i>
              </div>
              <span class="rating-number">({{ review.rating }}점)</span>
            </div>
          </div>
          <p>{{ review.content }}</p>
          <div class="review-footer">
            <div
              class="review-info"
              @click="openUserModal(review.user_username)"
            >
              작성자: <span class="username">{{ review.user_username }}</span>
            </div>
            <span class="review-date">{{ formatDate(review.created_at) }}</span>
              <div v-if="isCurrentUser(review.user_username)" class="action-buttons">
                <button @click="startEdit(review)" class="btn-edit">수정</button>
                <button @click="deleteReview(review.id)" class="btn-delete">삭제</button>
              </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <p>등록된 리뷰가 없습니다.</p>
    </div>
    <div v-if="showUserModal" class="user-modal-overlay" @click="closeUserModal">
      <div class="user-modal" @click.stop>
        <button class="modal-close-btn" @click="closeUserModal">
          <i class="fas fa-times"></i>
        </button>
        <div class="modal-content">
          <div class="user-profile">
            <i class="fas fa-user-circle profile-icon"></i>
            <h2>{{ selectedUsername }}</h2>
          </div>
          <div class="modal-buttons">
            <button class="btn-profile" @click="goToUserPage">
              <i class="fas fa-user"></i>
              프로필 보기
            </button>
            <button 
              v-if="selectedUsername && selectedUsername !== store.username"
              class="btn-follow"
              :class="{ 'following': isFollowing }"
              @click="handleFollow"
            >
              <i :class="isFollowing ? 'fas fa-user-minus' : 'fas fa-user-plus'"></i>
              {{ isFollowing ? '팔로우 취소' : '팔로우' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMovieStore } from '@/stores/movie'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const store = useMovieStore()
const route = useRoute()
const router = useRouter()
const props = defineProps({
  movieId: {
    type: String,
  },
  reviews: {
    type: Object
  }
})

// 수정 관련 상태 관리
const editingReview = ref(null)
const editContent = ref('')
const editRating = ref(0)
const hoverRating = ref(0)
const showUserModal = ref(false)
const selectedUsername = ref('')
const isFollowing = ref(false)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 현재 로그인한 사용자의 리뷰인지 확인
const isCurrentUser = (reviewUsername) => {
  if (!store.username) return false
  return reviewUsername === store.username
}

// 수정 모드 시작
const startEdit = (review) => {
  editingReview.value = review.id
  editContent.value = review.content
  editRating.value = review.rating
}

// 수정 취소
const cancelEdit = () => {
  editingReview.value = null
  editContent.value = ''
  editRating.value = 0
  hoverRating.value = 0
}

// 리뷰 수정
const updateReview = async (reviewId) => {
  try {
    const response = await axios.put(
      `${store.API_URL}/movies/reviews/${reviewId}/`,
      { 
        content: editContent.value,
        rating: (Math.round(editRating.value * 2) / 2).toFixed(1)
      },
      {
        headers: {
          Authorization: `Token ${store.token}`
        }
      }
    )
    await store.getReview(props.movieId)
    editingReview.value = null
    editContent.value = ''
    editRating.value = 0
  } catch (error) {
    console.error('리뷰 수정 실패:', error)
  }
}

const formatRating = (value) => {
  return value % 1 === 0 ? value.toFixed(0) : value.toFixed(1)
}

// 리뷰 삭제
const deleteReview = async (reviewId) => {
  if (!confirm('정말로 이 리뷰를 삭제하시겠습니까?')) return

  try {
    await axios.delete(
      `${store.API_URL}/movies/reviews/${reviewId}/`,
      { 
        headers: {
          Authorization: `Token ${store.token}`
        }
      }
    )
    // 리뷰 목록 갱신 - fetchReviews 대신 getReview 사용
    await store.getReview(props.movieId)
  } catch (error) {
    console.error('리뷰 삭제 실패:', error)
  }
}

const checkFollowStatus = async (username) => {
  try {
    const response = await axios({
      method: 'get',
      url: `${store.API_URL}/users/${username}/mypage/`,
      headers: {
        Authorization: `Token ${store.token}`
      }
    })
    isFollowing.value = response.data.is_followed
  } catch (error) {
    console.error('팔로우 상태 확인 실패:', error)
  }
}

const openUserModal = async (username) => {
  if (!store.token) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }
  selectedUsername.value = username
  showUserModal.value = true
  if (username !== store.username) {
    await checkFollowStatus(username)
  }
}

const handleFollow = async () => {
  if (!store.token) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }

  try {
    const response = await axios({
      method: 'post',
      url: `${store.API_URL}/users/${selectedUsername.value}/follow/`,
      headers: {
        Authorization: `Token ${store.token}`
      }
    })
    
    // 팔로우 상태 업데이트
    isFollowing.value = response.data.is_followed
    
    // 팔로우 상태에 따른 알림 메시지 표시
    if (response.data.is_followed) {
      alert(`${selectedUsername.value}님을 팔로우했습니다.`)
    } else {
      alert(`${selectedUsername.value}님을 팔로우 취소했습니다.`)
    }
    
  } catch (error) {
    console.error('팔로우 처리 실패:', error)
    alert('팔로우 처리 중 오류가 발생했습니다.')
  }
}

const closeUserModal = () => {
  showUserModal.value = false
  selectedUsername.value = ''
  isFollowing.value = false
}

const goToUserPage = () => {
  router.push(`/${selectedUsername.value}/mypage`)
  closeUserModal()
}

const loadMoreReviews = () => {
}
</script>

<style scoped>
.review-list {
  max-width: 816px;
  max-height: 840px;
  margin: 2rem auto;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.068);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.review-header {
  position: relative;
  text-align: center;
  margin-bottom: 1.5rem;
  padding: 0 1rem 1rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.review-header h1 {
  margin: 0;
  font-size: 1.8rem;
  color: white;
  display: inline-block;
}

.review-count {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  padding: 0.4rem 0.8rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.review-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.review-item:last-child {
  margin-bottom: 0;
}

.review-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 스크롤바 스타일링 */
.review-list::-webkit-scrollbar {
  width: 8px;
}

.review-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  margin: 8px;
}

.review-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.review-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .review-list {
    max-height: 600px;
    padding: 15px;
  }

  .review-item {
    padding: 1rem;
  }

  .review-header h1 {
    font-size: 1.5rem;
  }

  .review-count {
    font-size: 0.8rem;
    padding: 0.3rem 0.6rem;
  }
}

.review-info {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  cursor: pointer;
}

.username {
  color: #0072d2;
  transition: color 0.2s ease;
}

.username:hover {
  color: #0086f9;
}

.review-info:hover {
  color: #00bcd4; /* 마우스 오버 시 텍스트 색상 변경 */
  background-color: rgba(0, 0, 0, 0.1); /* 배경색 변경 */
}

.review-info span {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  font-weight: 500;
}

.review-date {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
}

p {
  color: #ffffff;
  line-height: 1.6;
  margin: 1rem 0;
  font-size: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.btn-edit,
.btn-save,
.btn-delete,
.btn-cancel {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-edit,
.btn-save {
  background: #0072d2;
  color: white;
}

.btn-delete {
  background: rgba(244, 67, 54, 0.1);
  color: #ff5252;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.edit-form {
  width: 100%;
  margin: 0 auto;
}

.editor-wrapper {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.editor-container {
  padding: 0 2rem;
}

.edit-textarea {
  width: 100%;
  height: 120px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ffffff;
  padding: 1.5rem 2rem;
  resize: none;
  font-size: 1rem;
  line-height: 1.5;
  box-sizing: border-box;
}

.editor-footer {
  padding: 0.5rem 2rem;
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.char-count {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 0 2rem;
}

.btn-save,
.btn-cancel {
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-save {
  background: #0072d2;
  color: white;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.star-display {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.star-display .star {
  display: inline-flex;
  font-size: 1.2rem;
}

.star-display i {
  color: rgba(255, 255, 255, 0.2);
  width: 0.6rem;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

.star-display i.active {
  color: #ffd700;
}

.star-display .star + .star {
  margin-left: -2px;  /* 별과 별 사이 간격 조정 */
}

.rating-number {
  margin-left: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.rating-section {
  text-align: center;
  margin-bottom: 1.5rem;
}

.rating-label {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
}

.star-rating {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.star-rating .star {
  display: inline-flex;
  font-size: 2.2rem;
}

.star-rating i {
  color: rgba(255, 255, 255, 0.2);
  width: 1.1rem;
  overflow: hidden;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 0;
  margin: 0;
}

.star-rating .star + .star {
  margin-left: -2px;  /* 별과 별 사이 간격 조정 */
}

.star-rating i.active,
.star-rating i.hover {
  color: #ffd700;
}

.rating-text {
  position: absolute;
  right: 30%;
  margin-left: 1rem;
  color: rgba(255, 255, 255, 0.9);
}

.user-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.user-modal {
  background: #1a1d29;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 400px;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.modal-close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s ease;
}

.modal-close-btn:hover {
  color: white;
}

.user-profile {
  text-align: center;
  margin-bottom: 2rem;
}

.profile-icon {
  font-size: 4rem;
  color: #0072d2;
  margin-bottom: 1rem;
}

.user-profile h2 {
  color: white;
  font-size: 1.5rem;
  margin: 0;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-profile,
.btn-follow {
  padding: 0.8rem 1.5rem;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.btn-profile {
  background: #0072d2;
  color: white;
}

.btn-profile:hover {
  background: #0086f9;
  transform: translateY(-2px);
}

.btn-follow {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-follow:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.btn-follow.following {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
}

.btn-follow.following:hover {
  background: rgba(244, 67, 54, 0.1);
  color: #ff5252;
}

.btn-follow.following:hover i {
  color: #ff5252;
}

.review-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
}

.load-more-reviews {
  width: 100%;
  max-width: 300px;
  margin: 2rem auto;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  letter-spacing: 0.3px;
  position: relative;
  overflow: hidden;
}

.load-more-reviews::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.load-more-reviews:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.load-more-reviews:hover::before {
  transform: translateX(100%);
}

.load-more-reviews:active {
  transform: translateY(1px);
}
</style>