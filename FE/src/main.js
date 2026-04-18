import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import './assets/main.css'

const app = createApp(App)

app.use(Toast, {
  position: 'top-right',
  timeout: 3200,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  hideProgressBar: false,
  newestOnTop: true,
  maxToasts: 5,
})

app.use(router)
app.mount('#app')
