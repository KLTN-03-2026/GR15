<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { jobService, mockInterviewService, profileService, walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getCompactAiQuotaText } from '@/utils/billing'

const emit = defineEmits(['refresh-overview'])

const notify = useNotify()

const profiles = ref([])
const jobs = ref([])
const entitlements = ref([])
const loadingBootstrap = ref(false)
const loadingMockSessions = ref(false)
const loadingMockMessages = ref(false)
const loadingAiQuota = ref(false)
const creatingMockSession = ref(false)
const answeringMock = ref(false)
const generatingMockReport = ref(false)
const streamEnabled = ref(true)
const mockStreaming = ref(false)
const mockStreamStatus = ref('Sẵn sàng')
const mockSidebarCollapsed = ref(false)

const mockSessions = ref([])
const mockMessages = ref([])
const activeMockSessionId = ref(null)
const mockReport = ref(null)
const streamingReportText = ref('')
const mockAnswerInput = ref('')
const mockMessagesContainer = ref(null)
const mockPanel = ref(null)
const mockComposerInput = ref(null)
const mockSessionForm = ref({
  title: 'Mock Interview cùng AI',
  related_ho_so_id: '',
  related_tin_tuyen_dung_id: '',
  question_count: 5,
})

const availableProfiles = computed(() =>
  profiles.value.filter((item) => Number(item.trang_thai) === 1)
)

const activeMockSession = computed(() =>
  mockSessions.value.find((item) => item.id === activeMockSessionId.value) || null
)

const mockSessionOptions = computed(() => mockSessions.value.slice(0, 6))
const hasMockMessages = computed(() => mockMessages.value.length > 0)
const mockCanAnswer = computed(() => Boolean(activeMockSessionId.value && mockAnswerInput.value.trim() && !answeringMock.value))
const mockEntitlement = computed(() =>
  entitlements.value.find((item) => item.feature_code === 'mock_interview_session') || null
)
const mockAiQuotaText = computed(() =>
  loadingAiQuota.value
    ? 'Đang tải...'
    : getCompactAiQuotaText(mockEntitlement.value, {
      unit: 'lượt',
      inactiveLabel: 'Dùng ví AI',
    })
)
const mockStatusTone = computed(() =>
  mockStreaming.value
    ? 'bg-violet-500/15 text-violet-200 border-violet-500/30'
    : 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-700'
)

const latestMockQuestionMeta = computed(() => {
  const assistantQuestions = mockMessages.value
    .filter((item) => item.role === 'assistant' && item.metadata?.type === 'interview_question')
  return assistantQuestions[assistantQuestions.length - 1]?.metadata || {}
})

const mockProgress = computed(() => {
  const answeredCount = mockMessages.value.filter((item) => item.role === 'user').length
  const maxQuestions = Number(latestMockQuestionMeta.value.max_questions || activeMockSession.value?.metadata?.question_count || 0)
  const currentQuestion = Math.min(answeredCount + 1, maxQuestions || answeredCount + 1)
  const percent = maxQuestions > 0 ? Math.min(100, Math.round((answeredCount / maxQuestions) * 100)) : 0

  return {
    answeredCount,
    maxQuestions,
    currentQuestion,
    percent,
  }
})

const messageBubbleClass = (role) =>
  role === 'user'
    ? 'ml-auto bg-gradient-to-r from-violet-600 to-fuchsia-500 text-white border-transparent'
    : 'mr-auto bg-slate-50 border-slate-200 text-slate-900 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-100'

