<template>
  
  <div v-if="store.movie" class="movie-detail">
    <MovieDetail :movie="store.movie" />
    <ReviewForm :movie-id="route.params.movieId" />
    <ReviewList 
        :movie-id="route.params.movieId"
        :reviews="store.reviews" />
  </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import axios from 'axios'
import ReviewForm from '@/components/ReviewForm.vue'
import MovieDetail from '@/components/MovieDetail.vue'
import ReviewList from '@/components/ReviewList.vue'


const route = useRoute()
const store = useMovieStore()

onMounted(() => {
  store.getMovieDetail(route.params.movieId)
  if (store.movie) {
    store.getReview(route.params.movieId)
  }
})
</script>

<style scoped>

/* 전체 컨테이너 */
.movie-detail {
  min-height: 100vh;
  background: rgb(26, 29, 41);
  animation: fadeInUp 0.8s ease-out forwards;
}

.movie-header {
  background-size: cover;
  background-position: center;
  position: relative;
  padding: 6rem 2rem;
  margin-bottom: 2rem;
}

.movie-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.6));
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .header-content {
    grid-template-columns: 300px 1fr;
    gap: 3rem;
  }

  .movie-info h1 {
    font-size: 2.8rem;
  }
}

@media (max-width: 768px) {
  .movie-header {
    padding: 4rem 1.5rem;
  }

  .header-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .poster {
    max-width: 300px;
    margin: 0 auto;
  }

  .movie-info h1 {
    font-size: 2.2rem;
    text-align: center;
  }

  .meta {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .genres {
    justify-content: center;
  }

  .overview {
    text-align: center;
  }

  .like-button {
    display: block;
    margin: 0 auto;
  }

  .form-header {
    flex-direction: column;
  }

  .review-card {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .movie-info h1 {
    font-size: 1.8rem;
  }

  .review-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .review-meta {
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
  }
}

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