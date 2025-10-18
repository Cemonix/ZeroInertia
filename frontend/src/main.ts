import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import ToastService from 'primevue/toastservice'
import './styles/main.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faTrash, faPlus, faCheck, faSpinner, faEdit, faChevronDown, faChevronRight, faEllipsisVertical } from '@fortawesome/free-solid-svg-icons'

// PrimeVue components
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'
import Dialog from 'primevue/dialog'

library.add(faTrash, faPlus, faCheck, faSpinner, faEdit, faChevronDown, faChevronRight, faEllipsisVertical)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: '.dark-mode',
      cssLayer: {
        name: 'primevue',
        order: 'reset, primevue, components'
      }
    }
  }
})
app.use(ToastService)

app.component('FontAwesomeIcon', FontAwesomeIcon)
app.component('Button', Button)
app.component('InputText', InputText)
app.component('Checkbox', Checkbox)
app.component('Dialog', Dialog)

app.mount('#app')

const authStore = useAuthStore()
authStore.initialize()
