import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    set_web:false,
    website:'',
    temper:'',
    highest_temper: '',
    lowest_temper: '',
    low_speed_fee: '',
    middle_speed_fee: '',
    high_speed_fee: '',
    default_temper: '',
    default_speed: '',
    mode: '',
    power_state: false,
  },
  //mutations: {},
  //actions: {}
})
