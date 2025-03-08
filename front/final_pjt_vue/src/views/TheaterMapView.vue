<template>
  <div class="theater-container">
    <div v-if="isLoading" class="loading">
      Loading...
    </div>
    <div v-else>
      <!-- 선택된 영화 정보 섹션 -->
      <div v-if="selectedMovie" class="selected-movie-section">
        <div class="movie-backdrop" :style="{ backgroundImage: `url(https://image.tmdb.org/t/p/original${selectedMovie.backdrop_path})` }">
          <div class="backdrop-overlay"></div>
        </div>
        <div class="content-wrapper">
          <img :src="`https://image.tmdb.org/t/p/w300${selectedMovie.poster_path}`" 
               :alt="selectedMovie.title"
               class="selected-movie-poster">
          <div class="selected-movie-info">
            <h1>{{ selectedMovie.title }}</h1>
            <div class="meta">
              <span class="rating">
                <i class="fas fa-star"></i>
                {{ selectedMovie.vote_average.toFixed(1) }}
              </span>
              <span class="dot"></span>
              <span class="runtime">
                <i class="far fa-clock"></i>
                {{ selectedMovie.runtime }}분
              </span>
              <span class="dot"></span>
              <span class="release-date">
                <i class="far fa-calendar-alt"></i>
                {{ selectedMovie.release_date }}
              </span>
            </div>
            <button @click="goToMovieDetail" class="detail-btn">
              <i class="fas fa-info-circle"></i>
              상세정보
            </button>
          </div>
        </div>
      </div>

      <!-- 검색창 -->
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="극장 검색 (영화관 이름, 주소, 지역 등)"
          @keyup.enter="searchTheaters"
        >
        <button @click="searchTheaters" class="search-btn">
          <i class="fas fa-search"></i>
        </button>
      </div>

      <!-- 지도 컨테이너 -->
      <div class="map-wrapper">
        <div class="map-container">
          <KakaoMap 
            :lat="coordinate.lat" 
            :lng="coordinate.lng" 
            :draggable="true"
            :level="3"
            class="kakao-map"
            @onLoadKakaoMap="onLoadKakaoMap"
          >
            <KakaoMapMarker
              v-for="(marker, index) in markerList"
              :key="index"
              :lat="marker.lat"
              :lng="marker.lng"
              :infoWindow="marker.infoWindow"
              :clickable="true" 
              @onClickKakaoMapMarker="onClickMapMarker(marker)"
            />
          </KakaoMap>
        </div>

        <div class="search-result-wrapper">
          <div class="result-header">
            <span class="result-title">검색 결과</span>
            <span class="result-count" v-if="searchResults.length > 0">
              총 <strong>{{ searchResults.length }}</strong>개
            </span>
          </div>
          <div class="result-list" :style="resultListStyle">
            <div v-for="(place, index) in searchResults" 
                 :key="index"
                 class="result-item"
                 @mouseover="highlightMarker(place)"
                 @mouseout="unhighlightMarker"
                 @click="moveToLocation(place)">
              <div class="item-number">{{ index + 1 }}</div>
              <div class="item-info">
                <h4 class="item-title">{{ place.place_name }}</h4>
                <p class="item-address">{{ place.address }}</p>
                <p class="item-phone" v-if="place.phone">{{ place.phone }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 극장 정보 섹션 -->
      <div v-if="selectedMovie" class="theater-section">
        <h3 class="theater-title">[{{ selectedMovie.title }}] 상영시간표</h3>
        
          <!-- 체인별 필터 -->
          <div class="filter-section">
            <button v-for="chain in theaterChains" 
                    :key="chain"
                    :class="['chain-btn', { active: selectedChain === chain }]"
                    @click="selectChain(chain)">
              {{ chain }}
            </button>
          </div>

          <!-- 지역별 필터 -->
          <div v-if="theaters.length > 0"class="filter-section">
            <button v-for="area in theaterAreas" 
                    :key="area"
                    :class="['area-btn', { active: selectedArea === area }]"
                    @click="selectArea(area)">
              {{ area }}
            </button>
          </div>

          <!-- 극장 목록 -->
          <div class="theaters-container">
            <div v-if="filteredTheaters.length === 0" class="no-theaters-message">
              <p>
                <template v-if="selectedMovie">
                  <template v-if="selectedMovie.id === 9999996">
                    <!-- CGV 단독 개봉 영화인 경우 -->
                    <template v-if="selectedChain && selectedChain !== 'CGV'">
                      [{{ selectedMovie.title }}]는 CGV 단독 개봉입니다.
                    </template>
                    <template v-else>
                      [{{ selectedMovie.title }}]를 상영 중인 영화관이 없습니다.
                    </template>
                  </template>
                  <template v-else>
                    <!-- 기존 메시지 로직 -->
                    <template v-if="selectedChain && selectedArea">
                      "{{ selectedArea }}" 지역에  [{{ selectedMovie.title }}]를 상영 중인 "{{ selectedChain }}" 영화관이 없습니다.
                    </template>
                    <template v-else-if="selectedChain">
                      [{{ selectedMovie.title }}]를 상영 중인 {{ selectedChain }} 영화관이 없습니다.
                    </template>
                    <template v-else-if="selectedArea">
                      [{{ selectedMovie.title }}]를 상영 중인 {{ selectedArea }} 지역 영화관이 없습니다.
                    </template>
                    <template v-else>
                      [{{ selectedMovie.title }}]를 상영 중인 영화관이 없습니다.
                    </template>
                  </template>
                </template>
              </p>
            </div>
            <div v-else class="theaters-list" :class="{ 'show-all': showAllTheaters }">
              <div v-for="(theaterGroup, theaterName) in groupedTheaters" 
                   :key="theaterName"
                   class="theater-card">
                <div class="theater-header">
                  <h4>{{ theaterName }}</h4>
                </div>
                <div class="screens-container">
                  <div v-for="screen in theaterGroup" 
                       :key="`${screen.screen}-${screen.movie_type}`"
                       class="screen-info-row">
                    <div class="theater-screen-info">
                      <span class="screen-name">{{ screen.screen }}</span>
                      <span v-if="screen.movie_type" 
                            :class="['movie-type-tag', getTypeClass(screen.movie_type)]">
                        {{ formatMovieType(screen.movie_type) }}
                      </span>
                    </div>
                    <div class="time-slots-container">
                      <div class="time-slots">
                        <button v-for="time in sortedShowingTimes(screen.showing_times)"
                                :key="time"
                                class="time-btn">
                          {{ time }}
                        </button>
                      </div>
                      <div class="theater-view-btn-container">
                        <button @click="goTheaterUnity(screen.theater_id)" class="theater-view-btn">
                          <i class="fas fa-video"></i>
                          극장 보기
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="show-more-section" v-if="filteredTheaters.length > 4">
            <button class="show-more-btn" @click="toggleShowAll">
              {{ showAllTheaters ? '접기' : `더보기 (총 ${filteredTheaters.length}개)` }}
            </button>
          </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { KakaoMap, KakaoMapMarker } from 'vue3-kakao-maps'
  
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useMovieStore } from '@/stores/movie'
import { useRoute, useRouter } from 'vue-router'

