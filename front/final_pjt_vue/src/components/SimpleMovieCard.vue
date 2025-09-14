<template>
  <div class="movie-card" @click="goDetail">
    <div v-if="rank" class="rank-number">{{ rank }}</div>
    <div v-if="movie.adult" class="adult-badge"></div>
    <div v-if="movie.is_playing" class="playing-badge">
      <svg class="camera-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
        <path d="M4 4h10a2 2 0 0 1 2 2v3.382l4-2.667V17.285l-4-2.667V18a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>
      </svg>
      <span class="now-text">NOW</span>
    </div>
    <img 
      :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`" 
      :alt="movie.title" 
      class="movie-poster"
    >
    <div class="overlay">
      <h3 class="movie-title">{{ movie.title }}</h3>
      <div class="movie-info">
        <span class="rating">⭐ {{ formatRating(movie.vote_average) }}</span>
        <span v-if="movie.is_playing" class="now-playing">상영중</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const props = defineProps({
  movie: {
    type: Object,
    required: true
  },
  rank: {
    type: Number,
    default: null
  }
})

const formatRating = (rating) => {
  return rating ? rating.toFixed(1) : '0.0'
}

const goDetail = () => {
  if (props.movie && props.movie.id) {
    router.push({ 
      name: 'MovieDetailView', 
      params: { movieId: props.movie.id }
    })
  } else {
    console.warn('Movie ID is missing')
  }
}
</script>

<style scoped>
.movie-card {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .movie-poster {
  transform: scale(1.05);
}

.overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1.5rem 1rem;
  background: linear-gradient(to top, 
    rgba(0, 0, 0, 0.95), 
    rgba(0, 0, 0, 0.8), 
    rgba(0, 0, 0, 0.4));
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.movie-card:hover .overlay {
  transform: translateY(0);
}

.movie-title {
  color: white;
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
  font-weight: 600;
}

.movie-info {
  display: flex;
  justify-content: center;
  gap: 1rem;
  font-size: 0.9rem;
  color: #fff;
}

.now-playing {
  color: #4ecca3;
  font-weight: 700;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}

.rating {
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
  font-weight: 600;
}

.rank-number {
  position: absolute;
  top: -15px;
  left: -15px;
  width: 40px;
  height: 40px;
  background: linear-gradient(45deg, #333333, #000000);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  z-index: 2;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.adult-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 40px;
  height: 40px;
  background-color: #d32f2f;
  border-radius: 6px;
  z-index: 2;
  box-shadow: 0 3px 6px rgba(0,0,0,0.3);
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><text x="50%" y="50%" font-family="Arial" font-size="18" font-weight="bold" text-anchor="middle" dy=".35em">19</text></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.playing-badge {
  position: absolute;
  top: 15px;
  left: 15px;
  background-color: #2671BC;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: bold;
  z-index: 2;
  box-shadow: 0 3px 6px rgba(0,0,0,0.3);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.5px;
}

.camera-icon {
  filter: drop-shadow(0 0 1px rgba(255, 255, 255, 0.5));
  color: #ffffff;
}

.now-text {
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
</style>