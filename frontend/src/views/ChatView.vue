<template>
  <div class="chat-page">
    <!-- mobile overlay -->
    <div
      v-if="sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    ></div>

    <!-- mobile hamburger -->
    <button
      class="mobile-menu-btn"
      @click="sidebarOpen = !sidebarOpen"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>

    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="brand-block">
        <div class="brand-logo">
          <svg viewBox="0 0 36 36" fill="none"><rect width="36" height="36" rx="10" fill="url(#sb)"/><path d="M10 15.5c0-3.3 3.6-6 7.5-6s7.5 2.7 7.5 6-3.6 6-7.5 6c-1 0-1.9-.13-2.75-.38L12 23l.88-2.65C11.56 19.16 10 17.44 10 15.5z" fill="#fff" fill-opacity=".9"/><defs><linearGradient id="sb" x1="0" y1="0" x2="36" y2="36"><stop stop-color="#fb923c"/><stop offset="1" stop-color="#f97316"/></linearGradient></defs></svg>
        </div>
        <div>
          <h2>Mango Talk</h2>
          <p class="muted">v0.5 附件消息阶段</p>
        </div>
      </div>

      <div class="user-card">
        <div class="avatar">
          {{ userInitial }}
        </div>
        <div class="user-meta">
          <p class="username">{{ authStore.user?.username || '未登录用户' }}</p>
          <p class="role">{{ authStore.user?.role || 'unknown' }}</p>
        </div>
        <div class="user-online-dot"></div>
      </div>

      <div class="room-section">
        <div class="room-section-header">
          <h3>我的房间</h3>
          <button class="refresh-btn" @click="handleRefreshRooms" :disabled="roomStore.loading">
            <svg v-if="!roomStore.loading" viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/></svg>
            <span v-else class="spinner-tiny"></span>
          </button>
        </div>

        <div v-if="roomStore.loading && roomStore.rooms.length === 0" class="room-empty">
          <span class="spinner-tiny"></span>
          <span>正在加载房间列表...</span>
        </div>

        <div v-else-if="roomStore.rooms.length === 0" class="room-empty">
          你当前还没有任何房间
        </div>

        <div v-else class="room-list">
          <button
            v-for="room in roomStore.rooms"
            :key="room.id"
            class="room-item"
            :class="{ active: room.id === roomStore.selectedRoomId }"
            @click="handleSelectRoom(room.id); sidebarOpen = false"
          >
            <div class="room-avatar" :class="room.type">
              {{ getRoomInitial(room) }}
            </div>

            <div class="room-info">
              <div class="room-top">
                <p class="room-name">{{ room.display_name }}</p>
                <span class="room-type-badge" :class="room.type">
                  {{ room.type === 'private' ? '私聊' : '群聊' }}
                </span>
              </div>

              <div class="room-bottom">
                <span>{{ room.member_count }} 人</span>
                <span class="room-role">{{ room.my_role }}</span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <button class="logout-btn" @click="handleLogout">
        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V4a1 1 0 00-1-1H3zm7.707 4.293a1 1 0 010 1.414L9.414 10l1.293 1.293a1 1 0 01-1.414 1.414l-2-2a1 1 0 010-1.414l2-2a1 1 0 011.414 0z" clip-rule="evenodd"/><path d="M14 10a1 1 0 01-1 1H9a1 1 0 110-2h4a1 1 0 011 1z"/></svg>
        退出登录
      </button>
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <template v-if="roomStore.selectedRoom">
          <div class="chat-header-main">
            <div class="chat-header-text">
              <h2>{{ roomStore.selectedRoom.display_name }}</h2>
              <p>
                {{ roomStore.selectedRoom.type === 'private' ? '私聊' : '群聊' }}
                · {{ roomStore.selectedRoom.member_count }} 位成员
                · {{ roomStore.selectedRoom.my_role }}
              </p>
            </div>

            <div class="ws-status" :class="wsStatusClass">
              <span class="ws-dot"></span>
              {{ wsStatusText }}
            </div>
          </div>
        </template>

        <template v-else>
          <div class="empty-header">
            <h2>欢迎回来</h2>
            <p>请从左侧选择一个房间开始聊天</p>
          </div>
        </template>
      </header>

      <section class="message-list">
        <template v-if="roomStore.selectedRoom">
          <div v-if="isCurrentRoomLoading" class="message-empty">
            <span class="spinner"></span>
            <span>正在加载消息记录...</span>
          </div>

          <div v-else-if="currentMessages.length === 0" class="message-empty">
            <svg viewBox="0 0 48 48" fill="none" width="48" height="48" style="opacity:0.4"><rect x="4" y="8" width="40" height="28" rx="6" stroke="currentColor" stroke-width="2"/><path d="M4 30l8-6 6 4 10-8 16 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
            <span>当前房间还没有消息，发送第一条吧</span>
          </div>

          <div v-else class="message-area">
            <div
              ref="messageScrollRef"
              class="message-scroll"
              @scroll="handleMessageScroll"
            >
              <div
                v-for="message in currentMessages"
                :key="message.id"
                class="message-row"
                :class="{ mine: isMine(message) }"
              >
                <div class="message-avatar-col" v-if="!isMine(message)">
                  <div class="msg-avatar">{{ getSenderLabel(message).charAt(0) }}</div>
                </div>

                <div class="message-body">
                  <div class="message-meta">
                    <span class="sender">
                      {{ getSenderLabel(message) }}
                    </span>
                    <span class="time">
                      {{ formatTime(message.created_at) }}
                    </span>
                  </div>

                  <div
                    class="message-bubble"
                    :class="{
                      mine: isMine(message),
                      recalled: message.is_recalled
                    }"
                  >
                    <p v-if="message.reply_to_message_id" class="reply-tip">
                      回复消息 #{{ message.reply_to_message_id }}
                    </p>

                    <p v-if="message.is_recalled" class="recalled-text">
                      该消息已被撤回
                    </p>

                    <template v-else>
                      <p v-if="message.content" class="message-content">
                        {{ message.content }}
                      </p>

                      <div
                        v-if="message.message_type === 'image' && getImageAttachments(message).length > 0"
                        class="attachment-list image-list"
                      >
                        <a
                          v-for="attachment in getImageAttachments(message)"
                          :key="attachment.id || attachment.stored_name"
                          class="image-attachment-link"
                          :href="attachment.file_url"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <img
                            class="image-attachment-preview"
                            :src="attachment.file_url"
                            :alt="attachment.original_name"
                          />
                        </a>
                      </div>

                      <div
                        v-if="message.message_type === 'file' && getFileAttachments(message).length > 0"
                        class="attachment-list file-list"
                      >
                        <a
                          v-for="attachment in getFileAttachments(message)"
                          :key="attachment.id || attachment.stored_name"
                          class="file-attachment-card"
                          :href="attachment.file_url"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <div class="file-attachment-icon">
                            <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20"><path fill-rule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clip-rule="evenodd"/></svg>
                          </div>
                          <div class="file-attachment-meta">
                            <p class="file-attachment-name">
                              {{ attachment.original_name }}
                            </p>
                            <p class="file-attachment-sub">
                              {{ attachment.mime_type || '未知类型' }} · {{ formatFileSize(attachment.file_size) }}
                            </p>
                          </div>
                        </a>
                      </div>

                      <p
                        v-if="
                          !message.content &&
                          getMessageAttachments(message).length === 0 &&
                          message.message_type !== 'text'
                        "
                        class="message-content empty-message-content"
                      >
                        该消息暂无可展示内容
                      </p>
                    </template>
                  </div>

                  <div
                    v-if="canRecallMessage(message)"
                    class="message-actions"
                    :class="{ mine: isMine(message) }"
                  >
                    <button
                      class="recall-btn"
                      type="button"
                      :disabled="recallingMessageId === message.id"
                      @click="handleRecallMessage(message)"
                    >
                      {{ recallingMessageId === message.id ? '撤回中...' : '撤回' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <Transition name="fade-up">
              <button
                v-if="showScrollToBottom"
                class="scroll-to-bottom-btn"
                type="button"
                @click="handleScrollToBottom"
              >
                <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
                {{ hasUnreadIncoming ? '有新消息' : '回到底部' }}
              </button>
            </Transition>
          </div>
        </template>

        <div v-else class="message-empty welcome-empty">
          <div class="welcome-icon">
            <svg viewBox="0 0 64 64" fill="none" width="64" height="64">
              <circle cx="32" cy="32" r="30" stroke="currentColor" stroke-width="1.5" opacity="0.15"/>
              <path d="M20 28c0-5.5 5.4-10 12-10s12 4.5 12 10-5.4 10-12 10c-1.5 0-3-.2-4.4-.6L22 40l1.4-4.3C21.3 33.7 20 31 20 28z" stroke="currentColor" stroke-width="1.8" fill="none" opacity="0.35"/>
            </svg>
          </div>
          <p class="welcome-text">选择一个房间开始聊天</p>
        </div>
      </section>

      <footer class="message-composer" v-if="roomStore.selectedRoom">
        <div class="composer-box">
          <div class="composer-input-row">
            <textarea
              v-model="draftMessage"
              class="composer-input"
              :placeholder="composerPlaceholder"
              @keydown="handleComposerKeydown"
            ></textarea>
          </div>

          <input
            ref="fileInputRef"
            class="file-input-hidden"
            type="file"
            @change="handleFileChange"
          />

          <div class="composer-actions">
            <div class="composer-feedback">
              <p v-if="sendError" class="send-error">
                {{ sendError }}
              </p>
              <p v-else-if="uploading" class="send-pending">
                正在上传文件，完成后自动发送
              </p>
              <p v-else-if="sending" class="send-pending">
                等待服务器确认...
              </p>
              <p v-else class="send-hint">
                Enter 发送 · Shift+Enter 换行
              </p>
            </div>

            <div class="composer-buttons">
              <button
                class="upload-btn"
                type="button"
                :disabled="wsStatus !== 'connected' || uploading || sending"
                @click="handlePickFile"
                title="上传文件或图片"
              >
                <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path fill-rule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clip-rule="evenodd"/></svg>
                <span class="upload-label">{{ uploading ? '上传中...' : '文件' }}</span>
              </button>

              <button
                v-if="wsStatus !== 'connected'"
                class="reconnect-btn"
                type="button"
                @click="handleReconnect"
              >
                重新连接
              </button>

              <button
                class="send-btn"
                :disabled="!canSend"
                @click="handleSendMessage"
              >
                <svg v-if="!sending" viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/></svg>
                <span v-else class="spinner-tiny"></span>
              </button>
            </div>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import http from '../lib/http'
import { useAuthStore } from '../stores/auth'
import { useRoomStore } from '../stores/room'
import { useMessageStore } from '../stores/message'

const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()
const messageStore = useMessageStore()

const messageScrollRef = ref(null)
const fileInputRef = ref(null)

const draftMessage = ref('')
const sendError = ref('')
const sending = ref(false)
const uploading = ref(false)
const recallingMessageId = ref(null)

const sidebarOpen = ref(false)

const pendingMessageText = ref('')
const pendingAttachmentStoredName = ref('')
const pendingAckTimer = ref(null)

const wsRef = ref(null)
const wsStatus = ref('idle')

const isNearBottom = ref(true)
const showScrollToBottom = ref(false)
const hasUnreadIncoming = ref(false)

const userInitial = computed(() => {
  const username = authStore.user?.username || 'M'
  return username.charAt(0).toUpperCase()
})

const currentMessages = computed(() => {
  const roomId = roomStore.selectedRoomId
  if (!roomId) {
    return []
  }

  return messageStore.getMessagesByRoom(roomId)
})

const isCurrentRoomLoading = computed(() => {
  const roomId = roomStore.selectedRoomId
  if (!roomId) {
    return false
  }

  return messageStore.isRoomLoading(roomId)
})

const canSend = computed(() => {
  return (
    !!roomStore.selectedRoomId &&
    !!draftMessage.value.trim() &&
    wsStatus.value === 'connected' &&
    !sending.value &&
    !uploading.value
  )
})

const composerPlaceholder = computed(() => {
  if (uploading.value) {
    return '文件上传中，请稍候...'
  }

  if (wsStatus.value === 'connected') {
    return '输入消息...'
  }

  if (wsStatus.value === 'connecting') {
    return '实时连接建立中，请稍候...'
  }

  return '实时连接未就绪，请先重新连接'
})

const wsStatusText = computed(() => {
  switch (wsStatus.value) {
    case 'connecting':
      return '连接中'
    case 'connected':
      return '已连接'
    case 'error':
      return '连接异常'
    case 'closed':
      return '已断开'
    default:
      return '未连接'
  }
})

const wsStatusClass = computed(() => wsStatus.value)

function clearPendingAckTimer() {
  if (pendingAckTimer.value) {
    clearTimeout(pendingAckTimer.value)
    pendingAckTimer.value = null
  }
}

function resetPendingSendState() {
  sending.value = false
  pendingMessageText.value = ''
  pendingAttachmentStoredName.value = ''
  clearPendingAckTimer()
}

function getRoomInitial(room) {
  const name = room.display_name || 'R'
  return name.charAt(0).toUpperCase()
}

function isMine(message) {
  return message.sender_id === authStore.user?.id
}

function getSenderLabel(message) {
  if (isMine(message)) {
    return '我'
  }

  if (message.sender_username) {
    return message.sender_username
  }

  return `用户 #${message.sender_id}`
}

function canRecallMessage(message) {
  return (
    !!message &&
    !message.is_recalled &&
    isMine(message)
  )
}

function formatTime(isoString) {
  if (!isoString) {
    return ''
  }

  const date = new Date(isoString)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

function getMessageAttachments(message) {
  if (!message || !Array.isArray(message.attachments)) {
    return []
  }

  return message.attachments
}

function getImageAttachments(message) {
  return getMessageAttachments(message).filter(
    (attachment) => attachment.attachment_type === 'image'
  )
}

function getFileAttachments(message) {
  return getMessageAttachments(message).filter(
    (attachment) => attachment.attachment_type === 'file'
  )
}

function formatFileSize(size) {
  const bytes = Number(size) || 0

  if (bytes < 1024) {
    return `${bytes} B`
  }

  const kb = bytes / 1024
  if (kb < 1024) {
    return `${kb >= 100 ? kb.toFixed(0) : kb.toFixed(1)} KB`
  }

  const mb = kb / 1024
  if (mb < 1024) {
    return `${mb >= 100 ? mb.toFixed(0) : mb.toFixed(1)} MB`
  }

  const gb = mb / 1024
  return `${gb >= 100 ? gb.toFixed(0) : gb.toFixed(1)} GB`
}

function isPendingMessageConfirmed(message) {
  const expectedContent = pendingMessageText.value
  const expectedStoredName = pendingAttachmentStoredName.value

  if (!expectedContent && !expectedStoredName) {
    return false
  }

  const contentMatched = expectedContent
    ? (message.content || '') === expectedContent
    : true

  const attachmentMatched = expectedStoredName
    ? getMessageAttachments(message).some(
        (attachment) => attachment.stored_name === expectedStoredName
      )
    : true

  return contentMatched && attachmentMatched
}

function computeIsNearBottom() {
  const el = messageScrollRef.value
  if (!el) {
    return true
  }

  const threshold = 80
  return el.scrollHeight - el.scrollTop - el.clientHeight <= threshold
}

function updateScrollState() {
  const near = computeIsNearBottom()
  isNearBottom.value = near

  if (near) {
    showScrollToBottom.value = false
    hasUnreadIncoming.value = false
  } else {
    showScrollToBottom.value = true
  }
}

async function scrollMessagesToBottom(behavior = 'auto') {
  await nextTick()

  const el = messageScrollRef.value
  if (!el) {
    return
  }

  el.scrollTo({
    top: el.scrollHeight,
    behavior,
  })

  isNearBottom.value = true
  showScrollToBottom.value = false
  hasUnreadIncoming.value = false
}

function handleMessageScroll() {
  updateScrollState()
}

function handleScrollToBottom() {
  scrollMessagesToBottom('smooth')
}

function resetRoomScrollState() {
  isNearBottom.value = true
  showScrollToBottom.value = false
  hasUnreadIncoming.value = false
}

function disconnectWebSocket() {
  if (wsRef.value) {
    wsRef.value.close()
    wsRef.value = null
  }
}

function connectWebSocket(roomId) {
  disconnectWebSocket()
  resetPendingSendState()
  uploading.value = false
  sendError.value = ''

  const token = authStore.token
  if (!roomId || !token) {
    wsStatus.value = 'idle'
    return
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsUrl = `${protocol}://${window.location.host}/ws/rooms/${roomId}?token=${encodeURIComponent(token)}`

  wsStatus.value = 'connecting'

  const ws = new WebSocket(wsUrl)
  wsRef.value = ws

  ws.onopen = () => {
    wsStatus.value = 'connected'
  }

  ws.onmessage = async (event) => {
    try {
      const payload = JSON.parse(event.data)

      if (payload.event === 'connected' || payload.event === 'pong') {
        return
      }

      if (payload.event === 'error') {
        resetPendingSendState()
        uploading.value = false
        sendError.value = payload?.data?.message || '实时消息发生错误'
        return
      }

      if (payload.event === 'message_recalled') {
        const recalledMessage = payload.data

        messageStore.appendOrUpdateMessage(roomId, {
          id: recalledMessage.id,
          room_id: recalledMessage.room_id,
          sender_id: recalledMessage.sender_id,
          is_recalled: true,
          recalled_at: recalledMessage.recalled_at,
        })

        return
      }

      if (payload.event === 'new_message') {
        const message = payload.data
        const mine = isMine(message)
        const shouldStickToBottom = isNearBottom.value || mine

        messageStore.appendOrUpdateMessage(roomId, message)

        await nextTick()

        if (shouldStickToBottom) {
          await scrollMessagesToBottom(mine ? 'smooth' : 'auto')
        } else {
          showScrollToBottom.value = true
          hasUnreadIncoming.value = true
          updateScrollState()
        }

        if (mine && isPendingMessageConfirmed(message)) {
          draftMessage.value = ''
          sendError.value = ''
          resetPendingSendState()
        }
      }
    } catch (error) {
      console.error('解析 WebSocket 消息失败:', error)
    }
  }

  ws.onerror = () => {
    wsStatus.value = 'error'
  }

  ws.onclose = () => {
    if (wsRef.value === ws) {
      wsRef.value = null
      wsStatus.value = 'closed'
    }
  }
}

async function loadCurrentRoomMessages() {
  if (!roomStore.selectedRoomId) {
    return
  }

  try {
    await messageStore.fetchRoomMessages(roomStore.selectedRoomId)
    resetRoomScrollState()
    await scrollMessagesToBottom('auto')
  } catch (error) {
    console.error('获取消息列表失败:', error)
  }
}

async function handleRefreshRooms() {
  try {
    await roomStore.fetchMyRooms()
  } catch (error) {
    console.error('获取房间列表失败:', error)
  }
}

function handleSelectRoom(roomId) {
  roomStore.selectRoom(roomId)
}

function handleLogout() {
  disconnectWebSocket()
  resetPendingSendState()
  uploading.value = false
  authStore.logout()
  roomStore.clearRooms()
  messageStore.clearMessages()
  router.push('/login')
}

function handleComposerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSendMessage()
  }
}

function handleReconnect() {
  if (!roomStore.selectedRoomId) {
    return
  }

  connectWebSocket(roomStore.selectedRoomId)
}

function handlePickFile() {
  if (!roomStore.selectedRoomId) {
    return
  }

  if (wsStatus.value !== 'connected') {
    sendError.value = '实时连接未建立，暂时无法发送附件'
    return
  }

  if (uploading.value || sending.value) {
    return
  }

  fileInputRef.value?.click()
}

async function uploadAttachment(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await http.post('/uploads', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data.data
}

async function handleFileChange(event) {
  const file = event.target.files?.[0]

  if (!file) {
    return
  }

  try {
    await handleUploadAndSendAttachment(file)
  } finally {
    event.target.value = ''
  }
}

async function handleUploadAndSendAttachment(file) {
  const ws = wsRef.value
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    sendError.value = '实时连接未建立，暂时无法发送附件'
    return
  }

  uploading.value = true
  sendError.value = ''

  try {
    const attachment = await uploadAttachment(file)
    const currentContent = draftMessage.value.trim()
    const messageType = attachment.attachment_type === 'image' ? 'image' : 'file'

    const currentWs = wsRef.value
    if (!currentWs || currentWs.readyState !== WebSocket.OPEN) {
      sendError.value = '文件已上传成功，但实时连接已断开，请重连后重试'
      return
    }

    sending.value = true
    pendingMessageText.value = currentContent
    pendingAttachmentStoredName.value = attachment.stored_name
    clearPendingAckTimer()

    currentWs.send(
      JSON.stringify({
        action: 'send_message',
        data: {
          message_type: messageType,
          content: currentContent,
          attachments: [attachment],
        },
      })
    )

    pendingAckTimer.value = setTimeout(() => {
      if (
        sending.value &&
        pendingAttachmentStoredName.value === attachment.stored_name
      ) {
        sending.value = false
        pendingAttachmentStoredName.value = ''
        sendError.value = '暂未收到服务器确认，文件已上传，但消息发送未确认，请检查连接后重试'
      }
    }, 5000)
  } catch (error) {
    console.error('上传附件失败:', error)
    resetPendingSendState()
    sendError.value =
      error?.response?.data?.detail || '文件上传失败，请稍后重试'
  } finally {
    uploading.value = false
  }
}

async function handleSendMessage() {
  const content = draftMessage.value.trim()

  if (!content) {
    return
  }

  const ws = wsRef.value
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    sendError.value = '实时连接未建立，暂时无法发送消息'
    return
  }

  try {
    sending.value = true
    sendError.value = ''
    pendingMessageText.value = content
    pendingAttachmentStoredName.value = ''
    clearPendingAckTimer()

    ws.send(
      JSON.stringify({
        action: 'send_message',
        data: {
          message_type: 'text',
          content,
          attachments: [],
        },
      })
    )

    pendingAckTimer.value = setTimeout(() => {
      if (sending.value && pendingMessageText.value === content) {
        sending.value = false
        sendError.value = '暂未收到服务器确认，输入内容已保留，请检查连接后重试'
      }
    }, 5000)
  } catch (error) {
    console.error('发送 WebSocket 消息失败:', error)
    resetPendingSendState()
    sendError.value = '发送失败，请稍后重试'
  }
}

async function handleRecallMessage(message) {
  if (!message || !canRecallMessage(message)) {
    return
  }

  if (recallingMessageId.value) {
    return
  }

  try {
    recallingMessageId.value = message.id
    sendError.value = ''

    await http.post(`/messages/${message.id}/recall`)
  } catch (error) {
    console.error('撤回消息失败:', error)
    sendError.value =
      error?.response?.data?.detail || '撤回失败，请稍后重试'
  } finally {
    recallingMessageId.value = null
  }
}

watch(
  () => roomStore.selectedRoomId,
  async (newRoomId, oldRoomId) => {
    if (!newRoomId) {
      disconnectWebSocket()
      return
    }

    if (newRoomId === oldRoomId) {
      return
    }

    resetPendingSendState()
    uploading.value = false
    sendError.value = ''
    draftMessage.value = ''
    resetRoomScrollState()

    await loadCurrentRoomMessages()
    connectWebSocket(newRoomId)
  }
)

onMounted(async () => {
  try {
    await roomStore.fetchMyRooms()
    await loadCurrentRoomMessages()
    connectWebSocket(roomStore.selectedRoomId)
  } catch (error) {
    console.error('初始化聊天页失败:', error)
  }
})

onBeforeUnmount(() => {
  disconnectWebSocket()
  resetPendingSendState()
})
</script>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700&family=Outfit:wght@600;700;800&display=swap');

/* ========== TOKENS ========== */
.chat-page {
  --c-orange: #f97316;
  --c-orange-hover: #ea580c;
  --c-orange-subtle: #fff7ed;
  --c-orange-border: #fed7aa;
  --c-cyan: #06b6d4;
  --c-cyan-deep: #0891b2;
  --c-cyan-subtle: #ecfeff;
  --c-cyan-border: #a5f3fc;
  --c-sidebar-bg: #0c1222;
  --c-sidebar-surface: rgba(255,255,255,0.05);
  --c-sidebar-text: rgba(255,255,255,0.7);
  --c-sidebar-text-dim: rgba(255,255,255,0.35);
  --c-main-bg: #f0f4f8;
  --c-surface: #ffffff;
  --c-text: #0f172a;
  --c-text-secondary: #64748b;
  --c-border: #e2e8f0;
  --c-danger: #ef4444;
  --radius-lg: 18px;
  --radius-md: 14px;
  --radius-sm: 10px;

  display: flex;
  height: 100vh;
  min-height: 100vh;
  background: var(--c-main-bg);
  overflow: hidden;
  font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
  color: var(--c-text);
}

/* ========== SIDEBAR ========== */
.sidebar {
  width: 320px;
  padding: 20px 16px;
  background: var(--c-sidebar-bg);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  min-width: 0;
  overflow: hidden;
  position: relative;
  z-index: 20;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 1px;
    background: linear-gradient(180deg, rgba(6,182,212,0.3) 0%, rgba(249,115,22,0.3) 100%);
  }
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding: 0 4px;

  h2 {
    margin: 0;
    font-family: 'Outfit', sans-serif;
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--c-orange) 30%, var(--c-cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .muted {
    margin: 2px 0 0;
    color: var(--c-sidebar-text-dim);
    font-size: 11px;
    letter-spacing: 0.03em;
  }
}

.brand-logo {
  width: 36px;
  height: 36px;
  flex-shrink: 0;

  svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 2px 8px rgba(249,115,22,0.3));
  }
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: var(--radius-md);
  background: var(--c-sidebar-surface);
  border: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 20px;
  position: relative;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--c-orange), var(--c-cyan));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Outfit', sans-serif;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-online-dot {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34,197,94,0.5);
}