// window 함수를 script 최상단에 배치
window.routeToPlace = (placeName, lat, lng) => {
  window.open(`https://map.kakao.com/link/to/${placeName},${lat},${lng}`, '_blank')
}

window.showPlaceDetail = (placeName) => {
  window.open(`https://map.kakao.com/link/search/${placeName}`, '_blank')
}

const coordinate = {
  lat: 36.1071708,
  lng: 128.4178800
}

const router = useRouter()
const route = useRoute()
const store = useMovieStore()
const isLoading = ref(true)
const selectedMovie = ref(null)
const theaters = ref([])
const selectedChain = ref(null)
const selectedArea = ref(null)
const showAllTheaters = ref(false)
const movieId = route.params.movieId

// 검색 관련 상태 추가
const searchKeyword = ref('')
const map = ref(null)
const markerList = ref([])
const searchResults = ref([{
  place_name: '메가박스 구미강동',
  address: '경북 구미시 인동가산로 14',
  phone: '1544-0070',
  lat: coordinate.lat,
  lng: coordinate.lng,
  infoWindow: {
    content: `
      <div class="custom-overlay">
        <div class="overlay-title">메가박스 구미강동</div>
        <div class="overlay-address">경북 구미시 인동가산로 14</div>
        <div class="overlay-phone">1544-0070</div>
        <div class="overlay-buttons">
          <button class="overlay-btn" onclick="window.routeToPlace('메가박스 구미강동', ${coordinate.lat}, ${coordinate.lng})">
            <img src="https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/places_jibun.png" width="14" height="14">
            길찾기
          </button>
          <button class="overlay-btn" onclick="window.showPlaceDetail('메가박스 구미강동')">
            상세정보
          </button>
        </div>
      </div>
    `,
    visible: false
  }
}])
const isListView = ref(false)

