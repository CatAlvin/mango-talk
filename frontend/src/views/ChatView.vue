<template>
  <div class="chat-page">
    <aside class="sidebar">
      <div class="brand-block">
        <h2>Mango Talk</h2>
        <p class="muted">Version 0.4 前端联调阶段</p>
      </div>

      <div class="user-card">
        <div class="avatar">
          {{ userInitial }}
        </div>
        <div class="user-meta">
          <p class="username">{{ authStore.user?.username || '未登录用户' }}</p>
          <p class="role">角色：{{ authStore.user?.role || 'unknown' }}</p>
        </div>
      </div>

      <div class="room-section">
        <div class="room-section-header">
          <h3>我的房间</h3>
          <button class="refresh-btn" @click="handleRefreshRooms" :disabled="roomStore.loading">
            {{ roomStore.loading ? '加载中...' : '刷新' }}
          </button>
        </div>

        <div v-if="roomStore.loading && roomStore.rooms.length === 0" class="room-empty">
          正在加载房间列表...
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
            @click="handleSelectRoom(room.id)"
          >
            <div class="room-avatar">
              {{ getRoomInitial(room) }}
            </div>

            <div class="room-info">
              <div class="room-top">
                <p class="room-name">{{ room.display_name }}</p>
                <span class="room-type" :class="room.type">
                  {{ room.type === 'private' ? '私聊' : '群聊' }}
                </span>
              </div>

              <div class="room-bottom">
                <span>{{ room.member_count }} 人</span>
                <span>我的角色：{{ room.my_role }}</span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <button class="logout-btn" @click="handleLogout">
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
                类型：{{ roomStore.selectedRoom.type === 'private' ? '私聊' : '群聊' }}
                · 成员数：{{ roomStore.selectedRoom.member_count }}
                · 我的角色：{{ roomStore.selectedRoom.my_role }}
              </p>
            </div>

            <div class="ws-status" :class="wsStatusClass">
              {{ wsStatusText }}
            </div>
          </div>
        </template>

        <template v-else>
          <h2>聊天主页</h2>
          <p>请先从左侧选择一个房间</p>
        </template>
      </header>

      <section class="message-list">
        <template v-if="roomStore.selectedRoom">
          <div v-if="isCurrentRoomLoading" class="message-empty">
            正在加载消息记录...
          </div>

          <div v-else-if="currentMessages.length === 0" class="message-empty">
            当前房间还没有消息
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

                  <p v-else class="message-content">
                    {{ message.content }}
                  </p>
                </div>
              </div>
            </div>

            <button
              v-if="showScrollToBottom"
              class="scroll-to-bottom-btn"
              type="button"
              @click="handleScrollToBottom"
            >
              {{ hasUnreadIncoming ? '有新消息，回到底部' : '回到底部' }}
            </button>
          </div>
        </template>

        <div v-else class="message-empty">
          请先从左侧选择一个房间
        </div>
      </section>

      <footer class="message-composer" v-if="roomStore.selectedRoom">
        <div class="composer-box">
          <textarea
            v-model="draftMessage"
            class="composer-input"
            :placeholder="composerPlaceholder"
            @keydown="handleComposerKeydown"
          ></textarea>

          <div class="composer-actions">
            <div class="composer-feedback">
              <p v-if="sendError" class="send-error">
                {{ sendError }}
              </p>
              <p v-else-if="sending" class="send-pending">
                正在等待服务器确认，这条消息确认成功后才会清空输入框
              </p>
              <p v-else class="send-hint">
                Enter 发送，Shift + Enter 换行
              </p>
            </div>

            <div class="composer-buttons">
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
                {{ sending ? '等待确认...' : '发送' }}
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
import { useAuthStore } from '../stores/auth'
import { useRoomStore } from '../stores/room'
import { useMessageStore } from '../stores/message'

const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()
const messageStore = useMessageStore()

const messageScrollRef = ref(null)
const draftMessage = ref('')
const sendError = ref('')
const sending = ref(false)
const pendingMessageText = ref('')
const pendingAckTimer = ref(null)

const wsRef = ref(null)
const wsStatus = ref('idle') // idle | connecting | connected | error | closed

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
    !sending.value
  )
})

const composerPlaceholder = computed(() => {
  if (wsStatus.value === 'connected') {
    return '输入消息，按 Enter 发送，Shift + Enter 换行'
  }

  if (wsStatus.value === 'connecting') {
    return '实时连接建立中，请稍候...'
  }

  return '实时连接未就绪，请先重新连接'
})