.user-meta {
  min-width: 0;
  flex: 1;

  .username {
    margin: 0 0 2px;
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    word-break: break-word;
  }

  .role {
    margin: 0;
    color: var(--c-sidebar-text-dim);
    font-size: 12px;
  }
}

/* ---- Room list ---- */
.room-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.room-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 0 4px;

  h3 {
    margin: 0;
    font-size: 11px;
    font-weight: 700;
    color: var(--c-sidebar-text-dim);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }
}

.refresh-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: var(--c-sidebar-surface);
  color: var(--c-sidebar-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;

  &:hover:not(:disabled) {
    background: rgba(255,255,255,0.1);
    color: var(--c-cyan);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.room-empty {
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--c-sidebar-surface);
  color: var(--c-sidebar-text-dim);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.room-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
  padding-right: 4px;
  min-width: 0;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
  }
}

.room-item {
  width: 100%;
  border: 1px solid transparent;
  background: transparent;
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  gap: 12px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 0;
  color: inherit;

  &:hover {
    background: var(--c-sidebar-surface);
  }

  &.active {
    background: rgba(6,182,212,0.1);
    border-color: rgba(6,182,212,0.2);
  }
}

.room-avatar {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Outfit', sans-serif;
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;

  &.private {
    background: linear-gradient(135deg, var(--c-cyan), #0e7490);
  }

  &.group {
    background: linear-gradient(135deg, var(--c-orange), #c2410c);
  }
}

.room-info {
  flex: 1;
  min-width: 0;
}

.room-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  min-width: 0;
}

.room-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-type-badge {
  padding: 1px 7px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  flex-shrink: 0;
  letter-spacing: 0.02em;

  &.private {
    background: rgba(6,182,212,0.15);
    color: var(--c-cyan);
  }

  &.group {
    background: rgba(249,115,22,0.15);
    color: var(--c-orange);
  }
}

.room-bottom {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 11px;
  color: var(--c-sidebar-text-dim);
}

.room-role {
  color: rgba(6,182,212,0.7);
}

.logout-btn {
  margin-top: 12px;
  height: 40px;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--c-sidebar-text);
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.2s, color 0.2s;

  &:hover {
    background: rgba(239,68,68,0.1);
    color: #fca5a5;
    border-color: rgba(239,68,68,0.2);
  }
}

