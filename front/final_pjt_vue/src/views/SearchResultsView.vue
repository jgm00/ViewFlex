<template>
  <div class="search-results">
    <h1 class="title">검색 결과: "{{ $route.query.q }}"</h1>
    
    <div v-if="store.isLoading" class="loading">
      Loading...
    </div>
    <div v-else>
      <div v-if="store.searchResults.length" class="movie-grid">
        <MovieCard 
          v-for="movie in store.searchResults" 
          :key="movie.id" 
          :movie="movie"
          v-lazy-load
        />
      </div>
      <div v-else class="no-results">
        검색 결과가 없습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { useMovieStore } from '@/stores/movie'
import MovieCard from '@/components/MovieCard.vue'

const store = useMovieStore()
</script>

<style scoped>
.search-results {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.title {
  font-size: 2rem;
  color: #f9f9f9;
  text-align: center;
  margin-bottom: 2rem;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.no-results {
  text-align: center;
  color: #f9f9f9;
  font-size: 1.2rem;
  padding: 2rem;
}

.loading {
  text-align: center;
  color: #f9f9f9;
  font-size: 1.2rem;
  padding: 2rem;
}
</style>