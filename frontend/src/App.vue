<template>
  <router-view />
</template>

<style>
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  background: #f5f7fa;
}
.page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 20px;
}
.topbar {
  background: #123a6b;
  color: #fff;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.topbar a {
  color: #cfe0f5;
  text-decoration: none;
  margin-right: 16px;
}
</style>