// initialMarker 수정
const initialMarker = ref({
  lat: coordinate.lat,
  lng: coordinate.lng,
  infoWindow: {
    content: `
      <div class="custom-overlay">
        <div class="overlay-title">메가박스 구미강동</div>
        <div class="overlay-address">경북 구미시 인동가산로 14</div>
        <div class="overlay-phone">1544-0070</div>
        <div class="overlay-buttons">
          <button class="overlay-btn" onclick="window.routeToPlace('메가박스 구미강동', ${coordinate.lat}, ${coordinate.lng})">
            <img src="https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/places_jibun.png" width="14" height="14">
            길찾기
          </button>
          <button class="overlay-btn" onclick="window.showPlaceDetail('메가박스 구미강동')">
            상세정보
          </button>
        </div>
      </div>
    `,
    visible: false
  }
})

// theaters 데이터를 가져오는 함수 추가
const fetchTheaters = async () => {
  try {
    let url = `http://127.0.0.1:8000/movies/${movieId}/theaters/`
    
    const params = new URLSearchParams()
    if (selectedChain.value) params.append('chain', selectedChain.value)
    if (selectedArea.value) params.append('area', selectedArea.value)
    
    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const response = await axios.get(url)
    
    if (response.data.length === 0) {
      let message = ''
      
      if (selectedMovie.value.id === 9999996) {
        // CGV 단독 개봉 영화인 경우
        if (selectedChain.value && selectedChain.value !== 'CGV') {
          message = `[${selectedMovie.value.title}]는 CGV 단독 개봉입니다.`
        } else {
          message = `[${selectedMovie.value.title}]를 상영 중인 영화관이 없습니다.`
        }
      } else {
        // 기존 메시지 로직
        message = `[${selectedMovie.value.title}]`
        if (selectedChain.value && selectedArea.value) {
          message = `"${selectedArea.value}" 지역에 ` + message + `를 상영 중인 "${selectedChain.value}" 영화관이 없습니다.`
        } else if (selectedChain.value) {
          message += `를 상영 중인 "${selectedChain.value}" 영화관이 없습니다.`
        } else if (selectedArea.value) {
          message += `를 상영 중인 "${selectedArea.value}" 지역 영화관이 없습니다.`
        } else {
          message += '를 상영 중인 영화관이 없습니다.'
        }
      }
      
      alert(message)
      return
    }
    
    theaters.value = response.data
    updateMapMarkers()
  } catch (error) {
    console.error('극장 정보를 가져오는데 실패했습니다:', error)
  }
}

// onMounted 수정
onMounted(async () => {
  isLoading.value = true
  try {
    if (movieId) {
      console.log('현재 movieId:', movieId)
      
      // 영화 정보 가져오기
      const movieResponse = await axios.get(`http://127.0.0.1:8000/movies/${movieId}`)
      selectedMovie.value = movieResponse.data
      
      // 극장 정보 가져오기
      await fetchTheaters()
    }
  } catch (error) {
    console.error('Error details:', error.response)
  } finally {
    isLoading.value = false
  }
})

// 극 체인 목록 - 모든 체인을 항상 표시
const theaterChains = computed(() => {
  return ['메가박스', '롯데시네마', 'CGV']
})

// theaterAreas computed 속성을 수정
const theaterAreas = computed(() => {
  return ['서울', '경기', '대구', '경북', '부산', '경남']
})

