<template>
  <div id="app">
    <k-nav></k-nav>
    <div class="section">
    <router-view/>
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  data() {
    return {
    };
  },
  components: {
    'k-nav': NavBar,
  },
};
</script>


<style lang="stylus">

</style>
