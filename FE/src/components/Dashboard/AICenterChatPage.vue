<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { aiChatService, jobService, profileService, walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getCompactAiQuotaText } from '@/utils/billing'

const emit = defineEmits(['refresh-overview'])

const notify = useNotify()

const profiles = ref([])
const jobs = ref([])
const entitlements = ref([])
const loadingBootstrap = ref(false)
const loadingChatSessions = ref(false)
const loadingChatMessages = ref(false)
const loadingAiQuota = ref(false)
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
const chatEntitlement = computed(() =>
  entitlements.value.find((item) => item.feature_code === 'chatbot_message') || null
)
const chatAiQuotaText = computed(() =>
  loadingAiQuota.value
    ? 'Đang tải...'
    : getCompactAiQuotaText(chatEntitlement.value, {
      unit: 'prompts',
      inactiveLabel: 'Dùng ví AI',
    })
)
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

const fetchAiEntitlements = async () => {
  loadingAiQuota.value = true
  try {
    const response = await walletService.getEntitlements()
    entitlements.value = response?.data?.entitlements || []
  } catch (error) {
    notify.apiError(error, 'Không tải được hạn mức AI.')
  } finally {
    loadingAiQuota.value = false
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
    await Promise.all([fetchChatSessions(), fetchAiEntitlements()])
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
  await Promise.all([fetchBootstrapData(), fetchChatSessions(), fetchAiEntitlements()])
})

watch(
  () => chatMessages.value.length,
  () => {
    scrollChatToBottom()
  }
)
</script>

