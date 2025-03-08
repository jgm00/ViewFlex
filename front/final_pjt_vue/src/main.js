// import './assets/main.css'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import { useKakao } from 'vue3-kakao-maps/@utils';

useKakao(import.meta.env.VITE_KAKAO_MAP_KEY, ['clusterer', 'services', 'drawing'])

const app = createApp(App)
const pinia = createPinia()

pinia.use(piniaPluginPersistedstate)
//app.use(createPinia())
app.use(pinia)
app.use(router)

app.mount('#app')