// 필터링된 극장 목록
const filteredTheaters = computed(() => {
  let filtered = theaters.value || []
  
  if (selectedChain.value) {
    filtered = filtered.filter(t => t.chain === selectedChain.value)
  }
  
  if (selectedArea.value) {
    filtered = filtered.filter(t => t.area === selectedArea.value)
  }
  
  return filtered
})

// 극장별로 그룹화된 데이터
const groupedTheaters = computed(() => {
  const filtered = filteredTheaters.value
  const grouped = {}
  
  filtered.forEach(theater => {
    const theaterName = `${theater.chain} ${theater.theater}`
    if (!grouped[theaterName]) {
      grouped[theaterName] = []
    }
    
    grouped[theaterName].push({
      screen: theater.screen,
      movie_type: theater.movie_type,
      showing_times: theater.showing_times
    })
  })
  
  return grouped
})

// 시간 정렬 함수
const sortedShowingTimes = (times) => {
  return [...times].sort((a, b) => {
    const timeA = a.split(':').map(Number)
    const timeB = b.split(':').map(Number)
    return (timeA[0] * 60 + timeA[1]) - (timeB[0] * 60 + timeB[1])
  })
}

// 영화 타입에 따른 클래스
const getTypeClass = (type) => {
  const typeMap = {
    '2D': 'type-2d',
    '3D': 'type-3d',
    'IMAX': 'type-imax',
    '4DX': 'type-4dx',
    'SCREENX': 'type-screenx'
  }
  return typeMap[type] || 'type-default'
}

const formatMovieType = (type) => {
  return type || '일반'
}

// selectChain 함수 수정
const selectChain = async (chain) => {
  if (selectedChain.value === chain) {
    selectedChain.value = null
  } else {
    selectedChain.value = chain
  }
  await fetchTheaters()
}

// selectArea 함수 수정
const selectArea = async (area) => {
  if (selectedArea.value === area) {
    selectedArea.value = null
  } else {
    selectedArea.value = area
  }
  await fetchTheaters()
}

// 지도 마커 업데이트 함수 추가
const updateMapMarkers = () => {
  if (!map.value) return

  // 필터링된 극장 목록 가져오기
  const filteredTheatersList = theaters.value?.filter(theater => {
    const chainMatch = !selectedChain.value || theater.chain === selectedChain.value
    const areaMatch = !selectedArea.value || theater.area === selectedArea.value
    return chainMatch && areaMatch
  }) || []

  // 필터링된 결과가 없으면 초기 마커로 리셋
  if (filteredTheatersList.length === 0) {
    markerList.value = [initialMarker.value]
    const initialPosition = new kakao.maps.LatLng(coordinate.lat, coordinate.lng)
    map.value.setCenter(initialPosition)
    map.value.setLevel(3)
    return
  }

  // 중복 제거를 위한 Map 객체 생성 (theater와 chain 조합으로 unique key 생성)
  const uniqueTheaters = new Map()
  
  filteredTheatersList.forEach(theater => {
    const key = `${theater.chain}-${theater.theater}`
    if (!uniqueTheaters.has(key)) {
      uniqueTheaters.set(key, theater)
    }
  })

  // 중복이 제거된 극장 목록으로 마커 생성
  markerList.value = Array.from(uniqueTheaters.values()).map(theater => ({
    lat: theater.lat,
    lng: theater.lng,
    infoWindow: {
      content: `
        <div class="custom-overlay">
          <div class="overlay-title">${theater.chain} ${theater.theater}</div>
          <div class="overlay-address">${theater.area}</div>
          <div class="overlay-buttons">
            <button class="overlay-btn" onclick="window.routeToPlace('${theater.chain} ${theater.theater}', ${theater.lat}, ${theater.lng})">
              <img src="https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/places_jibun.png" width="14" height="14">
              길찾기
            </button>
            <button class="overlay-btn" onclick="window.showPlaceDetail('${theater.chain} ${theater.theater}')">
              상세정보
            </button>
          </div>
        </div>
      `,
      visible: false
    },
    place_name: `${theater.chain} ${theater.theater}`,
    address: theater.area,
    phone: theater.phone || ''
  }))

  // 검색 결과 목록도 동일하게 업데이트
  searchResults.value = markerList.value

  // 지도 범위 재설정
  if (markerList.value.length > 0) {
    const bounds = new kakao.maps.LatLngBounds()
    markerList.value.forEach(marker => {
      bounds.extend(new kakao.maps.LatLng(marker.lat, marker.lng))
    })
    map.value.setBounds(bounds)
  }
}

