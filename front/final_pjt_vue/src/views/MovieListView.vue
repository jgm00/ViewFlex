<template>
  <div class="movie-list-container">
    <h1 class="title">영화 목록</h1>
    
    <div class="search-section">
      <div class="search-input-group">
        <input
          v-show="isTagifyInitialized"
          ref="tagifyRef"
          placeholder="장르나 배우로 검색하세요 (액션, 톰 크루즈, ...)"
          @focus="showDropdown = true"
          @blur="handleBlur"
        >
        <div v-show="showDropdown" class="genre-dropdown">
          <div class="genre-items">
            <div 
              v-for="(name, id) in genreMap" 
              :key="id"
              class="genre-item"
              @mousedown.prevent="addGenreTag(name)"
            >
              {{ name }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="store.isLoading" class="loading">
      Loading...
    </div>
    <div v-else>
      <div class="movie-grid">
        <MovieCard 
          v-for="movie in filteredMovies" 
          :key="movie.id" 
          :movie="movie"
          v-lazy-load
        />
      </div>
      
      <!-- Show pagination only when total pages > 1 -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          &lt;
        </button>

        <div class="page-numbers">
          <button 
            class="page-btn"
            :class="{ active: currentPage === 1 }"
            @click="changePage(1)"
          >
            1
          </button>

          <template v-for="pageNum in displayedPages" :key="pageNum">
            <span v-if="pageNum === '...'" class="dots">...</span>
            <button 
              v-else-if="pageNum !== 1 && pageNum !== totalPages"
              class="page-btn"
              :class="{ active: currentPage === pageNum }"
              @click="changePage(pageNum)"
            >
              {{ pageNum }}
            </button>
          </template>

          <button 
            class="page-btn"
            :class="{ active: currentPage === totalPages }"
            @click="changePage(totalPages)"
          >
            {{ totalPages }}
          </button>
        </div>

        <button 
          class="page-btn" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          &gt;
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useMovieStore } from '@/stores/movie'
import MovieCard from '@/components/MovieCard.vue'
import Tagify from '@yaireo/tagify'
import '@yaireo/tagify/dist/tagify.css'
import axios from 'axios'

const store = useMovieStore()
const movies = ref([]) 
const currentPage = ref(1)
const itemsPerPage = 20
const pageCache = ref(new Map())  // 페이지 캐시 저장소

// 장르 ID와 이름 매핑
const genreMap = {
  28: '액션',
  12: '모험',
  16: '애니메이션',
  35: '코미디',
  80: '범죄',
  99: '다큐멘터리',
  18: '드라마',
  10751: '가족',
  14: '판타지',
  36: '역사',
  27: '공포',
  10402: '음악',
  9648: '미스터리',
  10749: '로맨스',
  878: 'SF',
  10770: 'TV 영화',
  53: '스릴러',
  10752: '전쟁',
  37: '서부'
};

// 장르 이름으로 ID 찾기
const getGenreId = (genreName) => {
  console.log('Looking up genre ID for:', genreName);
  console.log('Available genres:', genreMap);
  
  const entry = Object.entries(genreMap).find(([_, name]) => name === genreName);
  const id = entry ? Number(entry[0]) : null;
  
  console.log(`Genre "${genreName}" -> ID: ${id}`);
  return id;
};

// 장르 ID로 이름 찾기
const getGenreName = (genreId) => {
  return genreMap[genreId] || String(genreId);
};

const tagifyRef = ref(null)
const selectedTags = ref([])
const isSearching = ref(false)

// Tagify 인스턴스를 저장할 ref 추가
const tagifyInstance = ref(null);

// 드롭다운 표시 여부를 제어할 ref 추가
const showDropdown = ref(false);

// blur 이벤트 핸들러
const handleBlur = () => {
  // 약간의 지연을 주어 클릭 이벤트가 처리될 수 있도록 함
  setTimeout(() => {
    showDropdown.value = false;
  }, 200);
};

// 태그 변경 핸들러 수정
const handleTagChange = async (e) => {
  try {
    const tags = e.detail.tagify.value;
    selectedTags.value = tags;
    
    store.isLoading = true;
    
    // 헤더 설정을 조건부로 처리
    const headers = {};
    if (store.token) {
      headers.Authorization = `Token ${store.token}`;
    }

    // 르와 배우 태그 분리
    const genreTags = [];
    const actorTags = [];

    tags.forEach(tag => {
      const tagValue = tag.value.trim();  // 공백 제거
      const genreId = getGenreId(tagValue);
      if (genreId) {
        genreTags.push(genreId);
      } else {
        actorTags.push(tagValue);
      }
    });

    if (genreTags.length === 0 && actorTags.length === 0) {
      const response = await axios.get(`${store.API_URL}/movies/`, { headers });
      movies.value = response.data;
    } else {
      const searchParams = new URLSearchParams();
      if (genreTags.length) {
        searchParams.append('genre_ids', genreTags.join(','));
      }
      if (actorTags.length) {
        searchParams.append('actors', actorTags.join(','));
      }

      console.log('Search params:', searchParams.toString());  // 디버깅용

      const response = await axios.get(
        `${store.API_URL}/movies/filter/?${searchParams.toString()}`,
        { headers }
      );

      movies.value = response.data;
    }

    currentPage.value = 1;
    
  } catch (error) {
    console.error('Error in handleTagChange:', error);
  } finally {
    store.isLoading = false;
  }
};

