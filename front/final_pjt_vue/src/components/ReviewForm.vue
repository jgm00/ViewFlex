<template>
  <div class="review-form">
    <div class="review-header">
      <h3>리뷰 작성</h3>
      <!-- <span class="review-count">(총 {{ store.reviews.length }}개의 리뷰)</span> -->
    </div>
    <div class="form-content">
      <div class="rating-section">
        <label class="rating-label">평점</label>
        <div class="star-rating">
          <div v-for="n in 5" :key="n" class="star">
            <i 
              class="fas fa-star-half"
              :class="{ 
                'active': (n * 2 - 1) <= rating * 2,
                'hover': (n * 2 - 1) <= hoverRating * 2
              }"
              @mouseover="hoverRating = (n * 2 - 1) / 2"
              @mouseleave="hoverRating = 0"
              @click="rating = (n * 2 - 1) / 2"
            ></i>
            <i 
              class="fas fa-star-half fa-flip-horizontal"
              :class="{ 
                'active': (n * 2) <= rating * 2,
                'hover': (n * 2) <= hoverRating * 2
              }"
              @mouseover="hoverRating = n"
              @mouseleave="hoverRating = 0"
              @click="rating = n"
            ></i>
          </div>
          <span v-if="rating" class="rating-text">
            {{ formatRating(rating) }}점
          </span>
        </div>
      </div>
      
      <div class="content-section">
        <!-- <label>리뷰 내용</label> -->
        <div class="editor-wrapper">
          <div class="editor-container">
            <textarea 
              v-model="reviewContent" 
              placeholder="영화에 대한 솔직한 리뷰를 남겨주세요."
              class="review-editor"
              :class="{ 'has-content': reviewContent.length > 0 }"
              maxlength="500"
            ></textarea>
          </div>
          <div class="editor-footer">
            <button 
              class="submit-btn"
              @click="submitReview"
            >
              리뷰 등록하기
            </button>
            <span class="char-count">{{ reviewContent.length }}/500</span>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMovieStore } from '@/stores/movie'
import axios from 'axios'

const props = defineProps({
  movieId: {
    type: String,
    required: true
  }
})

const store = useMovieStore()
const rating = ref(0)
const hoverRating = ref(0)
const reviewContent = ref('')

const submitReview = () => {
  if (!store.token) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }

  if (!rating.value || !reviewContent.value.trim()) {
    alert('별점과 리뷰 내용을 모두 입력해주세요.')
    return
  }

  axios({
    method: 'post',
    url: `${store.API_URL}/movies/${props.movieId}/reviews/`,
    data: {
      rating: (Math.round(rating.value * 2) / 2).toFixed(1),
      content: reviewContent.value,
      movie: props.movieId
    },
    headers: {
      Authorization: `Token ${store.token}`
    }
  }).then(() => {
    rating.value = 0
    reviewContent.value = ''
    alert('리뷰가 등록되었습니다.')
    store.getReview(props.movieId)
  }).catch((err) => {
    if (err.response?.status === 401) {
      alert('로그인이 필요하거나 세션이 만료되었습니다.')
    } else {
      alert('리뷰 등록에 실패했습니다.')
    }
    console.error(err)
  })
}

const isValid = computed(() => {
  return rating.value > 0 && reviewContent.value.trim().length > 0
})

const formatRating = (value) => {
  return value % 1 === 0 ? value.toFixed(0) : value.toFixed(1);
}
</script>

<style scoped>
.review-form {
  max-width: 800px;
  max-height: 400px;
  margin: 2rem auto;
  padding: 1.2rem;
  background: rgba(255, 255, 255, 0.068);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.review-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  width: 90%;
  margin-left: auto;
  margin-right: auto;
}

h3 {
  color: #ffffff;
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
}

.review-count {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  position: absolute;
  right: 0;
  top: 7.5%;
  right: 8%;
  transform: translateY(-40%);
}

.rating-label, 
.content-section label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 1.1rem;
  margin-bottom: 1rem;
  display: block;
}

.rating-section {
  text-align: center;
  margin-bottom: 1.5rem;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rating-label {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
}

.star-rating {
  display: inline-flex;
  align-items: center;
  position: relative;
  justify-content: center;
  width: 100%;
  padding: 0 3rem;
}

.star {
  display: inline-flex;
  font-size: 2.2rem;
  line-height: 1;
  margin: 0;
  padding: 0;
}

.star i {
  color: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: color 0.2s ease;
  margin: 0;
  padding: 0;
  width: 1.1rem;  /* 반쪽 별의 너비를 정확히 절반으로 */
  overflow: hidden;
}

.star i.active,
.star i.hover {
  color: #ffd700;
}

.rating-text {
  position: absolute;
  right: 36%;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 1rem;
  white-space: nowrap;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.review-editor {
  width: 100%;
  height: 150px;  /* 고정 높이 설정 */
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ffffff;
  padding: 1.5rem 2rem;  /* 내부 여백 수정 */
  resize: none;  /* 크기 조절 비활성화 */
  font-size: 1rem;
  line-height: 1.5;
  box-sizing: border-box;  /* 추가 */
}

.editor-footer {
  display: grid;  /* flex에서 grid로 변경 */
  grid-template-columns: 1fr auto 1fr;  /* 3등분 그리드 */
  align-items: center;
  padding: 0.5rem 2rem;
  margin-top: 1rem;
  position: relative;  /* 추가 */
}

.submit-btn {
  grid-column: 2;  /* 가운데 열에 배치 */
  background: linear-gradient(to right, #0072d2, #0086f9);
  color: white;
  font-weight: 500;
  padding: 0.6rem 1.5rem;
  border-radius: 20px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  min-width: 100px;
  justify-self: center;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 114, 210, 0.4);
  background: linear-gradient(to right, #0086f9, #0098ff);
}

.char-count {
  grid-column: 3;  /* 마지막 열에 배치 */
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin: 0;
  justify-self: end;  /* 오른쪽 정렬 */
}

.button-container {
  text-align: center;
  margin-top: 2rem;
}

.content-section {
  text-align: center;  /* 추가 */
  width: 100%;  /* 추가 */
  margin-bottom: 1rem;  /* 추가 */
}

.content-section label {
  color: #ffffff;  /* 더 밝은 흰색으로 변경 */
  font-weight: 500;
  margin-bottom: 1rem;
  display: block;
  text-align: center;  /* 추가 */
}

.editor-wrapper {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;  /* 중앙 정렬 */
}

.editor-container {
  padding: 0 2rem;  /* 좌우 여백 추가 */
}

/* 반응형 디자인 추가 */
@media (max-width: 768px) {
  .editor-footer {
    padding: 0.5rem 1rem;
    grid-template-columns: 1fr auto 1fr;  /* 비율 유지 */
  }
  
  .submit-btn {
    padding: 0.5rem 1.2rem;
    font-size: 0.85rem;
  }
}
</style>