/* ========== MAIN AREA ========== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.chat-header {
  padding: 18px 28px;
  background: var(--c-surface);
  border-bottom: 1px solid var(--c-border);

  h2 {
    margin: 0 0 4px;
    color: var(--c-text);
    font-family: 'Outfit', sans-serif;
    font-size: 20px;
    font-weight: 700;
  }

  p {
    margin: 0;
    color: var(--c-text-secondary);
    font-size: 13px;
    line-height: 1.5;
  }
}

.chat-header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.chat-header-text {
  min-width: 0;
}

.empty-header h2 {
  margin-bottom: 4px;
}

.ws-status {
  flex-shrink: 0;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;

  .ws-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  &.idle .ws-dot,
  &.closed .ws-dot {
    background: #94a3b8;
  }

  &.connecting .ws-dot {
    background: #f59e0b;
    animation: pulse-dot 1.2s ease-in-out infinite;
  }

  &.connected .ws-dot {
    background: #22c55e;
    box-shadow: 0 0 4px rgba(34,197,94,0.5);
  }

  &.error .ws-dot {
    background: var(--c-danger);
  }

  &.idle, &.closed {
    background: #f1f5f9;
    color: #64748b;
  }

  &.connecting {
    background: #fffbeb;
    color: #b45309;
  }

  &.connected {
    background: #f0fdf4;
    color: #15803d;
  }

  &.error {
    background: #fef2f2;
    color: #b91c1c;
  }
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ========== MESSAGE LIST ========== */
.message-list {
  flex: 1 1 0;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--c-main-bg);
}

