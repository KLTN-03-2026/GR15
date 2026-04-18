<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { aiChatService, jobService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const emit = defineEmits(['refresh-overview'])

const notify = useNotify()

const profiles = ref([])
const jobs = ref([])
const loadingBootstrap = ref(false)
const loadingChatSessions = ref(false)
const loadingChatMessages = ref(false)
const creatingChatSession = ref(false)
const sendingChatMessage = ref(false)
const streamEnabled = ref(true)
const chatStreaming = ref(false)
const chatStreamStatus = ref('Sẵn sàng')
const chatSidebarCollapsed = ref(false)

const chatSessions = ref([])
const chatMessages = ref([])
const activeChatSessionId = ref(null)
const chatMessageInput = ref('')
const chatMessagesContainer = ref(null)
const chatPanel = ref(null)
const chatComposerInput = ref(null)
const chatSessionForm = ref({
  title: 'Tư vấn nghề nghiệp cùng AI',
  related_ho_so_id: '',
  related_tin_tuyen_dung_id: '',
})

const availableProfiles = computed(() =>
  profiles.value.filter((item) => Number(item.trang_thai) === 1)
)

const activeChatSession = computed(() =>
  chatSessions.value.find((item) => item.id === activeChatSessionId.value) || null
)

const chatSessionOptions = computed(() => chatSessions.value.slice(0, 6))
const hasChatMessages = computed(() => chatMessages.value.length > 0)
const chatCanSend = computed(() => Boolean(activeChatSessionId.value && chatMessageInput.value.trim() && !sendingChatMessage.value))
const chatStatusTone = computed(() =>
  chatStreaming.value
    ? 'bg-blue-500/15 text-blue-200 border-blue-500/30'
    : 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-700'
)

const messageBubbleClass = (role) =>
  role === 'user'
    ? 'ml-auto bg-gradient-to-r from-blue-600 to-indigo-500 text-white border-transparent'
    : 'mr-auto bg-slate-50 border-slate-200 text-slate-900 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-100'

const formatDateTime = (value) => {
  if (!value) return 'Vừa xong'
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

const truncate = (value, max = 120) => {
  if (!value) return ''
  return value.length > max ? `${value.slice(0, max).trim()}...` : value
}

const sortMessagesAscending = (messages = []) =>
  [...messages].sort((a, b) => {
    const timeA = a?.created_at ? new Date(a.created_at).getTime() : 0
    const timeB = b?.created_at ? new Date(b.created_at).getTime() : 0
    if (timeA !== timeB) return timeA - timeB
    return Number(a?.id || 0) - Number(b?.id || 0)
  })

const chatPreview = (session) => {
  if (session.summary) return truncate(session.summary, 100)
  if (session.ho_so?.tieu_de_ho_so) {
    return `Hồ sơ: ${session.ho_so.tieu_de_ho_so}`
  }
  return 'Tư vấn nhanh về hồ sơ, công việc và kỹ năng cần cải thiện.'
}

const getChatIntentLabel = (intent) => {
  switch (intent) {
    case 'job_recommendation':
      return 'Gợi ý công việc'
    case 'matching_explanation':
      return 'Giải thích matching'
    case 'learning_plan':
      return 'Lộ trình học'
    case 'career_direction':
      return 'Định hướng nghề'
    case 'next_step_action':
      return 'Nên làm gì trước'
    case 'cv_improvement':
      return 'Cải thiện CV'
    case 'interview_prep':
      return 'Chuẩn bị phỏng vấn'
    default:
      return 'AI tư vấn'
  }
}

const getChatProviderLabel = (provider) => {
  switch (provider) {
    case 'ollama':
      return 'Sinh bởi Ollama'
    case 'openai':
      return 'Sinh bởi OpenAI'
    case 'intent_template':
      return 'Template theo ý định'
    case 'fast_template':
      return 'Template nhanh'
    case 'template':
      return 'Template sẵn'
    case 'template_fallback':
      return 'Template fallback'
    case 'guardrail':
      return 'Guardrail'
    case 'graceful_stream_fallback':
      return 'Fallback an toàn'
    case 'stream_pending':
      return 'Đang phân tích'
    default:
      return 'AI xử lý'
  }
}

const getChatProviderTone = (provider) => {
  switch (provider) {
    case 'ollama':
      return 'bg-emerald-500/15 text-emerald-200'
    case 'openai':
      return 'bg-cyan-500/15 text-cyan-200'
    case 'intent_template':
    case 'fast_template':
    case 'template':
    case 'template_fallback':
      return 'bg-amber-500/15 text-amber-200'
    case 'guardrail':
    case 'graceful_stream_fallback':
      return 'bg-rose-500/15 text-rose-200'
    default:
      return 'bg-slate-800/80 text-slate-300'
  }
}

const pickDefaultProfile = () => {
  const firstProfileId = availableProfiles.value[0]?.id ? String(availableProfiles.value[0].id) : ''
  const stillValid = availableProfiles.value.some(
    (item) => String(item.id) === String(chatSessionForm.value.related_ho_so_id)
  )

  if (!stillValid) {
    chatSessionForm.value.related_ho_so_id = ''
  }

  if (!chatSessionForm.value.related_ho_so_id) {
    chatSessionForm.value.related_ho_so_id = firstProfileId
  }
}

const scrollChatToBottom = async (behavior = 'smooth') => {
  await nextTick()
  const container = chatMessagesContainer.value
  if (!container) return
  container.scrollTo({
    top: container.scrollHeight,
    behavior,
  })
}

const expandChatPanel = async () => {
  await nextTick()

  chatPanel.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })

  chatComposerInput.value?.focus()
}

