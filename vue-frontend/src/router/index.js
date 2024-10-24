import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue')
    },
    {
        path: '/pending',
        name: 'Pending',
        component: () => import('../views/pending.vue')
    },
    {
        path: '/edit',
        name: '/edit',
        component: () => import('../views/edit.vue')
    },
    {
        path: '/manual',
        name: '/manual',
        component: () => import('../views/manual.vue')
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/Login.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('../views/Register.vue')
    },
    {
        path: '/ucs_removed',
        name: 'UCS Removed',
        component: () => import('../views/ucs_removed.vue')
    },
    {
        path: '/new_crawler',
        name: 'New Crawler',
        component: () => import('../views/new_satellites/new_crawler.vue')
    },
    {
        path: '/new_pending',
        name: 'New Pending',
        component: () => import('../views/new_satellites/new_pending.vue')
    },
    {
        path: '/new_action',
        name: 'New Action',
        component: () => import('../views/new_satellites/new_action.vue')
    },
    {
        path: '/new_edit',
        name: 'New Edit',
        component: () => import('../views/new_satellites/new_edit.vue')
    },
    {
        path: '/duplicate_pending',
        name: 'Duplicate Pending',
        component: () => import('../views/duplicate_satellites/duplicate_pending.vue')
    }
]


const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes
})

router.beforeEach((to, from, next) => {
    const publicPages = ['/login', '/register']; // Paths of public pages that can be accessed without logging in
    const authRequired = !publicPages.includes(to.path); // Pages that require authentication
    const loggedIn = localStorage.getItem('authToken'); // Check if the token exists in local storage

    if (authRequired && !loggedIn) {
        return next('/login'); // Redirect to login page if authentication is required but user is not logged in
    }

    next(); // Otherwise, continue with the normal routing
});

export default router