.message-area {
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1 1 0;
  min-height: 0;
}

.message-empty {
  margin: 24px;
  padding: 32px 24px;
  border-radius: var(--radius-lg);
  background: var(--c-surface);
  color: var(--c-text-secondary);
  box-shadow: 0 1px 3px rgba(15,23,42,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.welcome-empty {
  flex: 1;
  margin: 24px;
  justify-content: center;
}

.welcome-icon {
  color: var(--c-text-secondary);
}

.welcome-text {
  margin: 0;
  font-size: 15px;
  color: var(--c-text-secondary);
}

.message-scroll {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px 28px;

  &::-webkit-scrollbar {
    width: 5px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(0,0,0,0.08);
    border-radius: 3px;
  }
}

.scroll-to-bottom-btn {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: 12px;
  border: none;
  border-radius: 999px;
  padding: 8px 18px;
  background: var(--c-sidebar-bg);
  color: #fff;
  font-family: inherit;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(15,23,42,0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 5;
}

.fade-up-enter-active,
.fade-up-leave-active {
  transition: all 0.25s ease;
}
.fade-up-enter-from,
.fade-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(8px);
}

/* ---- Message rows ---- */
.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;

  &.mine {
    flex-direction: row-reverse;

    .message-body {
      align-items: flex-end;
    }

    .message-meta {
      flex-direction: row-reverse;
    }
  }
}

.message-avatar-col {
  flex-shrink: 0;
  padding-top: 20px;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--c-cyan), var(--c-cyan-deep));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Outfit', sans-serif;
  font-size: 13px;
  font-weight: 700;
}

