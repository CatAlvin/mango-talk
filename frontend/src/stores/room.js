import { defineStore } from 'pinia'
import http from '../lib/http'

export const useRoomStore = defineStore('room', {
  state: () => ({
    rooms: [],
    selectedRoomId: null,
    loading: false,
  }),

  getters: {
    selectedRoom(state) {
      return state.rooms.find((room) => room.id === state.selectedRoomId) || null
    },
  },

  actions: {
    async fetchMyRooms() {
      this.loading = true

      try {
        const response = await http.get('/rooms/mine')
        this.rooms = response.data

        if (!this.selectedRoomId && this.rooms.length > 0) {
          this.selectedRoomId = this.rooms[0].id
        }

        if (
          this.selectedRoomId &&
          !this.rooms.some((room) => room.id === this.selectedRoomId)
        ) {
          this.selectedRoomId = this.rooms.length > 0 ? this.rooms[0].id : null
        }

        return this.rooms
      } finally {
        this.loading = false
      }
    },

    selectRoom(roomId) {
      this.selectedRoomId = roomId
    },

    clearRooms() {
      this.rooms = []
      this.selectedRoomId = null
    },
  },
})
