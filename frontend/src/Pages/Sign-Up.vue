<template>
  <div class="signup-page d-flex align-items-center justify-content-center flex-column">
    <!--Dropdown Box-->
    <div class="col-12 language-dropdown text-end my-3 px-2">
      <div class="dropdown">
        <a class="btn dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
          EN
        </a>
        <ul class="dropdown-menu">
          <li><a class="dropdown-item" href="#">English</a></li>
        </ul>
      </div>
    </div>

    <!-- IMage Background -->
    <img class="background-img" src="/src/assets/Sign Up Screen (1).png" alt="Background" />

    <!-- Signup Box -->
    <div class="signup-box bg-white col-xl-6 col-md-8 col-lg-7">
      <div class="title text-center py-3">
        <h2>Hi, Welcome To AI Medical Coder</h2>
        <p>Please signup to your account</p>
      </div>

      <form @submit.prevent="handleSubmit">
        <!-- Username -->
        <div class="mb-3 text-start">
          <label class="form-label">Username</label>
          <div class="input-group input-box">
            <span class="input-group-text bg-white border-end-0">
              <i class="fa-regular fa-user text-muted"></i>
            </span>
            <input
              type="text"
              class="form-control border-start-0"
              placeholder="John Doe"
              v-model="form.username"
              required
            />
          </div>
        </div>

        <!-- Email -->
        <div class="mb-3 text-start">
          <label class="form-label">Email Address</label>
          <div class="input-group input-box">
            <span class="input-group-text bg-white border-end-0 rounded-start-5">
              <i class="fa-regular fa-envelope text-muted"></i>
            </span>
            <input
              type="email"
              class="form-control border-start-0 rounded-end-5"
              placeholder="example123@gmail.com"
              v-model="form.email"
              required
            />
          </div>
        </div>

        <!-- Password -->
        <div class="mb-3 text-start">
          <label class="form-label">Password</label>
          <div class="input-group input-box">
            <input
              :type="showPassword ? 'text' : 'password'"
              class="form-control border-end-0 rounded-start-5"
              placeholder="••••••••"
              v-model="form.password"
              @input="validatePassword"
              required
            />
            <span class="input-group-text bg-white rounded-end-5" @click="togglePassword">
              <i class="fa-solid fa-eye text-muted"></i>
            </span>
          </div>
          <small v-if="passwordError" class="text-danger">{{ passwordError }}</small>
        </div>

        <!-- Submit -->
        <div class="d-flex py-2 mb-3">
          <button type="submit" class="btn btn-teal flex-fill" :disabled="loading">
            <span v-if="loading">
              <i class="fa fa-spinner fa-spin me-2"></i> Registering...
            </span>
            <span v-else>Sign Up</span>
          </button>
        </div>

        <!-- Alerts -->
        <div v-if="alert.message" class="alert" :class="alert.type" role="alert">
          {{ alert.message }}
        </div>

        <div class="divider my-4 text-muted text-center"><span>OR</span></div>

        <!-- Google / Facebook Buttons -->
        <button type="button"
          class="btn btn-outline-secondary button-login w-100 mb-2 d-flex align-items-center justify-content-center gap-2 rounded-5">
          <img src="/src/assets/google.png" width="20px" alt=""> Sign Up With Google
        </button>
        <button type="button"
          class="btn btn-outline-secondary button-login w-100 d-flex align-items-center justify-content-center gap-2 rounded-5">
          <img src="/src/assets/facebook.png" width="20px" alt=""> Sign Up With Facebook
        </button>

        <!-- Footer -->
        <div class="mt-4 text-center">
          Already have an account?
          <router-link to="/" class="text-decoration-underline text-primary fw-medium User-login">
            Login
          </router-link>
        </div>
      </form>
    </div>

    <!-- Footer Last -->
    <div class="col-5 my-2 mt-4 footer-main d-flex align-items-center justify-content-between">
      <span class="text-muted">@2025 All Rights Reserved</span>
      <span class="text-muted">Privacy Policy Terms of Use</span>
    </div>
  </div>
</template>

<script>
import { registerUser } from '../api/auth'

export default {
  data() {
    return {
      showPassword: false,
      passwordError: '',
      loading: false,
      form: {
        username: '',
        email: '',
        password: '',
      },
      alert: {
        message: '',
        type: '',
      },
    }
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword
    },
    validatePassword() {
      const p = this.form.password
      if (p.length < 8) {
        this.passwordError = 'Password must be at least 8 characters long.'
      } else if (!/[A-Z]/.test(p)) {
        this.passwordError = 'Password must contain at least one uppercase letter.'
      } else if (!/[a-z]/.test(p)) {
        this.passwordError = 'Password must contain at least one lowercase letter.'
      } else if (!/[0-9]/.test(p)) {
        this.passwordError = 'Password must contain at least one number.'
      } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(p)) {
        this.passwordError = 'Password must contain at least one special character.'
      } else {
        this.passwordError = ''
      }
    },
    async handleSubmit() {
      this.validatePassword()
      if (this.passwordError) return

      this.loading = true
      this.alert = { message: '', type: '' }

      try {
        const res = await registerUser(this.form)
        this.loading = false

        if (res.code === 'USER_REGISTERED') {
          this.alert = {
            message: 'Registration successful! Redirecting to login...',
            type: 'alert-success',
          }

          setTimeout(() => this.$router.push('/'), 1500)
        } else {
          this.alert = {
            message: res.message || 'Registration failed.',
            type: 'alert-danger',
          }
        }
      } catch (err) {
        this.loading = false
        console.error(err)
        this.alert = {
          message: err.response?.data?.message || 'Something went wrong during registration.',
          type: 'alert-danger',
        }
      }
    },
  },
}
</script>

<style scoped>
.language-dropdown {
  z-index: 2;
  position: relative;
}

.dropdown-toggle {
  background-color: white;
  border-radius: 7px;
  padding: 2px 8px;
}

.signup-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.background-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 1;
  z-index: 0;
}

.signup-box {
  position: relative;
  background-color: white;
  z-index: 2;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.User-login {
  color: #4cc3c9 !important;
}

.alert {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.alert-success {
  color: #155724;
  background-color: #d4edda;
  border-color: #c3e6cb;
  border-radius: 8px;
  padding: 0.75rem;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
  border-radius: 8px;
  padding: 0.75rem;
}
</style>
