<template>
  <nav class="navbar" role="navigation">
    <div class="navbar-brand">
      <a role="button" class="navbar-burger" :class="{'is-active': mainNavVis}" @click="toggleMainNav">
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>
    <div class="navbar-menu" :class="{'is-active': mainNavVis}">
      <div class="navbar-start">
        <router-link class="navbar-item" to="/">Home</router-link>
        <router-link class="navbar-item" to="/about">About</router-link>
        <router-link class="navbar-item" to="/queue">Queue</router-link>
      </div>
      <div class="navbar-end"></div>
    </div>
  </nav>
</template>

<script>
export default {
  data() {
    return {
      mainNavVis: false,
    };
  },
  methods:{
    toggleMainNav () {
      this.mainNavVis = !this.mainNavVis
    }
  }
};
</script>