.message-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: min(72%, 540px);
  min-width: 0;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 11px;
  color: #94a3b8;

  .sender {
    font-weight: 600;
    color: var(--c-text-secondary);
  }
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 16px 16px 16px 4px;
  background: var(--c-surface);
  color: var(--c-text);
  box-shadow: 0 1px 3px rgba(15,23,42,0.05);
  border: 1px solid var(--c-border);
  word-break: break-word;

  &.mine {
    background: linear-gradient(135deg, var(--c-orange) 0%, var(--c-orange-hover) 100%);
    color: #fff;
    border-color: transparent;
    border-radius: 16px 16px 4px 16px;
    box-shadow: 0 2px 8px rgba(249,115,22,0.2);
  }

  &.recalled {
    background: var(--c-main-bg);
    color: #94a3b8;
    border-style: dashed;
    border-color: var(--c-border);
  }
}

.message-actions {
  display: flex;
  margin-top: 4px;

  &.mine {
    justify-content: flex-end;
  }
}

.recall-btn {
  border: none;
  background: transparent;
  color: #94a3b8;
  font-family: inherit;
  font-size: 11px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;

  &:hover:enabled {
    color: var(--c-danger);
    background: rgba(239,68,68,0.06);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.reply-tip {
  margin: 0 0 6px;
  font-size: 11px;
  opacity: 0.7;
  padding: 4px 8px;
  background: rgba(0,0,0,0.05);
  border-radius: 6px;
  display: inline-block;
}

.mine .reply-tip {
  background: rgba(255,255,255,0.15);
}

.message-content,
.recalled-text {
  margin: 0;
  line-height: 1.65;
  font-size: 14px;
  word-break: break-word;
}

.empty-message-content {
  opacity: 0.65;
}

/* ---- Attachments ---- */
.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.image-list {
  max-width: 100%;
}

.image-attachment-link {
  display: block;
  width: fit-content;
  max-width: min(260px, 100%);
  border-radius: 12px;
  overflow: hidden;
}

.image-attachment-preview {
  display: block;
  width: 100%;
  max-width: 260px;
  max-height: 300px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(226,232,240,0.8);
  background: var(--c-main-bg);
}

.message-bubble.mine .image-attachment-preview {
  border-color: rgba(255,255,255,0.2);
}

.file-attachment-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  background: rgba(248,250,252,0.9);
  border: 1px solid var(--c-border);
  transition: transform 0.15s, box-shadow 0.15s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(15,23,42,0.08);
  }
}

