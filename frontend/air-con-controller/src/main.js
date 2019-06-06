import Vue from 'vue'
import App from './App.vue'
import router from './router.js'
import store from './store/store.js'
import Axios from 'axios'
import './assets/style/font-awesome-4.7.0/css/font-awesome.min.css'

Vue.prototype.$axios = Axios
Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