// 더보기 토글
const toggleShowAll = () => {
  showAllTheaters.value = !showAllTheaters.value
}

// 극장 보기 버튼
const goTheaterUnity = (movieId) => {
  router.push({ name: 'TheaterUnityView', params: { movieId } })
}

// 지도 로드 시 호출되는 함수 수정
const onLoadKakaoMap = (mapRef) => {
  map.value = mapRef
  
  // 초기 마커 설정 (기존 마커와 동일)
  markerList.value = searchResults.value
  
  // 지도 중심 이동
  const initialPosition = new kakao.maps.LatLng(coordinate.lat, coordinate.lng)
  map.value.setCenter(initialPosition)
  map.value.setLevel(3)
}

// 검색 콜백 함수 수정
const placesSearchCB = (data, status) => {
  if (status === kakao.maps.services.Status.OK) {
    const bounds = new kakao.maps.LatLngBounds()
    markerList.value = []
    searchResults.value = []

    const filteredData = data.filter(place => 
      place.place_name.match(/CGV|메가박스|롯데시네마/i)
    )

    if (filteredData.length === 0) {
      alert('검색 결과가 없습니다.')
      return
    }

    filteredData.forEach((place) => {
      const markerItem = {
        lat: place.y,
        lng: place.x,
        infoWindow: {
          content: `
            <div class="custom-overlay">
              <div class="overlay-title">${place.place_name}</div>
              <div class="overlay-address">${place.address_name}</div>
              ${place.phone ? `<div class="overlay-phone">${place.phone}</div>` : ''}
              <div class="overlay-buttons">
                <button class="overlay-btn" onclick="window.routeToPlace('${place.place_name}', ${place.y}, ${place.x})">
                  <img src="https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/places_jibun.png" width="12" height="12">
                  길찾기
                </button>
                <button class="overlay-btn" onclick="window.showPlaceDetail('${place.place_name}')">
                  상세정보
                </button>
              </div>
            </div>
          `,
          visible: false
        },
        place_name: place.place_name,
        address: place.address_name,
        phone: place.phone
      }
      markerList.value.push(markerItem)
      searchResults.value.push(markerItem)
      bounds.extend(new kakao.maps.LatLng(Number(place.y), Number(place.x)))
    })

    if (markerList.value.length > 0) {
      map.value?.setBounds(bounds)
    }
  } else {
    alert('검색 결과가 없습니다.')
  }
}

// 극장 검색 함수 수정
const searchTheaters = () => {
  if (!searchKeyword.value) return

  const ps = new kakao.maps.services.Places()
  const searchQuery = `${searchKeyword.value} 영화관`
  ps.keywordSearch(searchQuery, placesSearchCB)
}

// 마커 클릭 이벤트 핸들
const onClickMapMarker = (markerItem) => {
  if (markerItem.infoWindow?.visible !== null && markerItem.infoWindow?.visible !== undefined) {
    markerItem.infoWindow.visible = !markerItem.infoWindow.visible
  } else {
    markerItem.infoWindow.visible = true
  }
}

// 목록/지도 뷰 토글 함수
const toggleView = () => {
  isListView.value = !isListView.value
}

// 검색 결과 항목에 클릭 ���벤트 추가
const moveToLocation = (place) => {
  const moveLatLng = new kakao.maps.LatLng(place.lat, place.lng)
  map.value?.setCenter(moveLatLng)
  map.value?.setLevel(3)  // 줌 레벨 설정
  
  // 해 마커의 인포윈도우 표시
  markerList.value.forEach(marker => {
    if (marker.place_name === place.place_name) {
      marker.infoWindow.visible = true
    } else {
      marker.infoWindow.visible = false
    }
  })
}