const collapseChatSidebar = () => {
  chatSidebarCollapsed.value = true
}

const expandChatSidebar = () => {
  chatSidebarCollapsed.value = false
}

const fetchBootstrapData = async () => {
  loadingBootstrap.value = true
  try {
    const [profilesRes, jobsRes] = await Promise.all([
      profileService.getProfiles({ per_page: 100, sort_by: 'updated_at', sort_dir: 'desc', trang_thai: 1 }),
      jobService.getJobs({ per_page: 30, page: 1 }),
    ])

    profiles.value = profilesRes?.data?.data || []
    jobs.value = jobsRes?.data?.data || []
    pickDefaultProfile()
  } catch (error) {
    notify.apiError(error, 'Không tải được dữ liệu nền cho chatbot AI.')
  } finally {
    loadingBootstrap.value = false
  }
}

const fetchChatSessions = async () => {
  loadingChatSessions.value = true
  try {
    const response = await aiChatService.getSessions()
    chatSessions.value = response?.data || []

    if (!activeChatSessionId.value && chatSessions.value.length) {
      await selectChatSession(chatSessions.value[0].id)
    } else if (activeChatSessionId.value) {
      const stillExists = chatSessions.value.some((item) => item.id === activeChatSessionId.value)
      if (!stillExists) {
        activeChatSessionId.value = null
        chatMessages.value = []
      }
    }
  } catch (error) {
    notify.apiError(error, 'Không tải được danh sách phiên chatbot.')
  } finally {
    loadingChatSessions.value = false
  }
}

const selectChatSession = async (sessionId) => {
  activeChatSessionId.value = sessionId
  loadingChatMessages.value = true
  try {
    const response = await aiChatService.getMessages(sessionId)
    chatMessages.value = sortMessagesAscending(response?.data || [])
    chatStreamStatus.value = 'Sẵn sàng'
  } catch (error) {
    chatMessages.value = []
    notify.apiError(error, 'Không tải được lịch sử hội thoại AI.')
  } finally {
    loadingChatMessages.value = false
    scrollChatToBottom('auto')
  }
}

