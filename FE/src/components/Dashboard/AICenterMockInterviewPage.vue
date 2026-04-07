<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { jobService, mockInterviewService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const emit = defineEmits(['refresh-overview'])

const notify = useNotify()

const profiles = ref([])
const jobs = ref([])
const loadingBootstrap = ref(false)
const loadingMockSessions = ref(false)
const loadingMockMessages = ref(false)
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
    await fetchMockSessions()
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
  await Promise.all([fetchBootstrapData(), fetchMockSessions()])
})

watch(
  () => mockMessages.value.length,
  () => {
    scrollMockToBottom()
  }
)
</script>

<template>
  <section
    class="grid grid-cols-1 gap-6"
    :class="mockSidebarCollapsed ? 'xl:grid-cols-[minmax(0,1fr)]' : 'xl:grid-cols-[360px_minmax(0,1fr)]'"
  >
    <aside
      class="space-y-6"
      :class="mockSidebarCollapsed ? 'hidden xl:hidden' : ''"
    >
      <section class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/85">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">Tạo phiên mock interview</h2>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">Chọn hồ sơ, job mục tiêu và số câu phỏng vấn.</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="hidden rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 xl:inline-flex dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              type="button"
              @click="collapseMockSidebar"
            >
              Thu gọn
            </button>
            <span class="material-symbols-outlined rounded-xl bg-violet-500/10 p-3 text-violet-300">school</span>
          </div>
        </div>

        <div class="mt-5 space-y-4">
          <label class="block">
            <span class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Tiêu đề phiên</span>
            <input
              v-model="mockSessionForm.title"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-500 focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950/80 dark:text-white"
              placeholder="Ví dụ: Mock interview Backend Laravel"
              type="text"
            >
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Hồ sơ ứng viên</span>
            <select
              v-model="mockSessionForm.related_ho_so_id"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950/80 dark:text-white"
            >
              <option value="">Chọn hồ sơ công khai</option>
              <option v-for="profile in availableProfiles" :key="profile.id" :value="String(profile.id)">
                {{ profile.tieu_de_ho_so }}
              </option>
            </select>
            <p v-if="!availableProfiles.length" class="mt-2 text-xs leading-5 text-amber-600 dark:text-amber-300">
              Bạn chưa có CV công khai. Hãy vào mục <strong class="text-slate-900 dark:text-white">CV của tôi</strong> để bật công khai ít nhất một hồ sơ trước khi luyện phỏng vấn.
            </p>
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Tin tuyển dụng liên quan</span>
            <select
              v-model="mockSessionForm.related_tin_tuyen_dung_id"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950/80 dark:text-white"
            >
              <option value="">Không chọn</option>
              <option v-for="job in jobs" :key="job.id" :value="String(job.id)">
                {{ job.tieu_de }}
              </option>
            </select>
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Số câu hỏi</span>
            <input
              v-model.number="mockSessionForm.question_count"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-500 focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950/80 dark:text-white"
              max="7"
              min="3"
              type="number"
            >
          </label>

          <button
            class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-500 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-violet-600/20 transition hover:from-violet-500 hover:to-fuchsia-400 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="creatingMockSession || loadingBootstrap"
            type="button"
            @click="createMockSession"
          >
            <span class="material-symbols-outlined text-lg">mic</span>
            {{ creatingMockSession ? 'Đang tạo phiên...' : 'Tạo phiên phỏng vấn mới' }}
          </button>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/85">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">Phiên gần đây</h2>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">Tiếp tục luyện từ các phiên đang hoạt động.</p>
          </div>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
            {{ mockSessions.length }} phiên
          </span>
        </div>

        <div v-if="loadingMockSessions" class="mt-5 space-y-3">
          <div v-for="index in 4" :key="index" class="h-20 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800" />
        </div>

        <div v-else-if="!mockSessionOptions.length" class="mt-5 rounded-xl border border-dashed border-slate-300 bg-slate-50/70 px-4 py-5 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-950/50 dark:text-slate-400">
          Chưa có phiên mock interview nào. Tạo phiên đầu tiên để bắt đầu luyện tập cùng AI.
        </div>

        <div v-else class="mt-5 space-y-3">
          <button
            v-for="session in mockSessionOptions"
            :key="session.id"
            type="button"
            class="w-full rounded-2xl border px-4 py-4 text-left transition"
            :class="session.id === activeMockSessionId
              ? 'border-violet-500/40 bg-violet-500/10 shadow-lg shadow-violet-900/10'
              : 'border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-950/70 dark:hover:border-slate-700 dark:hover:bg-slate-900'"
            @click="selectMockSession(session.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-900 dark:text-white">{{ session.title || 'Mock Interview' }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ formatDateTime(session.updated_at) }}</p>
              </div>
              <span class="rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide"
                :class="session.id === activeMockSessionId ? 'bg-violet-500/20 text-violet-700 dark:text-violet-200' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'">
                Mock
              </span>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-400">
              {{ mockPreview(session) }}
            </p>
          </button>
        </div>
      </section>
    </aside>

    <section ref="mockPanel" class="space-y-6">
      <section class="rounded-2xl border border-slate-200 bg-white/95 p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/85">
        <div class="flex flex-col gap-4 border-b border-slate-200 pb-5 md:flex-row md:items-center md:justify-between dark:border-slate-800">
          <div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">
              {{ activeMockSession?.title || 'Mock Interview' }}
            </h2>
            <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
              {{ activeMockSession
                ? 'Trả lời theo đúng ngữ cảnh hồ sơ hiện tại để AI đánh giá và sinh báo cáo cuối phiên.'
                : 'Tạo hoặc chọn một phiên mock interview để bắt đầu luyện phỏng vấn.' }}
            </p>
          </div>

        <div class="flex flex-wrap items-center gap-3">
          <button
            v-if="mockSidebarCollapsed"
            class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="expandMockSidebar"
          >
            Hiện cột trái
          </button>
          <span class="inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold" :class="mockStatusTone">
            <span
              v-if="mockStreaming"
              class="h-2 w-2 animate-pulse rounded-full bg-violet-300 shadow-[0_0_12px_rgba(196,181,253,0.9)]"
            />
            {{ mockStreamStatus }}
          </span>
          <label class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-950/70 dark:text-slate-300">
            <input v-model="streamEnabled" class="accent-violet-500" type="checkbox">
            Dùng stream SSE
            </label>
            <button
              class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              :disabled="!activeMockSessionId || generatingMockReport"
              type="button"
              @click="generateMockReport"
            >
              {{ generatingMockReport ? 'Đang sinh báo cáo...' : 'Sinh báo cáo' }}
            </button>
            <button
              class="rounded-xl border border-red-500/30 px-4 py-2.5 text-sm font-semibold text-red-300 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="!activeMockSessionId"
              type="button"
              @click="deleteMockSession"
            >
              Xóa phiên
            </button>
          </div>
        </div>

        <div v-if="activeMockSessionId" class="mt-5 rounded-2xl border border-slate-200 bg-slate-50/80 p-5 dark:border-slate-800 dark:bg-slate-950/70">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-slate-900 dark:text-white">Tiến độ phỏng vấn</p>
              <p class="mt-1 text-xs text-slate-500 dark:text-slate-500">
                Đã trả lời {{ mockProgress.answeredCount }}/{{ mockProgress.maxQuestions || '--' }} câu · Câu hiện tại {{ mockProgress.currentQuestion }}/{{ mockProgress.maxQuestions || '--' }}
              </p>
            </div>
            <span class="rounded-full bg-violet-500/10 px-3 py-1 text-xs font-semibold text-violet-700 dark:text-violet-200">
              {{ latestMockQuestionMeta.interview_stage_label || 'Đang luyện tập' }}
            </span>
          </div>
          <div class="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
            <div
              class="h-full rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500"
              :style="{ width: `${mockProgress.percent}%` }"
            />
          </div>
        </div>

        <div class="mt-6 rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-950/70">
          <div v-if="loadingMockMessages" class="space-y-4">
            <div v-for="index in 4" :key="index" class="h-16 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
          </div>

          <div v-else-if="!activeMockSessionId" class="flex min-h-[360px] items-center justify-center rounded-2xl border border-dashed border-slate-300 px-8 text-center text-sm leading-7 text-slate-600 dark:border-slate-700 dark:text-slate-400">
            Tạo hoặc chọn một phiên mock interview để nhận câu hỏi đầu tiên từ AI.
          </div>

          <div v-else class="space-y-4">
            <div v-if="!hasMockMessages" class="flex min-h-[320px] items-center justify-center rounded-2xl border border-dashed border-slate-300 px-8 text-center text-sm leading-7 text-slate-600 dark:border-slate-700 dark:text-slate-400">
              Phiên này chưa có nội dung. Hãy tạo phiên mới hoặc tải lại danh sách phiên để nhận câu hỏi đầu tiên.
            </div>

            <div v-else ref="mockMessagesContainer" class="max-h-[520px] space-y-4 overflow-y-auto pr-1">
              <article
                v-for="message in mockMessages.filter((item) => !item.metadata?.hidden_in_ui)"
                :key="message.id"
                class="max-w-[88%] rounded-2xl border px-4 py-3"
                :class="messageBubbleClass(message.role)"
              >
                <div class="mb-2 flex items-center gap-2">
                  <span class="text-xs font-semibold uppercase tracking-wide opacity-80">
                    {{ message.role === 'user' ? 'Bạn' : 'Người phỏng vấn AI' }}
                  </span>
                  <span
                    v-if="message.role === 'assistant'"
                    class="rounded-full bg-slate-200 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-violet-700 dark:bg-slate-800/80 dark:text-violet-200"
                  >
                    {{ getInterviewQuestionLabel(message) }}
                  </span>
                  <span
                    v-if="message.role === 'assistant'"
                    class="rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide"
                    :class="getMockProviderTone(message.metadata?.generation_provider)"
                  >
                    {{ getMockProviderLabel(message.metadata?.generation_provider) }}
                  </span>
                </div>
                <div
                  v-if="message.role === 'assistant' && message.metadata?.streaming && !message.content"
                  class="inline-flex items-center gap-2 text-sm leading-7 text-slate-600 dark:text-slate-300"
                >
                  <span>Đang soạn câu hỏi</span>
                  <span class="inline-flex gap-1">
                    <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-300 [animation-delay:0ms]" />
                    <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-300 [animation-delay:150ms]" />
                    <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-300 [animation-delay:300ms]" />
                  </span>
                </div>
                <p v-else class="whitespace-pre-wrap text-sm leading-7">{{ message.content }}</p>
              </article>
            </div>
          </div>
        </div>

        <div class="mt-5 flex flex-col gap-3 lg:flex-row">
          <textarea
            ref="mockComposerInput"
            v-model="mockAnswerInput"
            class="min-h-[112px] flex-1 rounded-2xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm leading-7 text-white outline-none transition placeholder:text-slate-500 focus:border-violet-500"
            placeholder="Nhập câu trả lời của bạn cho câu hỏi phỏng vấn hiện tại..."
          />
          <button
            class="rounded-2xl bg-gradient-to-r from-violet-600 to-fuchsia-500 px-6 py-4 text-sm font-bold text-white shadow-lg shadow-violet-600/20 transition hover:from-violet-500 hover:to-fuchsia-400 disabled:cursor-not-allowed disabled:opacity-60 lg:w-[180px]"
            :disabled="!mockCanAnswer"
            type="button"
            @click="submitMockAnswer"
          >
            {{ answeringMock ? 'Đang gửi...' : 'Trả lời' }}
          </button>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-800 bg-slate-900/85 p-6 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-white">Báo cáo gần nhất của phiên</h2>
            <p class="mt-1 text-sm text-slate-400">Bản tóm tắt nhanh để bạn biết cần ưu tiên cải thiện gì ngay.</p>
          </div>
          <span class="material-symbols-outlined rounded-xl bg-violet-500/10 p-3 text-violet-300">assignment</span>
        </div>

        <div v-if="generatingMockReport && streamingReportText" class="mt-5 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
          <p class="text-sm font-semibold text-white">Đang stream báo cáo...</p>
          <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300">{{ streamingReportText }}</p>
        </div>

        <div v-else-if="!mockReport" class="mt-5 rounded-2xl border border-dashed border-slate-700 bg-slate-950/50 px-4 py-5 text-sm leading-7 text-slate-400">
          Chưa có báo cáo cho phiên này. Hoàn thành phiên phỏng vấn rồi bấm <strong class="text-white">Sinh báo cáo</strong> để hệ thống tổng hợp điểm mạnh, điểm yếu và kế hoạch cải thiện.
        </div>

        <div v-else class="mt-5 space-y-5">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div class="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
              <p class="text-sm text-slate-400">Tổng điểm</p>
              <p class="mt-2 text-3xl font-bold text-white">{{ Math.round(Number(mockReport.tong_diem || 0)) }}/100</p>
            </div>
            <div class="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
              <p class="text-sm text-slate-400">Kỹ thuật</p>
              <p class="mt-2 text-2xl font-bold text-white">{{ Math.round(Number(mockReport.diem_ky_thuat || 0)) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
              <p class="text-sm text-slate-400">Giao tiếp</p>
              <p class="mt-2 text-2xl font-bold text-white">{{ Math.round(Number(mockReport.diem_giao_tiep || 0)) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
              <p class="text-sm text-slate-400">Phù hợp JD</p>
              <p class="mt-2 text-2xl font-bold text-white">{{ Math.round(Number(mockReport.diem_phu_hop_jd || 0)) }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div class="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
              <p class="text-sm font-semibold text-white">3 việc cần làm ngay</p>
              <ul class="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                <li
                  v-for="(item, index) in (mockReport.metadata?.structured_improvement?.priority_actions || mockReport.uu_tien_cai_thien || []).slice(0, 3)"
                  :key="`${index}-${item}`"
                  class="flex gap-3"
                >
                  <span class="mt-2 h-1.5 w-1.5 rounded-full bg-violet-400"></span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>

            <div class="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
              <p class="text-sm font-semibold text-white">Điểm cần cải thiện nhất</p>
              <p class="mt-4 text-lg font-bold text-violet-200">{{ mockReport.diem_yeu_nhat || mockReport.metadata?.weakest_dimension || 'Đang cập nhật' }}</p>
              <p class="mt-3 text-sm leading-7 text-slate-400">
                {{ mockReport.cau_tra_loi_can_cai_thien_nhat || 'Hệ thống chưa ghi nhận câu trả lời yếu nhất cho phiên này.' }}
              </p>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
            <p class="text-sm font-semibold text-white">Tóm tắt cải thiện</p>
            <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300">
              {{ mockReport.de_xuat_cai_thien_text || 'Báo cáo chi tiết đang được cập nhật.' }}
            </p>
          </div>
        </div>
      </section>
    </section>
  </section>
</template>