const wsStatusText = computed(() => {
  switch (wsStatus.value) {
    case 'connecting':
      return '实时连接中'
    case 'connected':
      return '实时已连接'
    case 'error':
      return '连接异常'
    case 'closed':
      return '连接已关闭'
    default:
      return '未连接'
  }
})

const wsStatusClass = computed(() => {
  return wsStatus.value
})

function clearPendingAckTimer() {
  if (pendingAckTimer.value) {
    clearTimeout(pendingAckTimer.value)
    pendingAckTimer.value = null
  }
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

function formatTime(isoString) {
  if (!isoString) {
    return ''
  }

  const date = new Date(isoString)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
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
  clearPendingAckTimer()
  sending.value = false
  pendingMessageText.value = ''
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

      if (payload.event === 'connected') {
        return
      }

      if (payload.event === 'pong') {
        return
      }

      if (payload.event === 'error') {
        sending.value = false
        clearPendingAckTimer()
        sendError.value = payload?.data?.message || '实时消息发生错误'
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

        if (
          mine &&
          pendingMessageText.value &&
          message.content === pendingMessageText.value
        ) {
          draftMessage.value = ''
          sendError.value = ''
          sending.value = false
          pendingMessageText.value = ''
          clearPendingAckTimer()
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
  clearPendingAckTimer()
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
    clearPendingAckTimer()

    ws.send(
      JSON.stringify({
        action: 'send_message',
        data: {
          content,
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
    sending.value = false
    pendingMessageText.value = ''
    clearPendingAckTimer()
    sendError.value = '发送失败，请稍后重试'
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

    clearPendingAckTimer()
    sending.value = false
    pendingMessageText.value = ''
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
  clearPendingAckTimer()
})
</script>

<style scoped lang="scss">
.chat-page {
  display: flex;
  height: 100vh;
  min-height: 100vh;
  background: #f8fafc;
  overflow: hidden;
}

.sidebar {
  width: 340px;
  padding: 24px 20px;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  min-width: 0;
}

.brand-block {
  h2 {
    margin: 0;
    font-size: 28px;
    color: #f97316;
  }

  .muted {
    margin: 8px 0 20px;
    color: #94a3b8;
    font-size: 13px;
  }
}

.user-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 18px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  margin-bottom: 18px;
}

.avatar {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: #fb923c;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-meta {
  min-width: 0;

  .username {
    margin: 0 0 6px;
    color: #0f172a;
    font-size: 16px;
    font-weight: 700;
    word-break: break-word;
  }

  .role {
    margin: 0;
    color: #64748b;
    font-size: 14px;
  }
}

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
  gap: 12px;

  h3 {
    margin: 0;
    font-size: 16px;
    color: #0f172a;
  }
}

.refresh-btn {
  height: 32px;
  padding: 0 12px;
  border: none;
  border-radius: 10px;
  background: #f1f5f9;
  color: #334155;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.room-empty {
  padding: 16px;
  border-radius: 14px;
  background: #f8fafc;
  color: #64748b;
  font-size: 14px;
}

.room-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding-right: 4px;
  min-width: 0;
}

.room-item {
  width: 100%;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 16px;
  padding: 14px;
  display: flex;
  gap: 12px;
  text-align: left;
  cursor: pointer;
  transition: all 0.18s ease;
  min-width: 0;

  &:hover {
    border-color: #fdba74;
    box-shadow: 0 8px 18px rgba(249, 115, 22, 0.08);
  }

  &.active {
    border-color: #fb923c;
    background: #fff7ed;
  }
}

.room-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #f97316;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.room-info {
  flex: 1;
  min-width: 0;
}

.room-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  min-width: 0;
}

.room-name {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-type {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  flex-shrink: 0;

  &.private {
    background: #e0f2fe;
    color: #0369a1;
  }

  &.group {
    background: #ede9fe;
    color: #6d28d9;
  }
}

.room-bottom {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: #64748b;
}

.logout-btn {
  margin-top: 18px;
  height: 42px;
  border: none;
  border-radius: 14px;
  background: #0f172a;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.chat-header {
  padding: 24px 28px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;

  h2 {
    margin: 0 0 10px;
    color: #0f172a;
    font-size: 24px;
  }

  p {
    margin: 0;
    color: #64748b;
    line-height: 1.6;
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

.ws-status {
  flex-shrink: 0;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;

  &.idle,
  &.closed {
    background: #e2e8f0;
    color: #475569;
  }

  &.connecting {
    background: #fef3c7;
    color: #b45309;
  }

  &.connected {
    background: #dcfce7;
    color: #15803d;
  }

  &.error {
    background: #fee2e2;
    color: #b91c1c;
  }
}

.message-list {
  flex: 1 1 0;
  padding: 24px 28px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.message-area {
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1 1 0;
  min-height: 0;
}

.message-empty {
  padding: 18px;
  border-radius: 16px;
  background: #fff;
  color: #64748b;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.message-scroll {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-right: 4px;
}

.scroll-to-bottom-btn {
  position: absolute;
  right: 8px;
  bottom: 8px;
  border: none;
  border-radius: 999px;
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.92);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
  cursor: pointer;
}

.message-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  &.mine {
    align-items: flex-end;
  }
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 12px;
  color: #94a3b8;

  .sender {
    font-weight: 600;
    color: #64748b;
  }
}

.message-bubble {
  max-width: min(72%, 560px);
  padding: 12px 14px;
  border-radius: 18px;
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;

  &.mine {
    background: #f97316;
    color: #fff;
    border-color: #f97316;
  }

  &.recalled {
    background: #f8fafc;
    color: #94a3b8;
    border-style: dashed;
  }
}

.reply-tip {
  margin: 0 0 8px;
  font-size: 12px;
  opacity: 0.85;
}

.message-content,
.recalled-text {
  margin: 0;
  line-height: 1.7;
  word-break: break-word;
}

.message-composer {
  flex-shrink: 0;
  padding: 18px 24px 22px;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
}

.composer-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.composer-input {
  width: 100%;
  min-height: 88px;
  resize: vertical;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 14px 16px;
  font-size: 15px;
  line-height: 1.6;
  outline: none;
  box-sizing: border-box;

  &:focus {
    border-color: #fb923c;
    box-shadow: 0 0 0 4px rgba(251, 146, 60, 0.12);
  }
}

.composer-actions {
  display: flex;
  align-items: flex-start;
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
  font-size: 14px;
  line-height: 1.5;
}

.send-error {
  color: #dc2626;
}

.send-pending {
  color: #b45309;
}

.send-hint {
  color: #64748b;
}

.composer-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.reconnect-btn {
  height: 42px;
  min-width: 108px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  background: #fff;
  color: #334155;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.send-btn {
  height: 42px;
  min-width: 108px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;

  &:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
}

@media (max-width: 900px) {
  .chat-page {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
    overflow: auto;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 18px 16px;
  }

  .room-section {
    min-height: auto;
  }

  .room-list {
    flex-direction: row;
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 4px;
    padding-right: 0;
  }

  .room-item {
    min-width: 240px;
    max-width: 280px;
    flex-shrink: 0;
  }

  .logout-btn {
    margin-top: 14px;
  }

  .chat-main {
    min-height: 60vh;
  }

  .chat-header {
    padding: 18px 16px;

    h2 {
      font-size: 22px;
    }
  }

  .message-list {
    padding: 16px;
  }

  .message-composer {
    padding: 14px 16px 18px;
  }

  .message-bubble {
    max-width: 86%;
  }
}

@media (max-width: 640px) {
  .brand-block {
    h2 {
      font-size: 24px;
    }
  }

  .user-card {
    padding: 14px;
  }

  .room-section-header {
    align-items: flex-start;
  }

  .room-item {
    min-width: 220px;
  }

  .chat-header-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .ws-status {
    align-self: flex-start;
  }

  .chat-header {
    h2 {
      font-size: 20px;
    }

    p {
      font-size: 14px;
    }
  }

  .message-list {
    padding: 14px 12px;
  }

  .message-bubble {
    max-width: 92%;
    padding: 10px 12px;
  }

  .message-meta {
    font-size: 11px;
  }

  .message-composer {
    padding: 12px;
  }

  .composer-input {
    min-height: 76px;
    font-size: 14px;
  }

  .composer-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .composer-buttons {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .reconnect-btn,
  .send-btn {
    width: 100%;
  }

  .send-error,
  .send-pending,
  .send-hint {
    font-size: 13px;
  }

  .scroll-to-bottom-btn {
    left: 50%;
    right: auto;
    transform: translateX(-50%);
    bottom: 8px;
    max-width: calc(100% - 24px);
  }
}
</style>