// 마커 하이라이트 함수 추가
const highlightMarker = (place) => {
  markerList.value.forEach(marker => {
    if (marker.place_name === place.place_name) {
      // 마커 크기 확대 및 인포윈도우 표시
      marker.infoWindow.visible = true
      
      // 지도 중심 이동
      const moveLatLng = new kakao.maps.LatLng(place.lat, place.lng)
      map.value?.panTo(moveLatLng)
    } else {
      marker.infoWindow.visible = false
    }
  })
}

// 마커 하이라이트 제거 함수 추가
const unhighlightMarker = () => {
  markerList.value.forEach(marker => {
    marker.infoWindow.visible = false
  })
}

// 검색 결과 목록 스타일 수정
const resultListStyle = {
  maxHeight: '300px',
  overflowY: 'auto',
  background: 'white',
  borderRadius: '8px',
  boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
}

// 커스텀 오버레이 스타일 추가
const style = document.createElement('style');
style.textContent = `
  .custom-overlay {
    position: relative;
    background: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    min-width: 200px;
    border: 1px solid #ddd;
  }

  .overlay-title {
    font-size: 14px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
  }

  .overlay-address {
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
  }

  .overlay-phone {
    font-size: 12px;
    color: #0072d2;
    margin-bottom: 8px;
  }

  .overlay-buttons {
    display: flex;
    gap: 8px;
    margin-top: 10px;
  }

  .overlay-btn {
    flex: 1;
    padding: 6px 8px;
    border: none;
    border-radius: 4px;
    background: #0072d2;
    color: white;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    transition: all 0.2s ease;
  }

  .overlay-btn:hover {
    background: #0066bd;
  }

  .overlay-btn img {
    opacity: 0.8;
  }

  .overlay-arrow {
    position: absolute;
    bottom: -8px;
    left: 50%;
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid #fff;
    transform: translateX(-50%);
  }
`;
document.head.appendChild(style);

const goToMovieDetail = () => {
  router.push({ name: 'MovieDetailView', params: { id: selectedMovie.value.id } })
}
</script>

<style scoped>
.theater-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  animation: smoothPageTransition 0.8s cubic-bezier(0.65, 0, 0.35, 1);
  transform-origin: center;
  width: 100%;
  min-height: 100vh;
  will-change: transform, opacity;
}

@keyframes smoothPageTransition {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #ffffff;
}

.movie-list {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
}

.movie-item {
  flex: 0 0 auto;
  width: 150px;
  cursor: pointer;
  transition: transform 0.2s;
  position: relative;
}

.movie-item:hover {
  transform: scale(1.05);
}

.movie-item.active {
  transform: scale(1.05);
}

.movie-item.active::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: #ff0000;
}

.movie-poster {
  width: 100%;
  height: 225px;
  object-fit: cover;
  border-radius: 8px;
}

.movie-title {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  text-align: center;
  color: #ffffff;
}

.theater-section {
  margin-top: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.theater-title {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #ffffff;
}

.filter-section {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.chain-btn, .area-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
}

.chain-btn:hover, .area-btn:hover,
.chain-btn.active, .area-btn.active {
  background: #0072d2 !important;
}

.theaters-container {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 1rem;
  margin-top: 1rem;
}

.theaters-list {
  height: 680px;
  overflow-y: auto;
  padding-right: 1rem;
  transition: height 0.3s ease;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}


.theaters-list.show-all {
  height: auto;
  margin-bottom: 1rem;
}

.theaters-list::-webkit-scrollbar {
  width: 6px;
}

.theaters-list::-webkit-scrollbar-track {
  background: transparent;
}

.theaters-list::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.theater-card {
  background: rgba(40, 49, 59, 0.9);
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
}

.theater-card:hover {
  transform: translateY(-2px);
}

.theater-header {
  padding: 1rem 1.5rem;
  background: rgba(30, 39, 49, 0.95);
}

.theater-header h4 {
  color: #ffffff;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.screens-container {
  padding: 0.5rem;
}

.screen-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.theater-screen-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 300px;
}

.screen-name {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
}

