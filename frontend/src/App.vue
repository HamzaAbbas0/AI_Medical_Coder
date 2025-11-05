<script>
import Login from '../src/Pages/Login.vue';
import SignUp from '../src/Pages/Sign-Up.vue';
import Mainlayout from '../src/Layouts/Mainlayout.vue';
export default {
  components: {
    Login,
    SignUp,
    Mainlayout
  }
}
</script>

<template>
  <!-- <login />
  <SignUp /> -->
  <router-view></router-view>
</template>
