<template>
  <div class="sidebar d-flex flex-column p-3">
    <div class="text-center mb-4">
      <h4 class="fw-bold logo-text">AI Medical <span class="fw-normal">Coder</span></h4>
    </div>

    <!-- Profile IMage -->
    <div class="text-center mb-3">
      <img src="/src/assets/user.png" alt="Profile" class="profile-img" />
    </div>

    <!-- User Profile -->
    <div class="text-center mb-4 text-muted">
      <div class="fw-semibold Profile-text">Aaish Hameedi</div>
      <small class="text-muted- Profile-date">{{ formattedDate }}</small>
    </div>

    <!-- Sidebar DropDown BUtton-->
    <div class="dropdown mb-3">
      <button
        class="btn btn-sidebar d-flex justify-content-between align-items-center w-100"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#dashboardMenu"
      >
        <span><i class="fa-solid fa-gauge me-2"></i> Dashboard</span>
        <i class="fa-solid fa-chevron-right"></i>
      </button>

      <div class="collapse ps-4 mt-2" id="dashboardMenu">
        <a href="#" class="sidebar-link">Overview</a>
        <a href="#" class="sidebar-link">Reports</a>
        <a href="#" class="sidebar-link">Analytics</a>
      </div>
    </div>

    <hr class="text-secondary my-3" />

    <!-- Settings Sidebar Button-->
    <button class="btn btn-sidebar text-start mb-1">
      <i class="fa-solid fa-gear me-2"></i> Settings
    </button>

    <!-- Logout Button-->
    <router-link to="/" class="btn btn-sidebar text-start mt-auto-">
      <i class="fa-solid fa-right-from-bracket me-2"></i> Logout
    </router-link>
  </div>
</template>

<style scoped>
.sidebar {
  width: 260px;
  min-height: 100vh;
  background-color: #f1f2f6;
}

.logo-text {
  color: #0a8588 !important;
}

.profile-img {
  width: 90px;
  height: 90px;
  object-fit: cover;
  border-radius: 50%;
}
.Profile-text{
    color: #030304;
}
.Profile-date{
    color: #8f9093;
}
.btn-sidebar {
  background: none;
  color: #525254;
  font-weight: 400;
  width: 100%;
  text-align: left;
  padding: 8px 10px;
  border: none;
  transition: background 0.2s ease;
}

.btn-sidebar:hover {
  background-color: #e0e0e0;
}

.sidebar-link {
  display: block;
  color: #555;
  text-decoration: none;
  padding: 6px 0;
  transition: color 0.2s;
}

.sidebar-link:hover {
  color: #0a8588;
}

hr {
  border-color: #ccc;
  opacity: 1;
}
</style>

<script>
export default {
    name: "CurrentDate",
    data() {
        return {
            formattedDate: '',
        };
    },
    created() {
        const today = new Date();
        // Format date as YYYY-MM-DD
        // this.formattedDate = today.toISOString().split("T")[0];
        this.formattedDate = today.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric"
        });
    },
};
</script>