.message-bubble.mine .file-attachment-card {
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.18);
}

.file-attachment-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--c-cyan-subtle);
  color: var(--c-cyan-deep);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-bubble.mine .file-attachment-icon {
  background: rgba(255,255,255,0.15);
  color: #fff;
}

.file-attachment-meta {
  min-width: 0;
  flex: 1;
}

.file-attachment-name {
  margin: 0 0 2px;
  font-size: 13px;
  font-weight: 600;
  word-break: break-word;
}

.file-attachment-sub {
  margin: 0;
  font-size: 11px;
  opacity: 0.7;
  word-break: break-word;
}

/* ========== COMPOSER ========== */
.message-composer {
  flex-shrink: 0;
  padding: 14px 24px 18px;
  background: var(--c-surface);
  border-top: 1px solid var(--c-border);
}

.composer-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-input-hidden {
  display: none;
}

.composer-input-row {
  position: relative;
}

.composer-input {
  width: 100%;
  min-height: 48px;
  max-height: 160px;
  resize: none;
  border: 1.5px solid var(--c-border);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: var(--c-text);
  outline: none;
  box-sizing: border-box;
  background: var(--c-main-bg);
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;

  &::placeholder {
    color: #94a3b8;
  }

  &:focus {
    border-color: var(--c-cyan);
    background: var(--c-surface);
    box-shadow: 0 0 0 3px rgba(6,182,212,0.1);
  }
}