const formatDateTime = (value) => {
  if (!value) return 'Vừa xong'
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

const mockPreview = (session) => {
  if (session.tin_tuyen_dung?.tieu_de) return session.tin_tuyen_dung.tieu_de
  if (session.ho_so?.tieu_de_ho_so) return session.ho_so.tieu_de_ho_so
  return 'Phiên phỏng vấn thử đang chờ câu hỏi đầu tiên.'
}

const getInterviewQuestionLabel = (message) => {
  const type = message?.metadata?.question_type
  if (type === 'behavioral') return 'Câu hỏi hành vi'
  if (type === 'follow_up') return 'Câu hỏi đào sâu'
  if (type === 'gap_skill') return 'Kỹ năng cần bù'
  return 'Câu hỏi phỏng vấn'
}

const getMockProviderLabel = (provider) => {
  switch (provider) {
    case 'ollama':
      return 'Sinh bởi Ollama'
    case 'rule_based':
      return 'Nội bộ'
    case 'stream_pending':
      return 'Đang soạn câu hỏi'
    default:
      return 'AI xử lý'
  }
}

const getMockProviderTone = (provider) => {
  switch (provider) {
    case 'ollama':
      return 'bg-emerald-500/15 text-emerald-200'
    case 'rule_based':
      return 'bg-amber-500/15 text-amber-200'
    default:
      return 'bg-slate-800/80 text-slate-300'
  }
}

const pickDefaultProfile = () => {
  const firstProfileId = availableProfiles.value[0]?.id ? String(availableProfiles.value[0].id) : ''
  const stillValid = availableProfiles.value.some(
    (item) => String(item.id) === String(mockSessionForm.value.related_ho_so_id)
  )

  if (!stillValid) {
    mockSessionForm.value.related_ho_so_id = ''
  }

  if (!mockSessionForm.value.related_ho_so_id) {
    mockSessionForm.value.related_ho_so_id = firstProfileId
  }
}

const scrollMockToBottom = async (behavior = 'smooth') => {
  await nextTick()
  const container = mockMessagesContainer.value
  if (!container) return
  container.scrollTo({
    top: container.scrollHeight,
    behavior,
  })
}

const expandMockPanel = async () => {
  await nextTick()

  mockPanel.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })

  mockComposerInput.value?.focus()
}

const collapseMockSidebar = () => {
  mockSidebarCollapsed.value = true
}

