import { defineStore } from 'pinia'
import http from '../lib/http'

export const useMessageStore = defineStore('message', {
  state: () => ({
    roomMessages: {},
    loadingRoomId: null,
  }),

  getters: {
    getMessagesByRoom: (state) => {
      return (roomId) => state.roomMessages[roomId] || []
    },

    isRoomLoading: (state) => {
      return (roomId) => state.loadingRoomId === roomId
    },
  },

  actions: {
    async fetchRoomMessages(roomId, limit = 50) {
      if (!roomId) {
        return []
      }

      this.loadingRoomId = roomId

      try {
        const response = await http.get(`/messages/room/${roomId}`, {
          params: { limit },
        })

        this.roomMessages[roomId] = response.data
        return response.data
      } finally {
        if (this.loadingRoomId === roomId) {
          this.loadingRoomId = null
        }
      }
    },

    appendOrUpdateMessage(roomId, message) {
      if (!roomId || !message) {
        return
      }

      const current = this.roomMessages[roomId] || []
      const index = current.findIndex((item) => item.id === message.id)

      if (index === -1) {
        this.roomMessages[roomId] = [...current, message]
        return
      }

      const next = [...current]
      next[index] = {
        ...next[index],
        ...message,
      }
      this.roomMessages[roomId] = next
    },

    clearMessages() {
      this.roomMessages = {}
      this.loadingRoomId = null
    },
  },
})
