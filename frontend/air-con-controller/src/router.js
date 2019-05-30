import Vue from 'vue'
import Router from 'vue-router'
import Initpage from './views/initpage.vue'
import Room from './views/room.vue'
import Reception from './views/reception.vue'
import Manager from './views/manager.vue'
import Server from './views/server.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'initpage',
      component: Initpage
    },
    {
      path: '/room',
      name: 'room',
      component: Room
    },
    {
      path: '/reception',
      name: 'reception',
      component: Reception
    },
    {
      path: '/manager',
      name: 'manager',
      component: Manager
    },
    {
      path: '/server',
      name: 'server',
      component: Server
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
    }
  ]
})
