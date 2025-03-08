<template>
  <div class="movie-card">
    
    <div class="poster-container">
      <img :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`" :alt="movie.title" class="movie-poster">
      <div v-if="movie.adult" class="adult-badge"></div>
      <div v-if="movie.is_playing" class="playing-badge">
        <svg class="camera-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
          <path d="M4 4h10a2 2 0 0 1 2 2v3.382l4-2.667V17.285l-4-2.667V18a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>
        </svg>
        <span class="now-text">NOW</span>
      </div>
      <div class="overlay">
        <p class="overview">{{ movie.overview }}</p>
        <button class="detail-btn" @click="goDetail">상세보기</button>
      </div>
    </div>

    <div class="movie-info">
      <div class="title-container">
        <h2 class="movie-title">{{ movie.title }}</h2>
        <span v-if="movie.is_playing" class="title-playing-badge">상영중</span>
      </div>
      <div class="movie-meta">
        <span class="rating">⭐ {{ movie.vote_average.toFixed(1) }}</span>
        <span class="runtime">🕒 {{ movie.runtime }}분</span>
        <span class="like-count">❤️ {{ movie.like_users.length }}</span>
      </div>
      <div class="genres">
        <span v-for="genre in movie.genre_ids" :key="genre.id" class="genre-tag">
          {{ genre.name }}
        </span>
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
  }
})

const goDetail = () => {
  router.push({ name: 'MovieDetailView', params: { movieId: props.movie.id }})
}
</script>

<style scoped>
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

.movie-card {
  background: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  opacity: 0;
  animation: fadeInUp 0.8s ease forwards;
}

.movie-card:nth-child(1) { animation-delay: 0.1s; }
.movie-card:nth-child(2) { animation-delay: 0.2s; }
.movie-card:nth-child(3) { animation-delay: 0.3s; }
.movie-card:nth-child(4) { animation-delay: 0.4s; }
.movie-card:nth-child(5) { animation-delay: 0.5s; }
.movie-card:nth-child(6) { animation-delay: 0.6s; }
.movie-card:nth-child(7) { animation-delay: 0.7s; }

.movie-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.poster-container {
  position: relative;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 450px;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.poster-container:hover .overlay {
  opacity: 1;
}

.poster-container:hover .movie-poster {
  transform: scale(1.1);
}

.overview {
  color: white;
  font-size: 0.9rem;
  line-height: 1.6;
  text-align: center;
  margin-bottom: 1.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 6;
  line-clamp: 6; 
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.detail-btn {
  background: #42b883;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s ease;
}

.detail-btn:hover {
  background: #3aa876;
}

.movie-info {
  padding: 1.5rem;
}

.movie-title {
  font-size: 1.2rem;
  color: #2c3e50;
  margin: 0;
  padding: 0;
  font-weight: 600;
  display: inline;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.movie-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.genre-tag {
  background: #42b883;
  color: white;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
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

.title-container {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 1rem;
  width: 100%;
}

.title-playing-badge {
  background-color: #2671bc;
  color: white;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  height: 18px;
  margin-left:8px;
}
</style>