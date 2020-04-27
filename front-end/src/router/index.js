import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/Home'
import SearchPage from '@/SearchPage'
import NewsPage from '@/NewsPage'

import MdCheckbox from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

Vue.use(MdCheckbox)

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: "/",
            redirect: {
                name: "Home"
            }
        },
        {
            path: '/home',
            name: 'Home',
            component: Home
        },
        {
            // path: '/search/:query/:pageNumber',
            path: '/search/:query',
            name: 'SearchPage',
            component: SearchPage
        },
        {
            // path: '/NewsPage/:id',
            path: '/NewsPage',
            name: 'NewsPage',
            component: NewsPage
        }
    ]
})