// 이전/다음 페이지 프리로딩
const preloadAdjacentPages = async () => {
  const nextPage = currentPage.value + 1
  const prevPage = currentPage.value - 1

  if (nextPage <= totalPages.value && !pageCache.value.has(nextPage)) {
    const start = (nextPage - 1) * itemsPerPage
    const end = start + itemsPerPage
    pageCache.value.set(nextPage, store.movies.slice(start, end))
  }

  if (prevPage >= 1 && !pageCache.value.has(prevPage)) {
    const start = (prevPage - 1) * itemsPerPage
    const end = start + itemsPerPage
    pageCache.value.set(prevPage, store.movies.slice(start, end))
  }
}

// currentPageMovies computed
const currentPageMovies = computed(() => {
  if (!movies.value?.length) return [];  // 데이터가 없으면 빈 배열 반환

  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  
  // 캐시 확인
  const cachedPage = pageCache.value.get(currentPage.value);
  if (cachedPage) return cachedPage;

  // 새로운 페이지 데이터 생성 및 시
  const pageMovies = movies.value.slice(start, end);
  pageCache.value.set(currentPage.value, pageMovies);
  
  return pageMovies;
});

// totalPages computed 수정
const totalPages = computed(() => {
  if (!movies.value?.length) return 1;
  return Math.ceil(movies.value.length / itemsPerPage);
});

// displayedPages computed 추가
const displayedPages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const delta = 2;  // 현재 페이지 양쪽에 표시할 페이지 수
  
  let pages = [];
  
  // 항상 처음과 마지막 페이지는 표시
  if (total <= 7) {
    // 7페이지 이하면 모든 페이지 표시
    pages = Array.from({ length: total }, (_, i) => i + 1);
  } else {
    if (current <= 4) {
      // 현재 페이지가 앞쪽에 있 경우
      pages = [1, 2, 3, 4, 5, '...', total];
    } else if (current >= total - 3) {
      // 현재 페이지가 뒤쪽에 있는 경우
      pages = [1, '...', total - 4, total - 3, total - 2, total - 1, total];
    } else {
      // 현재 페이지가 중간에 있는 경우
      pages = [1, '...', current - 1, current, current + 1, '...', total];
    }
  }
  
  return pages;
});

// filteredMovies computed 수정
const filteredMovies = computed(() => {
  if (!movies.value?.length) return [];
  
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  
  return movies.value.slice(start, end);
});

// changePage 함수 수정
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    // URL 업데이트
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    window.history.pushState({}, '', url);

    // 부드러운 스크롤 애니메이션
    window.scrollTo({
      top: 0,
      behavior: 'smooth'  // 부드러운 스크롤 효과
    });
  }
};

// 검색 후 페이지 초기화
watch(movies, () => {
  currentPage.value = 1;
});

// URL 쿼리 파라미터로 페이지 관리
watch(currentPage, (newPage) => {
  const url = new URL(window.location)
  url.searchParams.set('page', newPage)
  window.history.pushState({}, '', url)
})

// 이미 레이 로딩을 위한 디렉티브
const vLazyLoad = {
  mounted: (el) => {
    function loadImage() {
      if (el.dataset.src) {
        el.src = el.dataset.src
        el.removeAttribute('data-src')
      }
    }

    function handleIntersect(entries, observer) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadImage()
          observer.unobserve(el)
        }
      })
    }

    const observer = new IntersectionObserver(handleIntersect)
    observer.observe(el)
  }
}

// 디티브 등록
const directives = {
  'lazy-load': vLazyLoad
}

// 장르 태그 추가 함수 수정
const addGenreTag = (genreName) => {
  if (tagifyInstance.value) {
    tagifyInstance.value.addTags([genreName]);
  }
};

const isTagifyInitialized = ref(false)

onMounted(async () => {
  try {
    store.isLoading = true;

    // 헤더 설정을 조건부로 처리
    const headers = {};
    if (store.token) {
      headers.Authorization = `Token ${store.token}`;
    }

    const response = await axios.get(`${store.API_URL}/movies/`, { headers });
    
    movies.value = response.data;
    store.movies = response.data;

    // Tagify 초기화 전에는 input이 보이지 않음
    await nextTick();
    
    // Tagify 초기화
    tagifyInstance.value = new Tagify(tagifyRef.value, {
      whitelist: Object.values(genreMap),
      enforceWhitelist: false,
      dropdown: {
        enabled: 0,
        maxItems: 1000,
        classname: "customSuggestionsList"
      }
    });

    // Tagify 초기화 완료 후 input 표시
    isTagifyInitialized.value = true;

    // 이벤트 리스너
    tagifyInstance.value.on('change', handleTagChange);

    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get('page')) || 1;
    currentPage.value = page;

    await nextTick();
    preloadAdjacentPages();
  } catch (error) {
    console.error('Error loading movies:', error);
  } finally {
    store.isLoading = false;
  }
});
</script>