const createChatSession = async () => {
  if (!chatSessionForm.value.related_ho_so_id) {
    notify.warning('Vui lòng chọn một hồ sơ đang công khai trước khi tạo phiên chatbot.')
    return
  }

  creatingChatSession.value = true
  try {
    const response = await aiChatService.createSession({
      title: chatSessionForm.value.title,
      related_ho_so_id: Number(chatSessionForm.value.related_ho_so_id),
      related_tin_tuyen_dung_id: chatSessionForm.value.related_tin_tuyen_dung_id ? Number(chatSessionForm.value.related_tin_tuyen_dung_id) : null,
    })

    const session = response?.data
    notify.created('Phiên chatbot')
    emit('refresh-overview')
    await fetchChatSessions()
    if (session?.id) {
      await selectChatSession(session.id)
      collapseChatSidebar()
      await expandChatPanel()
    }
  } catch (error) {
    notify.apiError(error, 'Không thể tạo phiên chatbot AI.')
  } finally {
    creatingChatSession.value = false
  }
}

const sendChatMessageClassic = async (message) => {
  const response = await aiChatService.sendMessage({
    session_id: activeChatSessionId.value,
    message,
    force_model: true,
  })

  const userMessage = response?.data?.user_message
  const assistantMessage = response?.data?.assistant_message

  if (userMessage) chatMessages.value.push(userMessage)
  if (assistantMessage) chatMessages.value.push(assistantMessage)
}

const sendChatMessageStream = async (message) => {
  const tempUserId = `temp-user-${Date.now()}`
  const draftId = `draft-chat-${Date.now()}`
  let hasUserMessage = false
  chatStreaming.value = true
  chatStreamStatus.value = 'Đang stream'

  chatMessages.value.push({
    id: tempUserId,
    role: 'user',
    content: message,
    metadata: {
      streaming: true,
    },
  })
  chatMessages.value.push({
    id: draftId,
    role: 'assistant',
    content: '',
    metadata: {
      intent: null,
      provider: 'stream_pending',
      streaming: true,
    },
  })

  await aiChatService.sendMessageStream(
    {
      session_id: activeChatSessionId.value,
      message,
      force_model: true,
    },
    {
      onMeta(payload) {
        if (payload?.user_message && !hasUserMessage) {
          const tempIndex = chatMessages.value.findIndex((item) => item.id === tempUserId)
          if (tempIndex >= 0) {
            chatMessages.value.splice(tempIndex, 1, payload.user_message)
          } else {
            chatMessages.value.push(payload.user_message)
          }
          hasUserMessage = true
          scrollChatToBottom()
        }

        const draft = chatMessages.value.find((item) => item.id === draftId)
        if (draft) {
          draft.metadata = {
            ...draft.metadata,
            provider: payload?.provider || draft.metadata?.provider || 'stream_pending',
            intent: payload?.intent ?? draft.metadata?.intent ?? null,
            model_version: payload?.model_version || draft.metadata?.model_version || null,
            streaming: true,
          }
        }
      },
      onChunk(payload) {
        const draft = chatMessages.value.find((item) => item.id === draftId)
        if (draft) {
          draft.content += payload?.content || ''
          draft.metadata = {
            ...draft.metadata,
            streaming: true,
          }
          scrollChatToBottom()
        }
      },
      onDone(payload) {
        const draftIndex = chatMessages.value.findIndex((item) => item.id === draftId)
        if (draftIndex >= 0 && payload?.assistant_message) {
          chatMessages.value.splice(draftIndex, 1, payload.assistant_message)
        } else if (payload?.assistant_message) {
          chatMessages.value.push(payload.assistant_message)
        }
        chatStreaming.value = false
        chatStreamStatus.value = 'Hoàn tất'
        scrollChatToBottom()
      },
      onError(payload) {
        const tempUserIndex = chatMessages.value.findIndex((item) => item.id === tempUserId)
        if (tempUserIndex >= 0) {
          chatMessages.value.splice(tempUserIndex, 1)
        }
        const draftIndex = chatMessages.value.findIndex((item) => item.id === draftId)
        if (draftIndex >= 0) {
          chatMessages.value.splice(draftIndex, 1)
        }
        chatStreaming.value = false
        chatStreamStatus.value = 'Lỗi stream'
        throw new Error(payload?.message || 'Không thể stream phản hồi từ AI.')
      },
    }
  )
}

