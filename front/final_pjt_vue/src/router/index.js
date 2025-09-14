import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LogInView from '@/views/LogInView.vue'
import MyPageView from '@/views/MyPageView.vue'
import SignUpView from '@/views/SignUpView.vue'
import MovieListView from '@/views/MovieListView.vue'
import MovieDetailView from '@/views/MovieDetailView.vue'
import TheaterListView from '@/views/TheaterListView.vue'
import TheaterMapView from '@/views/TheaterMapView.vue'
import SearchResultsView from '@/views/SearchResultsView.vue'
import TheaterUnityView from '@/views/TheaterUnityView.vue'
import SurveyView from '@/views/SurveyView.vue'
import RecommendationsView from '@/views/RecommendationsView.vue'
import { useMovieStore } from '@/stores/movie'
import NotFoundView from '@/views/NotFoundView.vue'

const routes = [
  {
    path: '/',
    name: 'HomeView',
    component: HomeView
  },
  {
    path: '/signup',
    name: 'SignUpView',
    component : SignUpView
  },
  {
    path: '/login',
    name: 'LogInView',
    component : LogInView
  },
  {
    path: '/:username/mypage',
    name: 'MyPageView',
    component : MyPageView
  },
  {
    path: '/movie',
    name: 'MovieListView',
    component : MovieListView
  },
  {
    path: '/movie/:movieId',
    name: 'MovieDetailView',
    component : MovieDetailView
  },
  {
    path: '/theaters',
    name: 'TheaterListView',
    component: TheaterListView
  },
  {
    path: '/theaters/:movieId/map',
    name: 'TheaterMapView',
    component: TheaterMapView
  },
  {
    path: '/theaters/:movieId/map/unity',
    name: 'TheaterUnityView',
    component: TheaterUnityView,
    props: true
  },
  {
    path: '/search',
    name: 'SearchResultsView',
    component: SearchResultsView
  },
  {
    path: '/survey',
    name: 'SurveyView',
    component: SurveyView,
    meta: { requiresAuth: true }
  },
  {
    path: '/recommendations',
    name: 'RecommendationsView',
    component: RecommendationsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

// 네비게이션 가드 추가
router.beforeEach((to, from, next) => {
  const store = useMovieStore()

  // 로그인/회원가입 페이지로 가려고 할 때
  if (store.token) {
    if (to.name === 'LogInView') {
      alert('이미 로그인되어 있습니다.')
      next({ name: 'HomeView' })
      return
    }
    if (to.name === 'SignUpView') {
      alert('회원가입은 로그아웃 후 가능합니다.')
      next({ name: 'HomeView' })
      return
    }
  }

  // 인증이 필요한 페이지 체크
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.token) {
      // 로그인이 필요한 페이지인데 로그인이 안 되어 있는 경우
      console.log('로그인이 필요합니다.')
      next({ 
        name: 'LogInView',
        query: { redirect: to.fullPath }  // 로그인 후 돌아올 페이지 저장
      })
      return
    }
  }

  next()
})

export default router