.movie-type-tag {
  background: rgba(0, 114, 210, 0.2);
  color: #64B5F6 !important;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  min-width: 45px;
  text-align: center;
  display: inline-block;
  white-space: nowrap;
  min-width: fit-content;
}

.time-slots {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: flex-end;
  flex: 1;
}

.time-btn {
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: #ffffff;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 70px;
  text-align: center;
}

.time-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

/* 영화 타입 태그 스타일 */
.type-2d {
  color: #64B5F6 !important;
  padding: 0.3rem 0.6rem;
}

.type-3d {
  color: #CE93D8;
}

.type-imax {
  color: #F48FB1;
}

.type-4dx {
  color: #FFE082;
}

.type-screenx {
  color: #A5D6A7;
}

.type-default {
  background: #0074d21a !important;
  color: #E0E0E0;
  padding: 0.3rem 0.8rem;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .screen-info-row {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .theater-screen-info {
    width: 100%;
    justify-content: space-between;
  }

  .time-slots {
    width: 100%;
    justify-content: flex-start;
  }
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #ffffff;
}

/* 스크롤바 스타일링 */
.movie-list::-webkit-scrollbar {
  display: none;
}

.movie-list {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* 새로운 스타일 추가 */
.no-theaters-message {
  text-align: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  margin: 1rem 0;
}

.no-theaters-message p {
  color: #ffffff;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.back-button {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 24px;
  background: rgba(0, 114, 210, 0.8);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(0, 114, 210, 0.3);
}

.back-button:hover {
  background: rgba(0, 114, 210, 1);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 114, 210, 0.4);
}

.back-button:active {
  transform: translateY(1px);
}

/* 선택 영화 섹션 스타일 수정 */
.selected-movie-section {
  position: relative;
  width: 100%;
  min-height: 300px;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 0.75rem !important;
}

.movie-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 1;
}

.backdrop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0.8) 0%,
    rgba(0, 0, 0, 0.6) 50%,
    rgba(0, 0, 0, 0.4) 100%
  );
  z-index: 2;
}

.content-wrapper {
  position: relative;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 3rem;
  padding: 1.5rem 2rem;
}

.selected-movie-poster {
  width: 180px;
  height: 270px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.selected-movie-poster:hover {
  transform: translateY(-5px);
}

.selected-movie-info {
  flex: 1;
}

.selected-movie-info h1 {
  font-size: 2.8rem;
  color: #ffffff;
  margin: 0 0 1rem 0;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: -0.5px;
  line-height: 1.2;
}

.meta {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  color: #ffffff;
  font-size: 1.1rem;
}

.dot {
  color: rgba(255, 255, 255, 0.6);
  font-weight: bold;
}

.rating, .runtime, .release-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating i {
  color: #FFC107;
}

.runtime i, .release-date i {
  color: rgba(255, 255, 255, 0.9);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
    text-align: center;
    padding: 2rem;
    gap: 1.5rem;
  }

  .selected-movie-info h1 {
    font-size: 2.5rem;
  }

  .selected-movie-poster {
    width: 180px;
    height: 270px;
  }

  .meta {
    justify-content: center;
    font-size: 1.1rem;
  }
}

/* 기존의 movie-list 스타일 수정 */
.recommended-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: #ffffff;
}

.show-more-section {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  padding: 1rem;
}

