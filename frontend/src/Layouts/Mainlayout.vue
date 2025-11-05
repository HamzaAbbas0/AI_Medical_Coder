<script>
import Dashboard from "../components/Dashboard.vue";
import Navbar from "../components/Navbar.vue";
export default {
  components: {
    Navbar,
    Dashboard
  }
}
</script>
<template>
  <div class="d-flex">
    <Navbar />
    <div class="flex-grow-1 p-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<style scoped></style>
loca