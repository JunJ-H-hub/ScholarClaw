import { createApp } from 'vue'
import AppRoot from './AppRoot.vue'
import router from './router'

const app = createApp(AppRoot)
app.use(router)
app.mount('#app')