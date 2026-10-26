import { defineStore } from 'pinia'
import request from '../api/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || ''
  }),
  actions: {
    async login(form) {
      const data = await request.post('/auth/login', form)
      this.token = data.token
      this.username = data.user.username
      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.user.username)
    },
    async register(form) {
      return request.post('/auth/register', form)
    },
    logout() {
      this.token = ''
      this.username = ''
      localStorage.removeItem('token')
      localStorage.removeItem('username')
    }
  }
})