.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.composer-feedback {
  flex: 1;
  min-width: 0;
}

.send-error,
.send-pending,
.send-hint {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
}

.send-error {
  color: var(--c-danger);
}

.send-pending {
  color: #b45309;
}

.send-hint {
  color: #94a3b8;
}

.composer-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.upload-btn {
  height: 40px;
  padding: 0 14px;
  border: 1.5px solid var(--c-border);
  border-radius: var(--radius-sm);
  background: var(--c-surface);
  color: var(--c-text-secondary);
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: border-color 0.2s, color 0.2s;

  &:hover:not(:disabled) {
    border-color: var(--c-cyan);
    color: var(--c-cyan-deep);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.reconnect-btn {
  height: 40px;
  padding: 0 16px;
  border: 1.5px solid var(--c-border);
  border-radius: var(--radius-sm);
  background: var(--c-surface);
  color: var(--c-text-secondary);
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.2s;

  &:hover {
    border-color: var(--c-orange);
    color: var(--c-orange);
  }
}

.send-btn {
  width: 44px;
  height: 40px;
  border: none;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--c-orange) 0%, var(--c-orange-hover) 100%);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s;
  box-shadow: 0 2px 8px rgba(249,115,22,0.25);

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(249,115,22,0.35);
  }

  &:disabled {
    opacity: 0.45;
    cursor: not-allowed;
    box-shadow: none;
  }
}

