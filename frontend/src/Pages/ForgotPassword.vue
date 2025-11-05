<template>
  <div class="container py-5 d-flex flex-column align-items-center">
    <div class="col-12 col-md-7 col-lg-5">
      <h3 class="fw-bold mb-2">Forgot Password</h3>
      <p class="text-muted mb-4">
        Enter the account email and your new password. If the email exists, we’ll reset it right away.
      </p>

      <form @submit.prevent="handleSubmit" novalidate>
        <!-- Email -->
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input
            v-model.trim="form.email"
            type="email"
            class="form-control"
            placeholder="you@example.com"
            :class="{'is-invalid': errors.email}"
          />
          <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
        </div>

        <!-- New password -->
        <div class="mb-3">
          <label class="form-label">New Password</label>
          <div class="input-group">
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model.trim="form.new_password"
              class="form-control"
              placeholder="••••••••"
              :class="{'is-invalid': errors.new_password}"
              @input="validatePassword"
            />
            <button class="btn btn-outline-secondary" type="button" @click="showPassword = !showPassword">
              <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
            </button>
            <div v-if="errors.new_password" class="invalid-feedback d-block">{{ errors.new_password }}</div>
          </div>
          <small class="text-muted d-block mt-2">
            Must be 8+ chars, with upper, lower, number, and special character.
          </small>
        </div>

        <button class="btn btn-teal w-100" :disabled="submitting">
          <span v-if="!submitting">Reset Password</span>
          <span v-else class="d-inline-flex align-items-center gap-2">
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Processing…
          </span>
        </button>

        <div v-if="serverMessage" class="alert mt-3"
             :class="success ? 'alert-success' : 'alert-danger'">
          {{ serverMessage }}
        </div>

        <div class="text-center mt-3">
          <router-link to="/">Back to Login</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { resetPassword } from '@/api/auth'

export default {
  name: 'ForgotPassword',
  data() {
    return {
      form: {
        email: '',
        new_password: '',
      },
      errors: {},
      submitting: false,
      serverMessage: '',
      success: false,
      showPassword: false,
    }
  },
  methods: {
    validatePassword() {
      const p = this.form.new_password || ''
      if (p.length < 8) {
        this.errors.new_password = 'Password must be at least 8 characters.'
      } else if (!/[A-Z]/.test(p)) {
        this.errors.new_password = 'Include at least one uppercase letter.'
      } else if (!/[a-z]/.test(p)) {
        this.errors.new_password = 'Include at least one lowercase letter.'
      } else if (!/\d/.test(p)) {
        this.errors.new_password = 'Include at least one number.'
      } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(p)) {
        this.errors.new_password = 'Include at least one special character.'
      } else {
        this.errors.new_password = ''
      }
    },
    validateAll() {
      this.errors = {}
      // Email
      if (!this.form.email) {
        this.errors.email = 'Email is required.'
      } else if (!/^\S+@\S+\.\S+$/.test(this.form.email)) {
        this.errors.email = 'Please enter a valid email.'
      }
      // Password
      this.validatePassword()
      return Object.values(this.errors).every(v => !v)
    },
    async handleSubmit() {
      this.serverMessage = ''
      this.success = false
      if (!this.validateAll()) return

      this.submitting = true
      try {
        const res = await resetPassword({
          email: this.form.email,
          new_password: this.form.new_password,
        })
        if (res?.success) {
          this.success = true
          this.serverMessage = res.message || 'Password reset successful.'
          // Optional: redirect to login after 1.5s
          setTimeout(() => this.$router.push('/'), 1500)
        } else {
          this.success = false
          this.serverMessage = res?.message || 'Failed to reset password.'
        }
      } catch (err) {
        this.success = false
        // Try to surface backend details if present
        const msg = err?.response?.data?.error?.detail || err?.response?.data?.message
        this.serverMessage = msg || 'Server error. Please try again.'
        console.error('resetPassword error:', err)
      } finally {
        this.submitting = false
      }
    },
  }
}
</script>

<style scoped>
.btn-teal { background-color:#0a8588; color:#fff; border:none; }
.btn-teal:hover { background-color:#087375; color:#fff; }
</style>
