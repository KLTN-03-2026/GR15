import { computed, onMounted, onUnmounted, ref } from 'vue'
import { notificationService } from '@/services/api'
import { getStoredUser } from '@/utils/authStorage'
import { connectPrivateChannel, realtimeEnabled, subscribeRealtimeStatus } from '@/services/realtime'
import { useNotify } from '@/composables/useNotify'

const REFRESH_INTERVAL_MS = 60 * 1000

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const parsed = new Date(value).getTime()
  return Number.isNaN(parsed) ? 0 : parsed
}

const formatNotificationTime = (value) => {
  const timestamp = normalizeTimestamp(value)
  if (!timestamp) return 'Vừa xong'

  const diffMs = Date.now() - timestamp
  const diffMinutes = Math.round(diffMs / (60 * 1000))

  if (diffMinutes < 1) return 'Vừa xong'
  if (diffMinutes < 60) return `${diffMinutes} phút trước`

  const diffHours = Math.round(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours} giờ trước`

  const diffDays = Math.round(diffHours / 24)
  if (diffDays < 7) return `${diffDays} ngày trước`

  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(timestamp))
}

const toneByType = (type) => {
  const normalizedType = String(type || '')

  if (normalizedType.includes('interview')) return 'bg-violet-500/10 text-violet-600 dark:text-violet-300'
  if (normalizedType.includes('onboarding')) return 'bg-blue-500/10 text-blue-600 dark:text-blue-300'
  if (normalizedType.includes('offer') || normalizedType.includes('hired')) return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300'
  if (normalizedType.includes('rejected') || normalizedType.includes('declined')) return 'bg-rose-500/10 text-rose-600 dark:text-rose-300'
  if (normalizedType.includes('follow') || normalizedType.includes('job')) return 'bg-[#2463eb]/10 text-[#2463eb]'
  if (normalizedType.includes('admin')) return 'bg-sky-500/10 text-sky-600 dark:text-sky-300'

  return 'bg-[#2463eb]/10 text-[#2463eb]'
}

const iconByType = (type) => {
  const normalizedType = String(type || '')

  if (normalizedType.includes('interview')) return 'calendar_month'
  if (normalizedType.includes('onboarding')) return 'fact_check'
  if (normalizedType.includes('offer')) return 'workspace_premium'
  if (normalizedType.includes('hired')) return 'task_alt'
  if (normalizedType.includes('rejected') || normalizedType.includes('declined')) return 'cancel'
  if (normalizedType.includes('follow')) return 'campaign'
  if (normalizedType.includes('application')) return 'assignment'
  if (normalizedType.includes('job')) return 'work'
  if (normalizedType.includes('admin')) return 'admin_panel_settings'

  return 'notifications'
}

const deriveNotificationRoute = (item) => {
  const path = item.to || '#'
  const data = item.data || item.du_lieu_bo_sung || {}
  const applicationId = data.ung_tuyen_id || data.application_id
  const type = String(item.type || '')
  const focusSection = data.focus_section
    || (data.source === 'onboarding' || data.onboarding_plan_id ? 'onboarding' : '')
    || (data.interview_round_id || type.includes('interview') ? 'interview' : '')
    || (type.includes('offer') ? 'offer' : '')
    || (type.includes('application') ? 'timeline' : '')

  const appendDeepLinkParams = (basePath) => {
    const params = new URLSearchParams()
    params.set('highlight_application_id', applicationId)
    if (focusSection) params.set('focus_section', focusSection)
    if (data.interview_round_id) params.set('interview_round_id', data.interview_round_id)
    if (data.onboarding_plan_id) params.set('onboarding_plan_id', data.onboarding_plan_id)
    if (data.onboarding_task_id) params.set('onboarding_task_id', data.onboarding_task_id)

    return `${basePath}?${params.toString()}`
  }

  if (applicationId && path === '/applications') {
    return appendDeepLinkParams('/applications')
  }

  if (applicationId && path === '/employer/interviews') {
    return appendDeepLinkParams('/employer/interviews')
  }

  const jobId = data.tin_tuyen_dung_id || data.job_id
  if (jobId && (path === '/jobs' || path === '#')) {
    return `/jobs/${encodeURIComponent(jobId)}`
  }

  return path
}

const normalizeNotification = (item) => ({
  id: String(item.id),
  title: item.title || 'Thông báo',
  message: item.message || '',
  time: item.created_at,
  timeLabel: formatNotificationTime(item.created_at),
  to: deriveNotificationRoute(item),
  icon: iconByType(item.type),
  tone: toneByType(item.type),
  read: Boolean(item.read_at),
  type: item.type,
  data: item.data || null,
})

export const useNotifications = () => {
  const notify = useNotify()
  const loading = ref(false)
  const error = ref('')
  const rawItems = ref([])
  const unreadCount = ref(0)
  const realtimeStatus = ref(realtimeEnabled() ? 'idle' : 'disabled')
  const lastLiveAt = ref(null)
  let refreshTimer = null
  let realtimeChannel = null
  let unsubscribeRealtimeStatus = null

  const realtimeStatusLabel = computed(() => {
    switch (realtimeStatus.value) {
      case 'connected':
        return 'Đang realtime'
      case 'connecting':
      case 'idle':
        return 'Đang kết nối'
      case 'unavailable':
      case 'failed':
      case 'error':
        return 'Mất realtime, đang dùng tự tải lại'
      case 'disconnected':
        return 'Đã ngắt realtime'
      case 'disabled':
        return 'Chưa cấu hình realtime'
      default:
        return 'Trạng thái realtime chưa rõ'
    }
  })

  const isRealtimeConnected = computed(() => realtimeStatus.value === 'connected')

  const items = computed(() =>
    rawItems.value
      .slice()
      .sort((a, b) => normalizeTimestamp(b.time) - normalizeTimestamp(a.time)),
  )

  const refresh = async () => {
    loading.value = true
    error.value = ''

    try {
      const response = await notificationService.getNotifications({ page: 1, per_page: 10 })
      const payload = response?.data || {}
      const itemPayload = payload.items || {}
      rawItems.value = (itemPayload.data || []).map(normalizeNotification)
      unreadCount.value = Number(payload.unread_count || 0)
    } catch (err) {
      error.value = err?.message || 'Không tải được thông báo.'
      rawItems.value = []
      unreadCount.value = 0
    } finally {
      loading.value = false
    }
  }

  const markAsRead = async (id) => {
    if (!id) return

    const targetId = String(id)
    const target = rawItems.value.find((item) => item.id === targetId)
    if (target?.read) return

    rawItems.value = rawItems.value.map((item) =>
      item.id === targetId ? { ...item, read: true } : item,
    )
    unreadCount.value = Math.max(0, unreadCount.value - 1)

    try {
      await notificationService.markAsRead(targetId)
    } catch {
      await refresh()
    }
  }

  const markAllAsRead = async () => {
    if (unreadCount.value === 0) return

    rawItems.value = rawItems.value.map((item) => ({ ...item, read: true }))
    unreadCount.value = 0

    try {
      await notificationService.markAllAsRead()
    } catch {
      await refresh()
    }
  }

  const pushLiveNotification = (payload) => {
    if (!payload?.id) return

    const item = normalizeNotification({
      id: payload.id,
      type: payload.type,
      title: payload.title,
      message: payload.message,
      to: payload.to,
      data: payload.data,
      read_at: payload.read_at,
      created_at: payload.created_at || new Date().toISOString(),
    })

    rawItems.value = [item, ...rawItems.value.filter((existing) => existing.id !== item.id)].slice(0, 10)
    unreadCount.value += item.read ? 0 : 1
    lastLiveAt.value = item.time || new Date().toISOString()

    if (!item.read) {
      notify.info(item.message ? `${item.title}: ${item.message}` : item.title, {
        timeout: 4500,
        onClick: () => {
          if (item.to && item.to !== '#') {
            window.location.assign(item.to)
          }
        },
      })
    }
  }

  const subscribeRealtime = () => {
    const user = getStoredUser()
    if (!user?.id || !realtimeEnabled()) {
      realtimeStatus.value = realtimeEnabled() ? 'disconnected' : 'disabled'
      return
    }

    unsubscribeRealtimeStatus = subscribeRealtimeStatus((status) => {
      realtimeStatus.value = status
    })

    realtimeChannel = connectPrivateChannel(`user.${user.id}`)
    realtimeChannel?.listen('.notification.created', pushLiveNotification)
  }

  const handleWindowFocus = () => {
    void refresh()
  }

  onMounted(() => {
    void refresh()
    subscribeRealtime()

    if (typeof window !== 'undefined') {
      window.addEventListener('focus', handleWindowFocus)
      refreshTimer = window.setInterval(() => {
        void refresh()
      }, REFRESH_INTERVAL_MS)
    }
  })

  onUnmounted(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('focus', handleWindowFocus)
    }

    if (realtimeChannel) {
      realtimeChannel.stopListening('.notification.created')
      realtimeChannel = null
    }

    if (refreshTimer) {
      window.clearInterval(refreshTimer)
    }

    if (unsubscribeRealtimeStatus) {
      unsubscribeRealtimeStatus()
      unsubscribeRealtimeStatus = null
    }
  })

  return {
    items,
    loading,
    error,
    unreadCount,
    realtimeStatus,
    realtimeStatusLabel,
    isRealtimeConnected,
    lastLiveAt,
    refresh,
    markAsRead,
    markAllAsRead,
  }
}