/* ========== SPINNERS ========== */
.spinner {
  width: 24px;
  height: 24px;
  border: 2.5px solid var(--c-border);
  border-top-color: var(--c-cyan);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.spinner-tiny {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.25);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ========== MOBILE ========== */
.mobile-menu-btn {
  display: none;
}

.sidebar-overlay {
  display: none;
}

@media (max-width: 900px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 300px;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 100;
    box-shadow: none;

    &.open {
      transform: translateX(0);
      box-shadow: 8px 0 30px rgba(0,0,0,0.3);
    }
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 99;
    background: rgba(0,0,0,0.4);
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
    animation: fade-in 0.2s ease;
  }

  @keyframes fade-in {
    from { opacity: 0; }
  }

  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 30;
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 12px;
    background: var(--c-surface);
    box-shadow: 0 2px 10px rgba(15,23,42,0.1);
    color: var(--c-text);
    cursor: pointer;

    svg {
      width: 20px;
      height: 20px;
    }
  }

  .chat-header {
    padding: 16px 16px 16px 64px;
  }

  .message-scroll {
    padding: 16px;
  }

  .message-composer {
    padding: 12px 16px 16px;
  }

  .message-body {
    max-width: 85%;
  }
}

@media (max-width: 640px) {
  .chat-header {
    h2 { font-size: 18px; }
    p { font-size: 12px; }
  }

  .chat-header-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .message-scroll {
    padding: 12px;
    gap: 6px;
  }

  .message-body {
    max-width: 88%;
  }

  .message-bubble {
    padding: 9px 12px;
    border-radius: 14px 14px 14px 4px;

    &.mine {
      border-radius: 14px 14px 4px 14px;
    }
  }

  .message-meta {
    font-size: 10px;
  }

  .msg-avatar {
    width: 28px;
    height: 28px;
    font-size: 11px;
    border-radius: 8px;
  }

  .composer-input {
    min-height: 44px;
    font-size: 14px;
    padding: 10px 14px;
  }

  .composer-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .composer-buttons {
    width: 100%;
    justify-content: flex-end;
  }

  .upload-label {
    display: none;
  }

  .upload-btn {
    width: 40px;
    padding: 0;
    justify-content: center;
  }
}
</style>