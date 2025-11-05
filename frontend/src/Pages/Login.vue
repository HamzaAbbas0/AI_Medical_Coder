<template>
  <div class="login-page d-flex align-items-center justify-content-center flex-column">
    <!--Dropdown Box-->
    <div class="col-12 language-dropdown text-end my-2 px-4">
      <div class="dropdown">
        <a class="btn dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
          EN
        </a>

        <ul class="dropdown-menu">
          <li><a class="dropdown-item" href="#">English</a></li>
          <!-- <li><a class="dropdown-item" href="#">English</a></li>
        <li><a class="dropdown-item" href="#">English</a></li> -->
        </ul>
      </div>
    </div>
    <!-- Background image-->
    <div class="background-img">
      <img class="background-img" src="/src/assets/Sign Up Screen (1).png" alt="Background" />
    </div>


    <!-- Login Box -->
    <div class="login-box bg- col-xl-5 col-md-8 col-lg-7">
      <div class="title text-center py-2">
        <h2>Hi, Welcome Back!</h2>
        <p>Please login to your account!</p>
      </div>
      <!--Email iNPUT-->
      <div>
        <form @submit.prevent="handleSubmit">
       
          <div class="mb-3 text-start">
            <label class="form-label">Username</label>

            <!--Email Input field-->
            <div class="input-group input-box">
              <span class="input-group-text bg-white border-end-0">
                <i class="fa-regular fa-envelope text-muted"></i>
              </span>
              <input v-model="username" type="text" class="form-control border-start-0" placeholder="Enter your username" />
            </div>
          </div>

          <!-- Password Fields-->
          <div class="mb-3 text-start">
            <label class="form-label">Password</label>
            <div class="input-group input-box">
              <input v-model="password" :type="showPassword ? 'text' : 'password'" class="form-control py-2 border-end-0" placeholder="••••••••" />
              <span class="input-group-text bg-white" @click="togglePassword"><i class="fa-solid fa-eye text-muted" ></i></span>
            </div>
          </div>

          <div class="text-end mt-2">
            <router-link to="/forgot-password" class="text-decoration-underline">Forgot password?</router-link>
          </div>

          <!-- check box -->
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="keepSignedIn" />
              <label class="form-check-label" for="keepSignedIn">
                Keep me signed in
              </label>
            </div>
          </div>

          <!-- Sign In -->
          <div class="d-flex py-2 mb-3">
            <button type="submit" class="btn btn-teal  flex-fill">Sign In</button>
          </div>

          <div class="divider my-4 text-muted text-center">
            <span>OR</span>
          </div>
          
          <!-- google and facebook button -->
          <button type="button"
            class="btn btn-outline-secondary button-login w-100 mb-2 d-flex align-items-center justify-content-center gap-2 rounded-5">
            <img src="/src/assets/google.png" width="20px" alt=""> Login With Google
          </button>
          <button type="button"
            class="btn btn-outline-secondary button-login w-100 d-flex align-items-center justify-content-center gap-2 rounded-5">
            <img src="/src/assets/facebook.png" width="20px" alt=""> Login With Facebook
          </button>

          <!-- Login box Footer -->
          <div class="mt-4 text-center">
            New User? <router-link to="/Sign-up"
              class="text-decoration-underline text-primary fw-medium New-user">Create an
              Account</router-link>
          </div>
        </form>
      </div>
    </div>

    <!--Footer Box-->
    <div class="col-5 my-2 mt-4 footer-main d-flex align-items-center justify-content-between">
      <span class="text-muted"> @2025 All Right Reserved</span>
      <span class="text-muted">Privacy policy Terms of Use</span>
    </div>
  </div>
</template>

<script>
import { login } from '../api/auth'

export default {
  data() {
    return {
      username: '', // changed from email
      password: '',
      showPassword: false,
    }
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword
    },
    async handleSubmit() {
      try {
        const { data } = await login(this.username, this.password)
        // Save token for future requests
        localStorage.setItem('token', data.access || data.token)
        alert('Login successful!')
        this.$router.push('/dashboard')
      } catch (err) {
        console.error(err)
        alert('Login failed. Please check credentials.')
      }
    }
  }
}
</script>