const sendChatMessage = async () => {
  if (!chatCanSend.value) return

  const message = chatMessageInput.value.trim()
  sendingChatMessage.value = true
  chatStreamStatus.value = streamEnabled.value ? 'Đang gửi...' : 'Đang xử lý'
  try {
    if (streamEnabled.value) {
      await sendChatMessageStream(message)
    } else {
      await sendChatMessageClassic(message)
      chatStreamStatus.value = 'Hoàn tất'
      await scrollChatToBottom()
    }

    chatMessageInput.value = ''
    emit('refresh-overview')
    await fetchChatSessions()
  } catch (error) {
    chatMessages.value = chatMessages.value.filter(
      (item) => !String(item.id).startsWith('temp-user-') && !String(item.id).startsWith('draft-chat-')
    )
    chatStreaming.value = false
    chatStreamStatus.value = 'Lỗi stream'
    notify.apiError(error, 'Không gửi được câu hỏi đến AI.')
  } finally {
    sendingChatMessage.value = false
  }
}

const deleteChatSession = async () => {
  if (!activeChatSessionId.value) return

  try {
    await aiChatService.deleteSession(activeChatSessionId.value)
    notify.deleted('Phiên chatbot')
    activeChatSessionId.value = null
    chatMessages.value = []
    expandChatSidebar()
    emit('refresh-overview')
    await fetchChatSessions()
  } catch (error) {
    notify.apiError(error, 'Không thể xóa phiên chatbot.')
  }
}

onMounted(async () => {
  await Promise.all([fetchBootstrapData(), fetchChatSessions()])
})

watch(
  () => chatMessages.value.length,
  () => {
    scrollChatToBottom()
  }
)
</script>

