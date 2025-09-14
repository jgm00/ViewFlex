<template>
  <div class="logo">
    <span class="view">View</span><span class="flex">Flex</span>
    <span class="plus">+</span>
  </div>
</template>

<style scoped>
.logo {
  font-family: 'Montserrat', sans-serif;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
  cursor: pointer;
  user-select: none;
  display: inline-block;
}

.view {
  background: linear-gradient(120deg, #ffffff 0%, #e6e6e6 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.flex {
  background: linear-gradient(120deg, #0072d2 0%, #00a2ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.plus {
  color: #0072d2;
  font-size: 28px;
  font-weight: 400;
  margin-left: 1px;
  vertical-align: baseline;
}
</style>