.show-more-btn {
  margin-top: 1rem;
  width: 100%;
  background: rgba(0, 114, 210, 0.5);
  color: white;
  border: none; 
  padding: 0.8rem 2rem;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.show-more-btn:hover {
  background: rgba(0, 114, 210, 0.7);
}

.show-more-btn:active {
  transform: translateY(1px);
}

/* 영화 타입 태그 스타일 */
.movie-type-tag {
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.type-2d {
  background: rgba(0, 114, 210, 0.2);
  color: #64B5F6;
}

.type-3d {
  background: rgba(156, 39, 176, 0.2);
  color: #CE93D8;
}

.type-imax {
  background: rgba(233, 30, 99, 0.2);
  color: #F48FB1;
}

.type-4dx {
  background: rgba(255, 193, 7, 0.2);
  color: #FFE082;
}

.type-screenx {
  background: rgba(76, 175, 80, 0.2);
  color: #A5D6A7;
}

.type-default {
  background: rgba(158, 158, 158, 0.2);
  color: #E0E0E0;
}

.screen-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.theater-screen-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 300px;
}

.time-slots {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: flex-end;
  flex: 1;
}

.time-slots-container {
  display: flex;
  align-items: center;
  gap: 2rem;  /* 시간 버튼과 극장 보기 버튼 사이    격 */
  flex: 1;
}

.theater-view-btn-container {
  margin-left: auto;  /* 오른 정렬 */
}

.theater-view-btn {
  background-color: rgba(0, 114, 210, 0.2);
  color: #64B5F6;
  border: 1px solid rgba(100, 181, 246, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.theater-view-btn:hover {
  background-color: rgba(0, 114, 210, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 114, 210, 0.2);
}

.theater-view-btn:active {
  transform: translateY(0);
}

.theater-view-btn i {
  font-size: 0.9rem;
}

.map-container {
  width: 100%;
  height: 400px;
  margin: 0 !important;
  background: rgba(40, 49, 59, 0.9);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.kakao-map {
  width: 100% !important;
  height: 100%;
  border-radius: 12px;
}

.search-box {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: rgb(26, 29, 41);
  border-radius: 8px;
  margin-bottom: 1rem;
  width: 100%;
  max-width: 1180px;
  margin: 0 auto 1rem auto;
}

.search-box input {
  background: rgb(47, 49, 54);
  color: rgba(255, 255, 255, 0.897);
  flex: 1;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 14px;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.712);
}

.search-btn {
  padding: 12px 24px;
  background: #0072d2;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-btn:hover {
  background: #005bb7;
  transform: translateY(-1px);
}

.search-btn:active {
  transform: translateY(1px);
}

.search-section {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.view-toggle-btn {
  padding: 12px 24px;
  background: #1a1d29;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-results {
  background: rgb(26, 29, 41);
  border-radius: 12px;
  margin-top: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
}

.result-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.result-item h3 {
  color: white;
  margin: 0 0 0.5rem 0;
}

.result-item p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  font-size: 0.9rem;
}

.custom-overlay {
  padding: 15px;
  background: white;
  border-radius: 5px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.overlay-title {
  font-size: 15px;
  font-weight: 600;
  color: #000;
  margin-bottom: 8px;
}

.overlay-address {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 5px;
}

.overlay-phone {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 10px;
}

.overlay-buttons {
  display: flex;
  gap: 5px;
  margin-top: 10px;
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
}

.overlay-btn {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 3px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.overlay-btn:hover {
  background: #f8f8f8;
  border-color: #c8c8c8;
}

.map-wrapper {
  display: flex;
  gap: 1rem;
  height: 400px;
  margin-bottom: 2rem;
  flex-direction: row;
}

.search-result-wrapper {
  flex: 0 0 300px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.result-header {
  padding: 15px;
  background: #fff;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.result-count {
  font-size: 13px;
  color: #666;
}

.result-count strong {
  color: #0072d2;
}

.result-list {
  flex: 1;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.result-item:hover {
  background-color: #f8f9fa;
}

.result-item:last-child {
  border-bottom: none;
}

.item-number {
  width: 24px;
  height: 24px;
  background: #0072d2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 12px;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
}

.item-title {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: 600;
  color: #000;
}

.item-address {
  margin: 0 0 3px 0;
  font-size: 12px;
  color: #333 !important;
}

.item-phone {
  margin: 0;
  font-size: 12px;
  color: #0072d2 !important;
  font-weight: 500;
}

.map-container {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
}

.detail-btn {
  margin-top: 1.5rem;
  background: rgba(0, 114, 210, 0.5);
  color: #64B5F6;
  border: 1px solid rgba(100, 181, 246, 0.3);
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: fit-content;
}

.detail-btn i {
  font-size: 0.9rem;
}

.detail-btn:hover {
  background: rgba(0, 114, 210, 0.7);
  transform: translateY(-2px);
}

.detail-btn:active {
  transform: translateY(1px);
}

</style>