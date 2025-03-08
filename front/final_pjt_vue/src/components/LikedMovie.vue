<template>
  <div class="section-container">
    <h2>내가 찜한 영화</h2>
    <div class="movie-grid" v-if="likedMovies.length">
      <MovieCard 
        v-for="movie in displayedMovies" 
        :key="movie.id" 
        :movie="movie"
      />
    </div>
    <p v-else class="empty-message">아직 찜한 영화가 없습니다.</p>

    <button 
      v-if="!showAll && likedMovies.length > initialDisplayCount" 
      @click="showAll = true" 
      class="show-more-btn"
    >
      더보기
    </button>
    <button 
      v-if="showAll && likedMovies.length > initialDisplayCount" 
      @click="showAll = false" 
      class="show-less-btn"
    >
      접기
    </button>
  </div>
</template>

<script setup>
import MovieCard from '@/components/MovieCard.vue'
import { ref, computed } from 'vue'

const props = defineProps({
  likedMovies: {
    type: Array,
    required: true
  }
})

const initialDisplayCount = 8 // 처음에 보여줄 영화 개수
const showAll = ref(false)

const displayedMovies = computed(() => {
  return showAll.value ? props.likedMovies : props.likedMovies.slice(0, initialDisplayCount)
})
</script>

<style scoped>
.section-container {
  margin: 4rem 0;
}

.section-container h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 2rem;
  text-align: center;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 한 줄에 4개씩 */
  gap: 2rem;
  padding: 1rem;
  margin-bottom: 2rem;
}

.empty-message {
  text-align: center;
  color: #666;
  font-size: 1.1rem;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.show-more-btn, .show-less-btn {
  display: block;
  width: 100%;
  max-width: 200px;
  margin: 2rem auto 0;
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
@media (max-width: 1200px) {
  .movie-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .movie-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .movie-grid {
    grid-template-columns: 1fr;
  }
}
</style>