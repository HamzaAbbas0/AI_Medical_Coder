import { createRouter, createWebHistory } from 'vue-router'
import Login from '../Pages/Login.vue'
import Signup from '../Pages/Sign-Up.vue'
import Dashboard from '../components/Dashboard.vue'
import MainLayout from '../Layouts/Mainlayout.vue'
import ForgotPassword from '../Pages/ForgotPassword.vue'

const routes = [
    {
        path: '/',
        name: 'login',
        component: Login
    },
    {
        path: '/sign-up',
        name: 'sign-up',
        component: Signup,
    },
    {
        path: '/dashboard',
        component: MainLayout,
        children: [
            {
                path: '',
                name: 'Dashboard',
                component: Dashboard
            },
        ]
    },

    { path: '/forgot-password', 
    name: 'ForgotPassword', 
    component: ForgotPassword, 
    meta: { public: true } 
}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Simple guard to protect dashboard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!token && to.path.startsWith('/dashboard')) return next({ name: 'login' })
  next()
})

export default router