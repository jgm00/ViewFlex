import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useMovieStore = defineStore('movie', {
  state: () => ({
    API_URL: 'http://127.0.0.1:8000',
    token: localStorage.getItem('token'),
    username: localStorage.getItem('username'),
    movies: [],
    movie: null,
    reviews: [],
    likes: [],
    isLoading: false,
    searchResults: [],
    router: null,
    recommendedMovies: [],
    hasRecommendations: false,
    analysis: '',
    aiRecommendations: [],
    hasAiRecommendations: false
  }),

  getters: {
    isLiked: (state) => (movieId) => {
      return new Set(state.likes).has(Number(movieId))
    },
    isLogin: (state) => {
      return state.token !== null
    },
    hasRecommendations: (state) => {
      return state.aiRecommendations && state.aiRecommendations.length > 0
    }
  },

  actions: {
    initialize(routerInstance) {
      this.router = routerInstance
    },
    logIn(payload) {
      const { username: user, password } = payload

      axios({
        method: 'post',
        url: `${this.API_URL}/accounts/login/`,
        data: {
          username: user, 
          password
        }
      })
        .then((res) => {
          this.token = res.data.key
          this.username = user
          localStorage.setItem('token', res.data.key)
          localStorage.setItem('username', user)
          this.router.push({ name: 'HomeView' })
          this.LikedMovies()
        })
        .catch((err) => {
          console.log(err)
        })
    },
    logOut() {
      axios({
        method: 'post',
        url: `${this.API_URL}/accounts/logout/`,
      })
        .then((res) => {
          console.log(res.data)
          this.token = null
          this.username = null
          this.clearRecommendedMovies()
          localStorage.removeItem('token')
          localStorage.removeItem('username')
          
          if (this.router) {
            this.router.push({ name: 'HomeView' })
          }
        })
        .catch((err) => {
          console.log(err)
        })
    },
    getMovies() {
      axios({
        method: 'get',
        url: `${this.API_URL}/movies/`,
        headers: {
           Authorization: `Token ${this.token}`
        }
      })
        .then((res) => {
          this.movies = res.data
        })
        .catch((err) => {
          console.log(err)
        })
    },
    getMovieDetail(movieId) {
      const headers = this.token ? { Authorization: `Token ${this.token}` } : {}

      axios({
        method: 'get',
        url: `${this.API_URL}/movies/${movieId}/`,
        headers: headers
      })
        .then((res) => {
          this.movie = res.data
        })
        .catch((err) => {
          console.error(err)
        })
    },
    getReview(movieId) {
      const headers = this.token ? { Authorization: `Token ${this.token}` } : {}

      axios({
        method: 'get',
        url: `${this.API_URL}/movies/${movieId}/reviews/`,
        headers: headers
      })
        .then((res) => {
          this.reviews = res.data
        })
        .catch((err) => console.log(err))
    },
    async Like(movieId) {
      movieId = Number(movieId)
      try {
        const res = await axios({ 
          method: 'post',
          url: `${this.API_URL}/movies/${movieId}/likes/`,
          headers: {
            Authorization: `Token ${this.token}`
          }
        })
        
        await this.LikedMovies()

        await this.getMovies()
        
        if (this.movie?.id === movieId) {
          this.movie = {
            ...this.movie,
            like_count: res.data.like_count
          }
        }

        return res.data 
      } catch (err) {
        console.error(err)
        throw err
      }
    },
    LikedMovies() {
      if (!this.token) return

      axios({
        method: 'get',
        url: `${this.API_URL}/movies/liked/`,
        headers: {
          Authorization: `Token ${this.token}`
        }
      })
        .then((res) => {
          this.likes = res.data.map(movie => movie.id)
        })
        .catch((err) => {
          console.error('좋아요 목록 조회 중 오류:', err)
        })
    },
    updateMovieLikeStatus(movieId, userId, isLiked) {
      const movieIndex = this.movies.findIndex(m => m.id === movieId)
      if (movieIndex !== -1) {
        const movie = this.movies[movieIndex]
        if (isLiked) {
          if (!movie.like_users.includes(userId)) {
            this.movies[movieIndex] = {
              ...movie,
              like_users: [...movie.like_users, userId]
            }
          }
        } else {
          this.movies[movieIndex] = {
            ...movie,
            like_users: movie.like_users.filter(id => id !== userId)
          }
        }
      }
    },
    signUp(payload) {
      const { username: signupUsername, password1, password2 } = payload

      return axios({
        method: 'post',
        url: `${this.API_URL}/accounts/signup/`,
        data: {
          username: signupUsername,
          password1,
          password2
        }
      })
        .then(() => {
          return axios({
            method: 'post',
            url: `${this.API_URL}/accounts/login/`,
            data: {
              username: signupUsername,
              password: password1
            }
          })
        })
        .then((res) => {
          this.token = res.data.key
          this.username = signupUsername
          localStorage.setItem('token', res.data.key)
          localStorage.setItem('username', signupUsername)
          this.LikedMovies()
          this.router.push({ name: 'SurveyView' })
        })
        .catch((err) => {
          console.error('Error during signup/login:', err)
          if (err.response) {
            console.error('Error response:', err.response.data)
          }
          throw err
        })
    },
    async saveSurvey(surveyData) {
      const formattedData = {
        ...surveyData,
        preferred_genres: Array.isArray(surveyData.preferred_genres) 
          ? surveyData.preferred_genres.join(',') 
          : surveyData.preferred_genres,
        movie_elements: Array.isArray(surveyData.movie_elements)
          ? surveyData.movie_elements.join(',')
          : surveyData.movie_elements,
        favorite_movies: Array.isArray(surveyData.favorite_movies)
          ? surveyData.favorite_movies.join(',')
          : surveyData.favorite_movies
      }

      try {
        const response = await axios({
          method: 'post',
          url: `${this.API_URL}/users/survey/`,
          headers: {
            Authorization: `Token ${this.token}`,
            'Content-Type': 'application/json'
          },
          data: formattedData
        })

        console.log('Survey API Response:', response) // API 응답 확인

        // 응답 데이터가 있고 추천 영화가 포함되어 있는지 확인
        if (response.data && response.data.recommended_movies) {
          // 추천 영화 데이터 저장
          await this.setRecommendedMovies(
            response.data.recommended_movies,
            response.data.analysis || ''
          )
          console.log('Recommendations saved:', this.recommendedMovies)
        }

        return response // 전체 응답 반환
      } catch (error) {
        console.error('Survey save error:', error.response?.data || error.message)
        throw error
      }
    },
    async setRecommendedMovies(movies) {
      if (!movies || !Array.isArray(movies)) {
        console.error('Invalid movies data:', movies)
        return
      }

      try {
        // 전체 영화 목록을 한 번에 ��져옵니다
        const allMoviesResponse = await axios({
          method: 'get',
          url: `${this.API_URL}/movies/`,
          headers: {
            Authorization: `Token ${this.token}`
          }
        })

        const allMovies = allMoviesResponse.data
        console.log('All movies from database:', allMovies.length)

        // 추천된 각 영화의 상세 정보를 찾습니다
        const moviesWithDetails = movies.map(recommendedMovie => {
          // 디버깅을 위한 로그
          console.log('Looking for movie:', recommendedMovie.title)

          // 제목 정규화 함수
          const normalizeTitle = (title) => {
            return title
              .toLowerCase()
              .replace(/[:\-–—]/g, '') // 특수문자 제거
              .replace(/\(.*?\)/g, '') // 괄호와 그 안의 내용 제거
              .replace(/\s+/g, '') // 공백 제거
              .trim()
          }

          const movieDetails = allMovies.find(m => {
            const normalizedDBTitle = normalizeTitle(m.title)
            const normalizedRecommendedTitle = normalizeTitle(recommendedMovie.title)
            
            // 디버깅을 위한 로그
            if (normalizedDBTitle.includes(normalizedRecommendedTitle) || 
                normalizedRecommendedTitle.includes(normalizedDBTitle)) {
              console.log('Found match:', m.title, 'for', recommendedMovie.title)
            }
            
            return normalizedDBTitle.includes(normalizedRecommendedTitle) || 
                   normalizedRecommendedTitle.includes(normalizedDBTitle)
          })

          if (movieDetails) {
            return {
              ...movieDetails, // 기존 영화 정보 모두 포함
              reason: recommendedMovie.reason, // AI 추천 이유 추가
              id: movieDetails.id // ID 명시적 포함
            }
          }
          
          // 매칭되는 영화를 찾지 못한 경우
          console.warn(`Movie not found: ${recommendedMovie.title}`)
          return {
            ...recommendedMovie,
            id: null, // ID가 없는 경우 명시적으로 null 설정
            poster_path: null // 포스터 경로도 없음을 표시
          }
        }).filter(movie => movie !== null) // null 값 제거

        console.log('Final processed movies:', moviesWithDetails)

        this.aiRecommendations = moviesWithDetails
        this.hasAiRecommendations = true
        
        // localStorage에 저장
        localStorage.setItem('aiRecommendations', JSON.stringify(this.aiRecommendations))
        localStorage.setItem('hasAiRecommendations', 'true')
        
        console.log('Stored AI recommendations:', this.aiRecommendations)
      } catch (error) {
        console.error('Error setting recommended movies:', error)
      }
    },
    loadRecommendedMovies() {
      try {
        const savedMovies = localStorage.getItem('aiRecommendations')
        if (savedMovies) {
          this.aiRecommendations = JSON.parse(savedMovies)
          this.hasAiRecommendations = true
        }
      } catch (error) {
        console.error('Failed to load AI recommendations:', error)
        this.clearRecommendedMovies()
      }
    },
    clearRecommendedMovies() {
      this.aiRecommendations = []
      this.hasAiRecommendations = false
      localStorage.removeItem('aiRecommendations')
      localStorage.removeItem('hasAiRecommendations')
    }
  }
})