<style scoped>
.movie-list-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  padding-top: 20px;
}

.title {
  font-size: 2.5rem;
  color: #f9f9f9;
  text-align: center;
  margin-bottom: 2rem;
  font-weight: 700;
  margin-top: 60px;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2.5rem;
  padding: 1rem;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
  margin-top: 2rem;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #f9f9f9;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 2rem 0;
  gap: 0.5rem;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #f9f9f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 40px;
  transform: scale(1);
  transition: all 0.2s ease;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.2);
}

.page-btn:not(:disabled):active {
  transform: scale(0.95);
}

.page-btn.active {
  background: #42b883;
  color: white;
  box-shadow: 0 0 10px rgba(66, 184, 131, 0.5);
}

.dots {
  padding: 0.5rem;
  color: #f9f9f9;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .title {
    font-size: 2rem;
  }

  .page-btn {
    padding: 0.4rem 0.8rem;
    min-width: 35px;
    font-size: 0.9rem;
  }
}

/* Add new styles */
.search-section {
  position: relative;
  z-index: 10;
  width: 50%;
  display: flex;
  justify-content: center;
  /* margin: 2rem auto; */
}

.search-input-group {
  position: relative;
  /* width: 50px; */
  margin: 0 auto;
}

.search-section :deep(.tagify) {
  --tags-border-color: rgba(255, 255, 255, 0.2);
  --tags-hover-border-color: rgba(255, 255, 255, 0.3);
  --tags-focus-border-color: #42b883;
  --placeholder-color: rgba(255, 255, 255, 0.8);
  --input-color: white;
  
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--tags-border-color);
  border-radius: 8px;
  padding: 0.5rem;
  transition: all 0.3s ease;
}

.search-section :deep(.tagify:hover) {
  border-color: var(--tags-hover-border-color);
}

.search-section :deep(.tagify--focus) {
  border-color: var(--tags-focus-border-color);
  background: rgba(255, 255, 255, 0.15);
}

.search-section :deep(.tagify__input),
.search-section :deep(.tagify__input > *),
.search-section :deep(.tagify__input::before),
.search-section :deep(.tagify__input::after) {
  color: white !important;
  caret-color: white !important;
}

.search-section :deep(.tagify__input > div) {
  color: white !important;
}

.search-section :deep(.tagify__input:focus),
.search-section :deep(.tagify__input:active) {
  color: white !important;
  background: transparent !important;
}

.search-section :deep(.tagify__tag) {
  background: rgba(66, 184, 131, 0.2) !important;
  color: white !important;
}

.search-section :deep(.tagify__input::placeholder),
.search-section :deep(.tagify__input::-webkit-input-placeholder),
.search-section :deep(.tagify__input:-ms-input-placeholder),
.search-section :deep(.tagify__input::-moz-placeholder) {
  color: rgba(255, 255, 255, 0.8) !important;
  opacity: 1 !important;
}

.search-input-group {
  position: relative;
  width: 100%;
}

.search-input-group :deep(.tagify) {
  flex: 1;
  min-width: 200px;
}

.search-btn {
  padding: 0.5rem 1.5rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.search-btn:hover:not(:disabled) {
  background-color: #3aa876;
  transform: translateY(-1px);
}

.search-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.search-btn:disabled {
  background-color: #2c3e50;
  opacity: 0.5;
  cursor: not-allowed;
}

.genre-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin-top: 5px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.genre-items {
  padding: 0.5rem;
}

.genre-item {
  padding: 0.5rem 1rem;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 4px;
}

.genre-item:hover {
  background: rgba(66, 184, 131, 0.2);
}

/* 스크롤바 스타일링 */
.genre-dropdown::-webkit-scrollbar {
  width: 6px;
}

.genre-dropdown::-webkit-scrollbar-thumb {
  background: rgba(66, 184, 131, 0.5);
  border-radius: 3px;
}

/* Tagify 드롭다운 비활성화 */
.tagify__dropdown {
  display: none !important;
}

.search-section :deep(.tagify__input::placeholder),
.search-section :deep(.tagify__input::-webkit-input-placeholder),
.search-section :deep(.tagify__input:-ms-input-placeholder),
.search-section :deep(.tagify__input::-moz-placeholder) {
  color: rgba(255, 255, 255, 0.8) !important;
  opacity: 1 !important;
}

.search-input-group input::placeholder,
.search-input-group input::-webkit-input-placeholder,
.search-input-group input:-ms-input-placeholder,
.search-input-group input::-moz-placeholder {
  color: rgba(255, 255, 255, 0.8) !important;
  opacity: 1 !important;
}

/* 슬라이더 버튼 스타일 수정 */
.slider-btn {
  display: none;
}
</style>