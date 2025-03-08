<template>
  <div class="reviews-container">
    <div class="reviews-header">
      <h2>작성한 리뷰</h2>
      <span class="review-count">(총 {{ reviews.length }}개의 리뷰)</span>
    </div>
    
    <div v-if="reviews.length > 0">
      <div class="reviews-list">
        <div v-for="(review, index) in displayedReviews" 
             :key="review.id" 
             class="review-card" 
             @click="goToMovieDetail(review.movie__id)"
        >
          <div class="review-header">
            <h3>{{ review.movie__title }}</h3>
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
          <div class="review-content-wrapper">
            <p class="review-content">{{ review.content }}</p>
            <span class="review-date">{{ formatDate(review.created_at) }}</span>
          </div>
          <div class="hover-overlay">
            <span class="click-text">영화 상세보기</span>
            <i class="fas fa-arrow-right"></i>
          </div>
        </div>
      </div>
      
      <button 
        v-if="!showAll && reviews.length > initialDisplayCount" 
        @click="showAll = true" 
        class="show-more-btn"
      >
        더보기 ({{ reviews.length - initialDisplayCount }}개 더보기)
      </button>
      <button 
        v-if="showAll && reviews.length > initialDisplayCount" 
        @click="showAll = false" 
        class="show-less-btn"
      >
        접기
      </button>
    </div>
    
    <div v-else class="no-reviews">
      <p>등록한 리뷰가 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  reviews: {
    type: Array,
    required: true
  }
})

const initialDisplayCount = 3 // 처음에 보여줄 리뷰 개수
const showAll = ref(false)

const displayedReviews = computed(() => {
  const firstReview = props.reviews[0]
  console.log('All review properties:', Object.keys(firstReview))
  console.log('Complete review object:', firstReview)
  return showAll.value ? props.reviews : props.reviews.slice(0, initialDisplayCount)
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const goToMovieDetail = (movieId) => {
  router.push(`/movie/${movieId}`)
}
</script>

<style scoped>
.reviews-header {
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
}

.reviews-header h2 {
  margin: 0;
}

.review-count {
  color: #888;
  font-size: 0.9rem;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.review-header h3 {
  margin: 0;
  flex: 1;
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
  color: rgba(0, 0, 0, 0.2);  /* 배경이 밝은색이므로 어두운 색으로 변경 */
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
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .review-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .star {
    font-size: 1rem;
  }

  .rating-container {
    width: 100%;
    justify-content: flex-end;
  }
}

.reviews-container {
  width: 100%;
  height: 100%;
  max-height: 800px;
  overflow-y: auto;
  overflow-x: hidden;
}

.reviews-list {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  padding-right: 5px;
  width: 100%;
  box-sizing: border-box;
}

/* 스크롤바 스타일링 */
.reviews-container::-webkit-scrollbar {
  width: 8px;
}

.reviews-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.reviews-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.reviews-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.review-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.review-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.review-header {
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: none;  /* 실선 제거 */
}

.review-header h3 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.review-content-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.review-content {
  flex: 1;
  color: #4a4a4a;
  margin: 0;
  line-height: 1.5;
  max-height: 4.5em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.review-date {
  color: #888;
  font-size: 0.85rem;
  white-space: nowrap;
}

.hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.review-card:hover .hover-overlay {
  opacity: 1;
}

.click-text {
  color: white;
  font-weight: 500;
}

.hover-overlay i {
  color: white;
  font-size: 1.2rem;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .reviews-list {
    grid-template-columns: 1fr;
  }

  .review-card {
    padding: 1rem;
  }
}

.show-more-btn, .show-less-btn {
  position: sticky;
  bottom: 0;
  margin-top: 1rem;
  background: rgba(49, 52, 62, 0.7);
  border: 2px solid rgba(249, 249, 249, 0.2);
  color: rgb(249, 249, 249);
  z-index: 1;  
}

.show-more-btn, .show-less-btn {
  width: 100%;
  padding: 0.8rem;
  margin-top: 1rem;
  background: rgba(49, 52, 62, 0.7);
  color: rgb(249, 249, 249);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.show-more-btn:hover, .show-less-btn:hover {
  background: rgba(58, 61, 72, 0.9);
  border-color: rgba(249, 249, 249, 0.3);
}

.show-less-btn {
  background: #666;
}

.show-less-btn:hover {
  background: #555;
}

.no-reviews {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-top: 1rem;
}
</style>