<template>
  <section class="grid min-h-[calc(100vh-5rem)] grid-cols-1 overflow-hidden bg-[#f8f4f1] xl:grid-cols-[400px_minmax(0,1fr)]">
    <aside class="flex min-h-0 flex-col border-r border-slate-200 bg-white">
      <div class="border-b border-slate-200 p-5">
        <button
          class="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#f45112] px-5 py-4 text-sm font-black text-white shadow-[0_16px_34px_rgba(244,81,18,0.22)] transition hover:bg-[#e6470e] disabled:cursor-not-allowed disabled:opacity-70"
          :disabled="creatingChatSession || loadingBootstrap"
          type="button"
          @click="createChatSession"
        >
          <span class="material-symbols-outlined text-[20px]">add</span>
          {{ creatingChatSession ? 'Đang tạo...' : 'Cuộc hội thoại mới' }}
        </button>

        <div class="mt-4 space-y-3 rounded-2xl border border-orange-100 bg-orange-50/50 p-4">
          <label class="block">
            <span class="mb-1.5 block text-xs font-black uppercase tracking-[0.18em] text-slate-500">Tiêu đề hội thoại</span>
            <input
              v-model="chatSessionForm.title"
              class="w-full rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#f45112]"
              placeholder="Ví dụ: Tư vấn lộ trình Frontend"
              type="text"
            >
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-black uppercase tracking-[0.18em] text-slate-500">Hồ sơ dùng để tư vấn</span>
            <select
              v-model="chatSessionForm.related_ho_so_id"
              class="w-full rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#f45112]"
            >
              <option value="">Chọn hồ sơ công khai</option>
              <option v-for="profile in availableProfiles" :key="profile.id" :value="String(profile.id)">
                {{ profile.tieu_de_ho_so }}
              </option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-black uppercase tracking-[0.18em] text-slate-500">Tin tuyển dụng tham chiếu</span>
            <select
              v-model="chatSessionForm.related_tin_tuyen_dung_id"
              class="w-full rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#f45112]"
            >
              <option value="">Không chọn tin tuyển dụng</option>
              <option v-for="job in jobs" :key="job.id" :value="String(job.id)">
                {{ job.tieu_de }}
              </option>
            </select>
          </label>
          <p v-if="!availableProfiles.length" class="text-xs leading-5 text-orange-700">
            Bạn chưa có CV công khai. Hãy bật công khai ít nhất một hồ sơ trong mục CV của tôi.
          </p>
        </div>
      </div>

      <div class="min-h-0 flex-1 overflow-y-auto px-5 py-4">
        <div class="mb-3 flex items-center justify-between">
          <p class="text-xs font-black uppercase tracking-[0.28em] text-slate-400">Gần đây</p>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">{{ chatSessions.length }}</span>
        </div>

        <div v-if="loadingChatSessions" class="space-y-3">
          <div v-for="index in 5" :key="index" class="h-20 animate-pulse rounded-2xl bg-slate-100" />
        </div>
        <div v-else-if="!chatSessionOptions.length" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-5 text-sm leading-6 text-slate-500">
          Chưa có cuộc hội thoại nào. Tạo cuộc hội thoại đầu tiên để bắt đầu cùng AI.
        </div>
        <div v-else class="space-y-1">
          <button
            v-for="session in chatSessionOptions"
            :key="session.id"
            type="button"
            class="w-full rounded-2xl px-4 py-4 text-left transition"
            :class="session.id === activeChatSessionId
              ? 'border border-orange-200 bg-orange-50 text-[#f45112]'
              : 'text-slate-700 hover:bg-slate-50'"
            @click="selectChatSession(session.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <p class="min-w-0 truncate text-sm font-black">{{ session.title || 'Tư vấn nghề nghiệp' }}</p>
              <span class="shrink-0 text-xs text-slate-400">{{ formatDateTime(session.updated_at) }}</span>
            </div>
            <p class="mt-2 line-clamp-2 text-sm italic leading-6 text-slate-500">"{{ chatPreview(session) }}"</p>
          </button>
        </div>
      </div>

      <div class="space-y-3 border-t border-slate-200 p-5">
        <div class="rounded-xl bg-slate-50 px-4 py-3 text-sm font-medium text-slate-500">
          <span class="material-symbols-outlined mr-2 align-[-4px] text-[18px]">info</span>
          Hạn mức AI: {{ chatAiQuotaText }}
        </div>
        <div class="rounded-xl bg-slate-50 px-4 py-3 text-sm font-medium text-slate-500">
          <span class="material-symbols-outlined mr-2 align-[-4px] text-[18px]">bolt</span>
          Stream: {{ streamEnabled ? 'đang bật' : 'đang tắt' }}
        </div>
      </div>
    </aside>

    <main ref="chatPanel" class="flex min-h-0 flex-col">
      <header class="flex h-20 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-8">
        <div class="inline-flex rounded-2xl bg-slate-100 p-1">
          <span class="rounded-xl bg-white px-5 py-3 text-sm font-black text-[#f45112] shadow-sm">Tư vấn lộ trình</span>
          <RouterLink
            :to="{ name: 'AICenterMockInterview' }"
            class="rounded-xl px-5 py-3 text-sm font-semibold text-slate-500 transition hover:text-slate-900"
          >
            Phỏng vấn giả lập
          </RouterLink>
        </div>
        <div class="flex items-center gap-3">
          <span class="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
          <span class="text-xs font-bold uppercase tracking-[0.28em] text-slate-500">AI Agent Online</span>
        </div>
      </header>

      <div ref="chatMessagesContainer" class="min-h-0 flex-1 overflow-y-auto px-8 py-7">
        <div v-if="loadingChatMessages" class="space-y-5">
          <div v-for="index in 4" :key="index" class="h-24 animate-pulse rounded-[24px] bg-white" />
        </div>
        <div v-else-if="!activeChatSessionId" class="flex h-full items-center justify-center text-center text-sm leading-7 text-slate-500">
          Chọn một cuộc hội thoại gần đây hoặc tạo cuộc hội thoại mới để AI bắt đầu tư vấn trên hồ sơ của bạn.
        </div>
        <div v-else-if="!hasChatMessages" class="flex h-full items-center justify-center text-center text-sm leading-7 text-slate-500">
          Cuộc hội thoại này chưa có tin nhắn. Hãy hỏi AI về job gần nhất, kỹ năng còn thiếu hoặc cách cải thiện CV.
        </div>
        <div v-else class="space-y-8">
          <article
            v-for="message in chatMessages"
            :key="message.id"
            class="flex gap-5"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div v-if="message.role === 'assistant'" class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#f45112] text-white shadow-[0_12px_24px_rgba(244,81,18,0.2)]">
              <span class="material-symbols-outlined">smart_toy</span>
            </div>
            <div class="max-w-[82%]">
              <div class="mb-2 flex items-center gap-2" :class="message.role === 'user' ? 'justify-end' : ''">
                <span class="text-xs font-black uppercase tracking-[0.16em] text-slate-400">
                  {{ message.role === 'user' ? 'Bạn' : 'SmartJob AI' }}
                </span>
              </div>
              <div
                class="rounded-[24px] px-7 py-5 text-base leading-8 shadow-sm"
                :class="message.role === 'user'
                  ? 'rounded-tr-none bg-[#f45112] text-white shadow-[0_18px_36px_rgba(244,81,18,0.22)]'
                  : 'rounded-tl-none border border-slate-200 bg-white text-slate-900'"
              >
                <div
                  v-if="message.role === 'assistant' && message.metadata?.streaming && !message.content"
                  class="inline-flex items-center gap-2 text-slate-500"
                >
                  <span>Đang phân tích</span>
                  <span class="inline-flex gap-1">
                    <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-[#f45112]" />
                    <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-[#f45112] [animation-delay:150ms]" />
                    <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-[#f45112] [animation-delay:300ms]" />
                  </span>
                </div>
                <p v-else class="whitespace-pre-wrap">{{ message.content }}</p>
              </div>
            </div>
            <div v-if="message.role === 'user'" class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-200 text-slate-700">
              <span class="material-symbols-outlined">person</span>
            </div>
          </article>
        </div>
      </div>

      <footer class="shrink-0 border-t border-slate-200 bg-white px-10 py-6">
        <div class="flex items-center gap-4 rounded-2xl bg-slate-100 px-6 py-4">
          <textarea
            ref="chatComposerInput"
            v-model="chatMessageInput"
            class="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent text-base leading-7 text-slate-900 outline-none placeholder:text-slate-400"
            placeholder="Nhập câu hỏi của bạn tại đây..."
            @keydown.enter.exact.prevent="sendChatMessage"
          />
          <button
            class="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-[#f45112] text-white shadow-[0_12px_24px_rgba(244,81,18,0.24)] transition hover:bg-[#e6470e] disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!chatCanSend"
            type="button"
            @click="sendChatMessage"
          >
            <span class="material-symbols-outlined">{{ sendingChatMessage ? 'hourglass_top' : 'send' }}</span>
          </button>
        </div>
        <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div class="flex flex-wrap gap-4 text-sm font-medium text-slate-500">
            <button type="button" class="inline-flex items-center gap-1 hover:text-[#f45112]" @click="chatMessageInput = 'Trong hệ thống hiện có job nào gần nhất với hồ sơ của tôi?'">
              <span class="material-symbols-outlined text-[18px]">attach_file</span>
              Gợi ý job
            </button>
            <button type="button" class="inline-flex items-center gap-1 hover:text-[#f45112]" @click="chatMessageInput = 'Tôi đang thiếu những kỹ năng nào để phù hợp hơn với vị trí backend này?'">
              <span class="material-symbols-outlined text-[18px]">mic</span>
              Kỹ năng thiếu
            </button>
            <label class="inline-flex items-center gap-2">
              <input v-model="streamEnabled" class="accent-[#f45112]" type="checkbox">
              Stream SSE
            </label>
          </div>
          <div class="flex gap-3">
            <RouterLink to="/matched-jobs" class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50">
              Việc phù hợp
            </RouterLink>
            <button
              class="rounded-xl bg-slate-950 px-4 py-2 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!activeChatSessionId"
              type="button"
              @click="deleteChatSession"
            >
              Xóa phiên
            </button>
          </div>
        </div>
      </footer>
    </main>
  </section>
</template>