<template>
  <section
    class="grid grid-cols-1 gap-6"
    :class="chatSidebarCollapsed ? 'xl:grid-cols-[minmax(0,1fr)]' : 'xl:grid-cols-[360px_minmax(0,1fr)]'"
  >
    <aside
      class="space-y-6"
      :class="chatSidebarCollapsed ? 'hidden xl:hidden' : ''"
    >
      <section class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/85">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">Tạo phiên chatbot</h2>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">Chọn hồ sơ và job liên quan để AI bám ngữ cảnh tốt hơn.</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="hidden rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 xl:inline-flex dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              type="button"
              @click="collapseChatSidebar"
            >
              Thu gọn
            </button>
            <span class="material-symbols-outlined rounded-xl bg-blue-500/10 p-3 text-blue-300">add_comment</span>
          </div>
        </div>

        <div class="mt-5 space-y-4">
          <label class="block">
            <span class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Tiêu đề phiên</span>
            <input
              v-model="chatSessionForm.title"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-500 focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950/80 dark:text-white"
              placeholder="Ví dụ: Tư vấn hồ sơ Backend Laravel"
              type="text"
            >
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Hồ sơ ứng viên</span>
            <select
              v-model="chatSessionForm.related_ho_so_id"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950/80 dark:text-white"
            >
              <option value="">Chọn hồ sơ công khai</option>
              <option v-for="profile in availableProfiles" :key="profile.id" :value="String(profile.id)">
                {{ profile.tieu_de_ho_so }}
              </option>
            </select>
            <p v-if="!availableProfiles.length" class="mt-2 text-xs leading-5 text-amber-600 dark:text-amber-300">
              Bạn chưa có CV công khai. Hãy vào mục <strong class="text-slate-900 dark:text-white">CV của tôi</strong> để bật công khai ít nhất một hồ sơ.
            </p>
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Tin tuyển dụng liên quan</span>
            <select
              v-model="chatSessionForm.related_tin_tuyen_dung_id"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950/80 dark:text-white"
            >
              <option value="">Không chọn</option>
              <option v-for="job in jobs" :key="job.id" :value="String(job.id)">
                {{ job.tieu_de }}
              </option>
            </select>
          </label>

          <button
            class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-500 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-blue-600/20 transition hover:from-blue-500 hover:to-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="creatingChatSession || loadingBootstrap"
            type="button"
            @click="createChatSession"
          >
            <span class="material-symbols-outlined text-lg">smart_toy</span>
            {{ creatingChatSession ? 'Đang tạo phiên...' : 'Tạo phiên chatbot mới' }}
          </button>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/85">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">Phiên gần đây</h2>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">Chuyển nhanh giữa các cuộc tư vấn.</p>
          </div>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
            {{ chatSessions.length }} phiên
          </span>
        </div>

        <div v-if="loadingChatSessions" class="mt-5 space-y-3">
          <div v-for="index in 4" :key="index" class="h-20 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800" />
        </div>

        <div v-else-if="!chatSessionOptions.length" class="mt-5 rounded-xl border border-dashed border-slate-300 bg-slate-50/70 px-4 py-5 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-950/50 dark:text-slate-400">
          Chưa có phiên chatbot nào. Tạo phiên đầu tiên để bắt đầu tư vấn cùng AI.
        </div>

        <div v-else class="mt-5 space-y-3">
          <button
            v-for="session in chatSessionOptions"
            :key="session.id"
            type="button"
            class="w-full rounded-2xl border px-4 py-4 text-left transition"
            :class="session.id === activeChatSessionId
              ? 'border-blue-500/40 bg-blue-500/10 shadow-lg shadow-blue-900/10'
              : 'border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-950/70 dark:hover:border-slate-700 dark:hover:bg-slate-900'"
            @click="selectChatSession(session.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-900 dark:text-white">{{ session.title || 'Tư vấn nghề nghiệp' }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-500">{{ formatDateTime(session.updated_at) }}</p>
              </div>
              <span class="rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide"
                :class="session.id === activeChatSessionId ? 'bg-blue-500/20 text-blue-700 dark:text-blue-200' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'">
                AI
              </span>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-400">
              {{ chatPreview(session) }}
            </p>
          </button>
        </div>
      </section>
    </aside>

    <section ref="chatPanel" class="rounded-2xl border border-slate-200 bg-white/95 p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/85">
      <div class="flex flex-col gap-4 border-b border-slate-200 pb-5 md:flex-row md:items-center md:justify-between dark:border-slate-800">
        <div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-white">
            {{ activeChatSession?.title || 'Chatbot tư vấn nghề nghiệp' }}
          </h2>
          <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
            {{ activeChatSession
              ? 'Đặt câu hỏi về job phù hợp, kỹ năng còn thiếu, lộ trình học hoặc cải thiện CV.'
              : 'Tạo hoặc chọn một phiên chatbot để bắt đầu.' }}
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <button
            v-if="chatSidebarCollapsed"
            class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="expandChatSidebar"
          >
            Hiện cột trái
          </button>
          <span class="inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold" :class="chatStatusTone">
            <span
              v-if="chatStreaming"
              class="h-2 w-2 animate-pulse rounded-full bg-blue-300 shadow-[0_0_12px_rgba(147,197,253,0.9)]"
            />
            {{ chatStreamStatus }}
          </span>
          <label class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-950/70 dark:text-slate-300">
            <input v-model="streamEnabled" class="accent-blue-500" type="checkbox">
            Dùng stream SSE
          </label>
          <RouterLink
            to="/matched-jobs"
            class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Xem việc phù hợp
          </RouterLink>
          <button
            class="rounded-xl border border-red-500/30 px-4 py-2.5 text-sm font-semibold text-red-300 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="!activeChatSessionId"
            type="button"
            @click="deleteChatSession"
          >
            Xóa phiên
          </button>
        </div>
      </div>

      <div class="mt-6 rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-950/70">
        <div v-if="loadingChatMessages" class="space-y-4">
          <div v-for="index in 4" :key="index" class="h-16 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
        </div>

        <div v-else-if="!activeChatSessionId" class="flex min-h-[360px] items-center justify-center rounded-2xl border border-dashed border-slate-300 px-8 text-center text-sm leading-7 text-slate-600 dark:border-slate-700 dark:text-slate-400">
          Chọn một phiên gần đây hoặc tạo phiên chatbot mới để AI bắt đầu tư vấn trên hồ sơ của bạn.
        </div>

          <div v-else class="space-y-4">
            <div v-if="!hasChatMessages" class="flex min-h-[320px] items-center justify-center rounded-2xl border border-dashed border-slate-300 px-8 text-center text-sm leading-7 text-slate-600 dark:border-slate-700 dark:text-slate-400">
              Phiên này chưa có tin nhắn. Hãy hỏi AI về job gần nhất, kỹ năng còn thiếu hoặc cách cải thiện CV.
            </div>

            <div v-else ref="chatMessagesContainer" class="max-h-[520px] space-y-4 overflow-y-auto pr-1">
              <article
                v-for="message in chatMessages"
                :key="message.id"
              class="max-w-[88%] rounded-2xl border px-4 py-3"
              :class="messageBubbleClass(message.role)"
            >
              <div class="mb-2 flex items-center gap-2">
                <span class="text-xs font-semibold uppercase tracking-wide opacity-80">
                  {{ message.role === 'user' ? 'Bạn' : 'Trợ lý AI' }}
                </span>
                <span
                  v-if="message.role === 'assistant'"
                  class="rounded-full bg-slate-200 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-blue-700 dark:bg-slate-800/80 dark:text-blue-200"
                >
                  {{ getChatIntentLabel(message.metadata?.intent) }}
                </span>
                <span
                  v-if="message.role === 'assistant'"
                  class="rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide"
                  :class="getChatProviderTone(message.metadata?.provider)"
                >
                  {{ getChatProviderLabel(message.metadata?.provider) }}
                </span>
              </div>
              <div
                v-if="message.role === 'assistant' && message.metadata?.streaming && !message.content"
                  class="inline-flex items-center gap-2 text-sm leading-7 text-slate-600 dark:text-slate-300"
              >
                <span>Đang phân tích</span>
                <span class="inline-flex gap-1">
                  <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-300 [animation-delay:0ms]" />
                  <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-300 [animation-delay:150ms]" />
                  <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-300 [animation-delay:300ms]" />
                </span>
              </div>
              <p v-else class="whitespace-pre-wrap text-sm leading-7">{{ message.content }}</p>
            </article>
          </div>
        </div>
      </div>

      <div class="mt-5 space-y-3">
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="rounded-full border border-slate-700 bg-slate-950/60 px-3 py-1.5 text-xs font-semibold text-slate-300 transition hover:border-blue-500/40 hover:text-blue-200"
            @click="chatMessageInput = 'Trong hệ thống hiện có job nào gần nhất với hồ sơ của tôi?'"
          >
            Gợi ý job
          </button>
          <button
            type="button"
            class="rounded-full border border-slate-700 bg-slate-950/60 px-3 py-1.5 text-xs font-semibold text-slate-300 transition hover:border-blue-500/40 hover:text-blue-200"
            @click="chatMessageInput = 'Tôi đang thiếu những kỹ năng nào để phù hợp hơn với vị trí backend này?'"
          >
            Thiếu kỹ năng
          </button>
          <button
            type="button"
            class="rounded-full border border-slate-700 bg-slate-950/60 px-3 py-1.5 text-xs font-semibold text-slate-300 transition hover:border-blue-500/40 hover:text-blue-200"
            @click="chatMessageInput = 'CV hiện tại của tôi nên chỉnh ở đâu trước?'"
          >
            Cải thiện CV
          </button>
        </div>

        <div class="flex flex-col gap-3 lg:flex-row">
          <textarea
            ref="chatComposerInput"
            v-model="chatMessageInput"
            class="min-h-[112px] flex-1 rounded-2xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm leading-7 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500"
            placeholder="Nhập câu hỏi về hồ sơ, matching, nghề nghiệp hoặc kỹ năng cần bổ sung..."
          />
          <button
            class="rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-500 px-6 py-4 text-sm font-bold text-white shadow-lg shadow-blue-600/20 transition hover:from-blue-500 hover:to-indigo-400 disabled:cursor-not-allowed disabled:opacity-60 lg:w-[180px]"
            :disabled="!chatCanSend"
            type="button"
            @click="sendChatMessage"
          >
            {{ sendingChatMessage ? 'Đang gửi...' : 'Gửi cho AI' }}
          </button>
        </div>
      </div>
    </section>
  </section>
</template>