const expandMockSidebar = () => {
  mockSidebarCollapsed.value = false
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
    notify.apiError(error, 'Không tải được dữ liệu nền cho mock interview.')
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

const fetchMockSessions = async () => {
  loadingMockSessions.value = true
  try {
    const response = await mockInterviewService.getSessions()
    mockSessions.value = response?.data || []

    if (!activeMockSessionId.value && mockSessions.value.length) {
      await selectMockSession(mockSessions.value[0].id)
    } else if (activeMockSessionId.value) {
      const stillExists = mockSessions.value.some((item) => item.id === activeMockSessionId.value)
      if (!stillExists) {
        activeMockSessionId.value = null
        mockMessages.value = []
        mockReport.value = null
      }
    }
  } catch (error) {
    notify.apiError(error, 'Không tải được danh sách phiên mock interview.')
  } finally {
    loadingMockSessions.value = false
  }
}

const selectMockSession = async (sessionId) => {
  activeMockSessionId.value = sessionId
  loadingMockMessages.value = true
  mockReport.value = null
  streamingReportText.value = ''
  try {
    const [messagesRes, reportRes] = await Promise.allSettled([
      mockInterviewService.getMessages(sessionId),
      mockInterviewService.getReport(sessionId),
    ])

    if (messagesRes.status === 'fulfilled') {
      mockMessages.value = messagesRes.value?.data || []
    } else {
      mockMessages.value = []
      notify.apiError(messagesRes.reason, 'Không tải được nội dung phiên mock interview.')
    }

    if (reportRes.status === 'fulfilled') {
      mockReport.value = reportRes.value?.data || null
    } else {
      mockReport.value = null
    }
    mockStreamStatus.value = 'Sẵn sàng'
  } finally {
    loadingMockMessages.value = false
    scrollMockToBottom('auto')
  }
}

const createMockSession = async () => {
  if (!mockSessionForm.value.related_ho_so_id) {
    notify.warning('Vui lòng chọn một hồ sơ đang công khai trước khi tạo mock interview.')
    return
  }

  creatingMockSession.value = true
  try {
    const response = await mockInterviewService.createSession({
      title: mockSessionForm.value.title,
      related_ho_so_id: Number(mockSessionForm.value.related_ho_so_id),
      related_tin_tuyen_dung_id: mockSessionForm.value.related_tin_tuyen_dung_id ? Number(mockSessionForm.value.related_tin_tuyen_dung_id) : null,
      auto_generate_first_question: true,
      question_count: Number(mockSessionForm.value.question_count || 5),
    })

    const session = response?.data?.session
    notify.created('Phiên mock interview')
    emit('refresh-overview')
    await Promise.all([fetchMockSessions(), fetchAiEntitlements()])
    if (session?.id) {
      await selectMockSession(session.id)
      collapseMockSidebar()
      await expandMockPanel()
    }
  } catch (error) {
    notify.apiError(error, 'Không thể tạo phiên mock interview.')
  } finally {
    creatingMockSession.value = false
  }
}

const submitMockAnswerClassic = async (answer) => {
  const response = await mockInterviewService.answer({
    session_id: activeMockSessionId.value,
    answer,
  })

  const payload = response?.data || {}
  if (payload.user_message) mockMessages.value.push(payload.user_message)
  if (payload.assistant_message) mockMessages.value.push(payload.assistant_message)

  if (payload.completed) {
    notify.success('Phiên phỏng vấn đã hoàn tất. Bạn có thể sinh báo cáo ngay.')
  }
}

const submitMockAnswerStream = async (answer) => {
  const tempUserId = `mock-user-${Date.now()}`
  const draftId = `mock-draft-${Date.now()}`
  mockStreaming.value = true
  mockStreamStatus.value = 'Đang stream câu hỏi'

  mockMessages.value.push({
    id: tempUserId,
    role: 'user',
    content: answer,
    metadata: {
      type: 'interview_answer',
    },
  })
  mockMessages.value.push({
    id: draftId,
    role: 'assistant',
    content: '',
    metadata: {
      type: 'interview_question',
      generation_provider: 'stream_pending',
      streaming: true,
    },
  })
  scrollMockToBottom()

  await mockInterviewService.answerStream(
    {
      session_id: activeMockSessionId.value,
      answer,
    },
    {
      onChunk(payload) {
        const draft = mockMessages.value.find((item) => item.id === draftId)
        if (draft) {
          draft.content += payload?.content || ''
          draft.metadata = {
            ...draft.metadata,
            streaming: true,
          }
          scrollMockToBottom()
        }
      },
      onDone(payload) {
        const draftIndex = mockMessages.value.findIndex((item) => item.id === draftId)
        if (draftIndex >= 0 && payload?.assistant_message) {
          mockMessages.value.splice(draftIndex, 1, payload.assistant_message)
        } else if (payload?.assistant_message) {
          mockMessages.value.push(payload.assistant_message)
        }

        if (payload?.completed) {
          notify.success('Phiên phỏng vấn đã hoàn tất. Bạn có thể sinh báo cáo ngay.')
        }
        mockStreaming.value = false
        mockStreamStatus.value = 'Hoàn tất'
        scrollMockToBottom()
      },
      onError(payload) {
        mockStreaming.value = false
        mockStreamStatus.value = 'Lỗi stream'
        throw new Error(payload?.message || 'Không thể stream câu hỏi tiếp theo.')
      },
    }
  )
}

const submitMockAnswer = async () => {
  if (!mockCanAnswer.value) return

  const answer = mockAnswerInput.value.trim()
  answeringMock.value = true
  mockStreamStatus.value = streamEnabled.value ? 'Đang gửi câu trả lời...' : 'Đang xử lý'
  try {
    if (streamEnabled.value) {
      await submitMockAnswerStream(answer)
    } else {
      await submitMockAnswerClassic(answer)
      mockStreamStatus.value = 'Hoàn tất'
      await scrollMockToBottom()
    }

    mockAnswerInput.value = ''
    emit('refresh-overview')
    await fetchMockSessions()
  } catch (error) {
    mockStreaming.value = false
    mockStreamStatus.value = 'Lỗi stream'
    notify.apiError(error, 'Không gửi được câu trả lời phỏng vấn.')
    await selectMockSession(activeMockSessionId.value)
  } finally {
    answeringMock.value = false
  }
}

const generateMockReportClassic = async () => {
  const response = await mockInterviewService.generateReport(activeMockSessionId.value)
  mockReport.value = response?.data || null
}

const generateMockReportWithStream = async () => {
  streamingReportText.value = ''
  mockStreaming.value = true
  mockStreamStatus.value = 'Đang stream báo cáo'

  await mockInterviewService.generateReportStream(activeMockSessionId.value, {
    onChunk(payload) {
      streamingReportText.value += payload?.content || ''
    },
    onDone(payload) {
      mockReport.value = payload?.report || null
      mockStreaming.value = false
      mockStreamStatus.value = 'Hoàn tất'
    },
    onError(payload) {
      mockStreaming.value = false
      mockStreamStatus.value = 'Lỗi stream'
      throw new Error(payload?.message || 'Không thể stream báo cáo mock interview.')
    },
  })
}

const generateMockReport = async () => {
  if (!activeMockSessionId.value) return

  generatingMockReport.value = true
  mockStreamStatus.value = streamEnabled.value ? 'Đang tạo báo cáo...' : 'Đang xử lý báo cáo'
  try {
    if (streamEnabled.value) {
      await generateMockReportWithStream()
    } else {
      await generateMockReportClassic()
      mockStreamStatus.value = 'Hoàn tất'
    }

    notify.success('Đã sinh báo cáo mock interview.')
    emit('refresh-overview')
  } catch (error) {
    mockStreaming.value = false
    mockStreamStatus.value = 'Lỗi stream'
    notify.apiError(error, 'Không thể sinh báo cáo mock interview.')
  } finally {
    generatingMockReport.value = false
  }
}

const deleteMockSession = async () => {
  if (!activeMockSessionId.value) return

  try {
    await mockInterviewService.deleteSession(activeMockSessionId.value)
    notify.deleted('Phiên mock interview')
    activeMockSessionId.value = null
    mockMessages.value = []
    mockReport.value = null
    streamingReportText.value = ''
    expandMockSidebar()
    emit('refresh-overview')
    await fetchMockSessions()
  } catch (error) {
    notify.apiError(error, 'Không thể xóa phiên mock interview.')
  }
}

onMounted(async () => {
  await Promise.all([fetchBootstrapData(), fetchMockSessions(), fetchAiEntitlements()])
})

watch(
  () => mockMessages.value.length,
  () => {
    scrollMockToBottom()
  }
)
</script>

<template>
  <section class="grid min-h-[calc(100vh-5rem)] grid-cols-1 overflow-hidden bg-[#f8f4f1] xl:grid-cols-[400px_minmax(0,1fr)]">
    <aside class="flex min-h-0 flex-col border-r border-slate-200 bg-white">
      <div class="border-b border-slate-200 p-5">
        <button
          class="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#f45112] px-5 py-4 text-sm font-black text-white shadow-[0_16px_34px_rgba(244,81,18,0.22)] transition hover:bg-[#e6470e] disabled:cursor-not-allowed disabled:opacity-70"
          :disabled="creatingMockSession || loadingBootstrap"
          type="button"
          @click="createMockSession"
        >
          <span class="material-symbols-outlined text-[20px]">add</span>
          {{ creatingMockSession ? 'Đang tạo...' : 'Phiên phỏng vấn mới' }}
        </button>

        <div class="mt-4 space-y-3 rounded-2xl border border-orange-100 bg-orange-50/50 p-4">
          <label class="block">
            <span class="mb-1.5 block text-xs font-black uppercase tracking-[0.18em] text-slate-500">Tiêu đề phiên phỏng vấn</span>
            <input
              v-model="mockSessionForm.title"
              class="w-full rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#f45112]"
              placeholder="Ví dụ: Mock interview React"
              type="text"
            >
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-black uppercase tracking-[0.18em] text-slate-500">Hồ sơ dùng để phỏng vấn</span>
            <select
              v-model="mockSessionForm.related_ho_so_id"
              class="w-full rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#f45112]"
            >
              <option value="">Chọn hồ sơ công khai</option>
              <option v-for="profile in availableProfiles" :key="profile.id" :value="String(profile.id)">
                {{ profile.tieu_de_ho_so }}
              </option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-black uppercase tracking-[0.18em] text-slate-500">Tin tuyển dụng mục tiêu</span>
            <select
              v-model="mockSessionForm.related_tin_tuyen_dung_id"
              class="w-full rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#f45112]"
            >
              <option value="">Không chọn tin tuyển dụng</option>
              <option v-for="job in jobs" :key="job.id" :value="String(job.id)">
                {{ job.tieu_de }}
              </option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-black uppercase tracking-[0.18em] text-slate-500">Số câu hỏi phỏng vấn</span>
            <input
              v-model.number="mockSessionForm.question_count"
              class="w-full rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#f45112]"
              min="1"
              type="number"
            >
          </label>
        </div>
      </div>

      <div class="min-h-0 flex-1 overflow-y-auto px-5 py-4">
        <div class="mb-3 flex items-center justify-between">
          <p class="text-xs font-black uppercase tracking-[0.28em] text-slate-400">Gần đây</p>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">{{ mockSessions.length }}</span>
        </div>
        <div v-if="loadingMockSessions" class="space-y-3">
          <div v-for="index in 5" :key="index" class="h-20 animate-pulse rounded-2xl bg-slate-100" />
        </div>
        <div v-else-if="!mockSessionOptions.length" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-5 text-sm leading-6 text-slate-500">
          Chưa có phiên phỏng vấn nào. Tạo phiên đầu tiên để luyện cùng AI.
        </div>
        <div v-else class="space-y-1">
          <button
            v-for="session in mockSessionOptions"
            :key="session.id"
            type="button"
            class="w-full rounded-2xl px-4 py-4 text-left transition"
            :class="session.id === activeMockSessionId
              ? 'border border-orange-200 bg-orange-50 text-[#f45112]'
              : 'text-slate-700 hover:bg-slate-50'"
            @click="selectMockSession(session.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <p class="min-w-0 truncate text-sm font-black">{{ session.title || 'Mock Interview' }}</p>
              <span class="shrink-0 text-xs text-slate-400">{{ formatDateTime(session.updated_at) }}</span>
            </div>
            <p class="mt-2 line-clamp-2 text-sm italic leading-6 text-slate-500">"{{ mockPreview(session) }}"</p>
          </button>
        </div>
      </div>

      <div class="space-y-3 border-t border-slate-200 p-5">
        <div class="rounded-xl bg-slate-50 px-4 py-3 text-sm font-medium text-slate-500">
          <span class="material-symbols-outlined mr-2 align-[-4px] text-[18px]">info</span>
          Hạn mức AI: {{ mockAiQuotaText }}
        </div>
        <div class="rounded-xl bg-slate-50 px-4 py-3 text-sm font-medium text-slate-500">
          <span class="material-symbols-outlined mr-2 align-[-4px] text-[18px]">fact_check</span>
          {{ mockProgress.answeredCount }}/{{ mockProgress.maxQuestions || '--' }} câu đã trả lời
        </div>
      </div>
    </aside>

    <main ref="mockPanel" class="flex min-h-0 flex-col">
      <header class="flex h-20 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-8">
        <div class="inline-flex rounded-2xl bg-slate-100 p-1">
          <RouterLink
            :to="{ name: 'AICenterChatbot' }"
            class="rounded-xl px-5 py-3 text-sm font-semibold text-slate-500 transition hover:text-slate-900"
          >
            Tư vấn lộ trình
          </RouterLink>
          <span class="rounded-xl bg-white px-5 py-3 text-sm font-black text-[#f45112] shadow-sm">Phỏng vấn giả lập</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
          <span class="text-xs font-bold uppercase tracking-[0.28em] text-slate-500">AI Agent Online</span>
        </div>
      </header>

      <div ref="mockMessagesContainer" class="min-h-0 flex-1 overflow-y-auto px-8 py-7">
        <div v-if="activeMockSessionId" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5">
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-sm font-black text-slate-900">Tiến độ phỏng vấn</p>
              <p class="mt-1 text-xs text-slate-500">
                Đã trả lời {{ mockProgress.answeredCount }}/{{ mockProgress.maxQuestions || '--' }} câu · {{ latestMockQuestionMeta.interview_stage_label || 'Đang luyện tập' }}
              </p>
            </div>
            <button
              class="rounded-xl bg-slate-950 px-4 py-2 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!activeMockSessionId || generatingMockReport"
              type="button"
              @click="generateMockReport"
            >
              {{ generatingMockReport ? 'Đang sinh...' : 'Kết thúc & Xuất báo cáo' }}
            </button>
          </div>
          <div class="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-100">
            <div class="h-full rounded-full bg-[#f45112]" :style="{ width: `${mockProgress.percent}%` }" />
          </div>
        </div>

        <div v-if="loadingMockMessages" class="space-y-5">
          <div v-for="index in 4" :key="index" class="h-24 animate-pulse rounded-[24px] bg-white" />
        </div>
        <div v-else-if="!activeMockSessionId" class="flex h-full items-center justify-center text-center text-sm leading-7 text-slate-500">
          Tạo hoặc chọn một phiên phỏng vấn để nhận câu hỏi đầu tiên từ AI.
        </div>
        <div v-else-if="!hasMockMessages" class="flex min-h-[360px] items-center justify-center text-center text-sm leading-7 text-slate-500">
          Phiên này chưa có nội dung. Hãy tạo phiên mới hoặc tải lại danh sách phiên.
        </div>
        <div v-else class="space-y-8">
          <article
            v-for="message in mockMessages.filter((item) => !item.metadata?.hidden_in_ui)"
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
                  <span>Đang soạn câu hỏi</span>
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

          <section v-if="generatingMockReport && streamingReportText" class="rounded-[24px] border border-orange-200 bg-white p-6">
            <p class="text-sm font-black text-slate-900">Đang stream báo cáo...</p>
            <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ streamingReportText }}</p>
          </section>

          <section v-else-if="mockReport" class="rounded-[24px] border border-orange-200 bg-white p-6">
            <p class="text-sm font-black text-slate-900">Báo cáo phiên phỏng vấn</p>
            <div class="mt-4 grid gap-3 md:grid-cols-4">
              <div class="rounded-2xl bg-orange-50 p-4">
                <p class="text-xs font-bold text-slate-500">Tổng điểm</p>
                <p class="mt-2 text-2xl font-black text-[#f45112]">{{ Math.round(Number(mockReport.tong_diem || 0)) }}/100</p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-xs font-bold text-slate-500">Kỹ thuật</p>
                <p class="mt-2 text-xl font-black text-slate-900">{{ Math.round(Number(mockReport.diem_ky_thuat || 0)) }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-xs font-bold text-slate-500">Giao tiếp</p>
                <p class="mt-2 text-xl font-black text-slate-900">{{ Math.round(Number(mockReport.diem_giao_tiep || 0)) }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-xs font-bold text-slate-500">Phù hợp JD</p>
                <p class="mt-2 text-xl font-black text-slate-900">{{ Math.round(Number(mockReport.diem_phu_hop_jd || 0)) }}</p>
              </div>
            </div>
            <p class="mt-5 whitespace-pre-wrap text-sm leading-7 text-slate-600">
              {{ mockReport.de_xuat_cai_thien_text || mockReport.cau_tra_loi_can_cai_thien_nhat || 'Báo cáo chi tiết đang được cập nhật.' }}
            </p>
          </section>
        </div>
      </div>

      <footer class="shrink-0 border-t border-slate-200 bg-white px-10 py-6">
        <div class="flex items-center gap-4 rounded-2xl bg-slate-100 px-6 py-4">
          <textarea
            ref="mockComposerInput"
            v-model="mockAnswerInput"
            class="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent text-base leading-7 text-slate-900 outline-none placeholder:text-slate-400"
            placeholder="Nhập câu trả lời của bạn tại đây..."
            @keydown.enter.exact.prevent="submitMockAnswer"
          />
          <button
            class="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-[#f45112] text-white shadow-[0_12px_24px_rgba(244,81,18,0.24)] transition hover:bg-[#e6470e] disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!mockCanAnswer"
            type="button"
            @click="submitMockAnswer"
          >
            <span class="material-symbols-outlined">{{ answeringMock ? 'hourglass_top' : 'send' }}</span>
          </button>
        </div>
        <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
          <label class="inline-flex items-center gap-2 text-sm font-medium text-slate-500">
            <input v-model="streamEnabled" class="accent-[#f45112]" type="checkbox">
            Stream SSE
          </label>
          <div class="flex gap-3">
            <button
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!activeMockSessionId"
              type="button"
              @click="deleteMockSession"
            >
              Xóa phiên
            </button>
            <button
              class="rounded-xl bg-slate-950 px-4 py-2 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!activeMockSessionId || generatingMockReport"
              type="button"
              @click="generateMockReport"
            >
              Kết thúc & Xuất báo cáo
            </button>
          </div>
        </div>
      </footer>
    </main>
  </section>
</template>
