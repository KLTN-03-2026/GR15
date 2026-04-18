import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  adminApplicationService,
  adminProfileService,
  applicationService,
  companyService,
  employerApplicationService,
  employerJobService,
  followCompanyService,
  userService,
} from '@/services/api'
import { getStoredUser } from '@/utils/authStorage'
import { connectPrivateChannel } from '@/services/realtime'
import { APPLICATION_STATUS } from '@/utils/applicationStatus'

const STORAGE_PREFIX = 'app_notifications_read'
const REFRESH_INTERVAL_MS = 60 * 1000

const getBrowserStorage = () => {
  if (typeof window === 'undefined') return null
  return window.localStorage
}

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

const getStorageKey = (role) => {
  const user = getStoredUser()
  if (!user) return null

  const identifier = user.id || user.email || 'anonymous'
  return `${STORAGE_PREFIX}:${role}:${identifier}`
}

const readStoredIds = (role) => {
  const storage = getBrowserStorage()
  const storageKey = getStorageKey(role)
  if (!storage || !storageKey) return new Set()

  try {
    const raw = storage.getItem(storageKey)
    const parsed = raw ? JSON.parse(raw) : []
    return new Set(Array.isArray(parsed) ? parsed : [])
  } catch {
    return new Set()
  }
}

const writeStoredIds = (role, values) => {
  const storage = getBrowserStorage()
  const storageKey = getStorageKey(role)
  if (!storage || !storageKey) return

  storage.setItem(storageKey, JSON.stringify([...values]))
}

const createNotification = ({
  id,
  title,
  message,
  time,
  to,
  icon = 'notifications',
  tone = 'bg-[#2463eb]/10 text-[#2463eb]',
}) => ({
  id: String(id),
  title,
  message,
  time,
  timeLabel: formatNotificationTime(time),
  to,
  icon,
  tone,
})

const getJobActivityType = (job) => {
  const explicitType = String(job?.activity_type || '').toLowerCase()
  if (explicitType === 'reopened') return 'reopened'

  const publishedAt = normalizeTimestamp(job?.published_at || job?.created_at)
  const reopenedAt = normalizeTimestamp(job?.reactivated_at)

  if (reopenedAt && (!publishedAt || reopenedAt >= publishedAt)) {
    return 'reopened'
  }

  return 'published'
}

const getJobActivityTime = (job) => {
  const activityType = getJobActivityType(job)

  if (activityType === 'reopened') {
    return job?.reactivated_at || job?.activity_at || job?.published_at || job?.created_at || null
  }

  return job?.published_at || job?.activity_at || job?.created_at || null
}

const buildFollowedCompanyJobNotification = ({
  company,
  job,
  notificationId,
  message,
}) => {
  const jobId = Number(job?.id)
  if (!jobId) return null

  const activityType = getJobActivityType(job)
  const activityTime = getJobActivityTime(job) || new Date().toISOString()
  const companyId = Number(company?.id)
  const companyName = company?.name || company?.ten_cong_ty || 'Công ty bạn theo dõi'
  const jobTitle = job?.title || job?.tieu_de || 'vị trí tuyển dụng'
  const isReopened = activityType === 'reopened'

  return createNotification({
    id: notificationId || `candidate-followed-company-job-${activityType}-${companyId}-${jobId}-${activityTime}`,
    title: isReopened
      ? 'Công ty bạn theo dõi vừa mở lại tin tuyển dụng'
      : 'Công ty bạn theo dõi vừa đăng job mới',
    message: message || (
      isReopened
        ? `${companyName} vừa mở lại vị trí ${jobTitle}.`
        : `${companyName} vừa đăng vị trí ${jobTitle}.`
    ),
    time: activityTime,
    to: `/jobs/${jobId}`,
    icon: isReopened ? 'update' : 'campaign',
    tone: isReopened
      ? 'bg-amber-500/10 text-amber-600 dark:text-amber-300'
      : 'bg-[#2463eb]/10 text-[#2463eb]',
  })
}

const buildCandidateNotifications = async () => {
  const [applicationsResult, followedCompaniesResult] = await Promise.allSettled([
    applicationService.getApplications({ page: 1, per_page: 12 }),
    followCompanyService.getFollowedCompanies({ page: 1, per_page: 12, recent_jobs_limit: 3 }),
  ])

  const applications = applicationsResult.status === 'fulfilled'
    ? (applicationsResult.value?.data?.data || [])
    : []
  const followedCompanies = followedCompaniesResult.status === 'fulfilled'
    ? (followedCompaniesResult.value?.data?.data || [])
    : []

  const applicationItems = applications
    .map((application) => {
      const baseTitle = application?.tin_tuyen_dung?.tieu_de || application?.ho_so?.tieu_de_ho_so || 'Đơn ứng tuyển'
      const companyName = application?.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'nhà tuyển dụng'
      const appliedTime = application?.updated_at || application?.thoi_gian_ung_tuyen

      if (application?.ngay_hen_phong_van) {
        const attendanceStatus = Number(application?.trang_thai_tham_gia_phong_van)
        const title =
          attendanceStatus === 1
            ? 'Bạn đã xác nhận lịch phỏng vấn'
            : attendanceStatus === 2
              ? 'Bạn đã báo không tham gia phỏng vấn'
              : 'Bạn có lịch phỏng vấn mới'
        const message =
          attendanceStatus === 1
            ? `${baseTitle} tại ${companyName}. Hãy chuẩn bị kỹ cho buổi phỏng vấn sắp tới.`
            : attendanceStatus === 2
              ? `${baseTitle} tại ${companyName}. Bạn đã báo không thể tham gia buổi hẹn này.`
              : `${baseTitle} tại ${companyName}. Hãy kiểm tra lịch hẹn và chuẩn bị sớm.`

        return createNotification({
          id: `candidate-interview-${application.id}-${application.ngay_hen_phong_van}-${attendanceStatus}-${application.thoi_gian_phan_hoi_phong_van || 'pending'}`,
          title,
          message,
          time: application.ngay_hen_phong_van,
          to: '/applications',
          icon: 'calendar_month',
          tone: 'bg-violet-500/10 text-violet-600 dark:text-violet-300',
        })
      }

      switch (Number(application?.trang_thai)) {
        case APPLICATION_STATUS.REVIEWED:
          return createNotification({
            id: `candidate-reviewed-${application.id}-${application.updated_at || application.thoi_gian_ung_tuyen}`,
            title: 'Hồ sơ đã được xem',
            message: `${companyName} đã mở và xem hồ sơ của bạn cho vị trí ${baseTitle}.`,
            time: appliedTime,
            to: '/applications',
            icon: 'visibility',
            tone: 'bg-sky-500/10 text-sky-600 dark:text-sky-300',
          })
        case APPLICATION_STATUS.INTERVIEW_SCHEDULED:
          return createNotification({
            id: `candidate-interview-stage-${application.id}-${application.updated_at || application.ngay_hen_phong_van || application.thoi_gian_ung_tuyen}`,
            title: 'Đơn ứng tuyển đang ở vòng phỏng vấn',
            message: `${companyName} đã chuyển hồ sơ ${baseTitle} sang giai đoạn phỏng vấn.`,
            time: appliedTime,
            to: '/applications',
            icon: 'calendar_month',
            tone: 'bg-violet-500/10 text-violet-600 dark:text-violet-300',
          })
        case APPLICATION_STATUS.INTERVIEW_PASSED:
          return createNotification({
            id: `candidate-passed-${application.id}-${application.updated_at || application.thoi_gian_ung_tuyen}`,
            title: 'Bạn đã qua vòng phỏng vấn',
            message: `${companyName} đã cập nhật kết quả tích cực cho vị trí ${baseTitle}.`,
            time: appliedTime,
            to: '/applications',
            icon: 'workspace_premium',
            tone: 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-300',
          })
        case APPLICATION_STATUS.HIRED:
          return createNotification({
            id: `candidate-accepted-${application.id}-${application.updated_at || application.thoi_gian_ung_tuyen}`,
            title: 'Chúc mừng, bạn đã trúng tuyển',
            message: `${companyName} đã chốt kết quả trúng tuyển cho vị trí ${baseTitle}.`,
            time: appliedTime,
            to: '/applications',
            icon: 'task_alt',
            tone: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300',
          })
        case APPLICATION_STATUS.REJECTED:
          return createNotification({
            id: `candidate-rejected-${application.id}-${application.updated_at || application.thoi_gian_ung_tuyen}`,
            title: 'Đơn ứng tuyển đã có kết quả',
            message: `${companyName} đã cập nhật kết quả cho vị trí ${baseTitle}.`,
            time: appliedTime,
            to: '/applications',
            icon: 'cancel',
            tone: 'bg-rose-500/10 text-rose-600 dark:text-rose-300',
          })
        default:
          return null
      }
    })
    .filter(Boolean)

  const followItems = followedCompanies
    .flatMap((company) => {
      const followedAt = normalizeTimestamp(company?.theo_doi_luc)

      return (company?.tin_tuyen_dungs || [])
        .map((job) => {
          if (Number(job?.trang_thai) !== 1) return null

          const publishedAt = normalizeTimestamp(job?.published_at || job?.created_at)
          const reopenedAt = normalizeTimestamp(job?.reactivated_at)

          if (reopenedAt && (!followedAt || reopenedAt >= followedAt)) {
            return buildFollowedCompanyJobNotification({
              company,
              job: {
                ...job,
                activity_type: 'reopened',
                activity_at: job?.reactivated_at,
              },
            })
          }

          if (publishedAt && (!followedAt || publishedAt >= followedAt)) {
            return buildFollowedCompanyJobNotification({
              company,
              job: {
                ...job,
                activity_type: 'published',
                activity_at: job?.published_at || job?.created_at,
              },
            })
          }

          return null
        })
        .filter(Boolean)
    })

  return [...applicationItems, ...followItems]
    .sort((a, b) => normalizeTimestamp(b.time) - normalizeTimestamp(a.time))
    .slice(0, 8)
}

const buildEmployerNotifications = async () => {
  const [applicationsResponse, jobsResponse] = await Promise.all([
    employerApplicationService.getApplications({ page: 1, per_page: 12 }),
    employerJobService.getJobs({ page: 1, per_page: 20 }),
  ])

  const applications = applicationsResponse?.data?.data || []
  const jobs = jobsResponse?.data?.data || []
  const items = []

  applications.forEach((application) => {
    const jobTitle = application?.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng'
    const profileTitle = application?.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên'
    const candidateName = application?.nguoi_dung?.ho_ten || application?.ho_so?.nguoi_dung?.ho_ten || 'Ứng viên'

    if (Number(application?.trang_thai) === APPLICATION_STATUS.PENDING) {
      items.push(
        createNotification({
          id: `employer-pending-${application.id}-${application.thoi_gian_ung_tuyen}`,
          title: 'Có hồ sơ mới đang chờ xử lý',
          message: `${candidateName} vừa nộp ${profileTitle} cho vị trí ${jobTitle}.`,
          time: application.thoi_gian_ung_tuyen,
          to: '/employer/interviews',
          icon: 'hourglass_top',
          tone: 'bg-amber-500/10 text-amber-600 dark:text-amber-300',
        }),
      )
    }

    if (application?.ngay_hen_phong_van) {
      items.push(
        createNotification({
          id: `employer-scheduled-${application.id}-${application.ngay_hen_phong_van}`,
          title: 'Bạn có lịch phỏng vấn sắp tới',
          message: `${candidateName} sẽ phỏng vấn cho vị trí ${jobTitle}.`,
          time: application.ngay_hen_phong_van,
          to: '/employer/interviews',
          icon: 'calendar_month',
          tone: 'bg-violet-500/10 text-violet-600 dark:text-violet-300',
        }),
      )
    }

    if (Number(application?.trang_thai) === APPLICATION_STATUS.INTERVIEW_PASSED) {
      items.push(
        createNotification({
          id: `employer-passed-stage-${application.id}-${application.updated_at || application.ngay_hen_phong_van || application.thoi_gian_ung_tuyen}`,
          title: 'Ứng viên đã qua vòng phỏng vấn',
          message: `${candidateName} vừa được cập nhật sang trạng thái qua phỏng vấn cho vị trí ${jobTitle}.`,
          time: application.updated_at || application.ngay_hen_phong_van || application.thoi_gian_ung_tuyen,
          to: '/employer/interviews',
          icon: 'verified',
          tone: 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-300',
        }),
      )
    }

    if (Number(application?.trang_thai) === APPLICATION_STATUS.HIRED) {
      items.push(
        createNotification({
          id: `employer-hired-${application.id}-${application.updated_at || application.thoi_gian_ung_tuyen}`,
          title: 'Đã chốt trúng tuyển',
          message: `${candidateName} đã được đánh dấu trúng tuyển cho vị trí ${jobTitle}.`,
          time: application.updated_at || application.thoi_gian_ung_tuyen,
          to: '/employer/interviews',
          icon: 'task_alt',
          tone: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300',
        }),
      )
    }

    if (Number(application?.trang_thai) === APPLICATION_STATUS.REJECTED) {
      items.push(
        createNotification({
          id: `employer-rejected-${application.id}-${application.updated_at || application.thoi_gian_ung_tuyen}`,
          title: 'Đơn đã được từ chối',
          message: `${candidateName} đã được cập nhật kết quả từ chối cho vị trí ${jobTitle}.`,
          time: application.updated_at || application.thoi_gian_ung_tuyen,
          to: '/employer/interviews',
          icon: 'cancel',
          tone: 'bg-rose-500/10 text-rose-600 dark:text-rose-300',
        }),
      )
    }

    if (Number(application?.trang_thai_tham_gia_phong_van) === 1) {
      items.push(
        createNotification({
          id: `employer-confirmed-${application.id}-${application.thoi_gian_phan_hoi_phong_van || application.updated_at}`,
          title: 'Ứng viên đã xác nhận tham gia',
          message: `${candidateName} đã xác nhận tham gia phỏng vấn cho vị trí ${jobTitle}.`,
          time: application.thoi_gian_phan_hoi_phong_van || application.updated_at || application.ngay_hen_phong_van,
          to: '/employer/interviews',
          icon: 'how_to_reg',
          tone: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300',
        }),
      )
    }

    if (Number(application?.trang_thai_tham_gia_phong_van) === 2) {
      items.push(
        createNotification({
          id: `employer-declined-${application.id}-${application.thoi_gian_phan_hoi_phong_van || application.updated_at}`,
          title: 'Ứng viên báo không thể tham gia',
          message: `${candidateName} không thể tham gia lịch phỏng vấn cho vị trí ${jobTitle}.`,
          time: application.thoi_gian_phan_hoi_phong_van || application.updated_at || application.ngay_hen_phong_van,
          to: '/employer/interviews',
          icon: 'event_busy',
          tone: 'bg-rose-500/10 text-rose-600 dark:text-rose-300',
        }),
      )
    }

    if (application?.da_rut_don) {
      items.push(
        createNotification({
          id: `employer-withdrawn-${application.id}-${application.thoi_gian_rut_don || application.updated_at}`,
          title: 'Ứng viên đã rút đơn',
          message: `${candidateName} đã rút đơn ứng tuyển cho vị trí ${jobTitle}.`,
          time: application.thoi_gian_rut_don || application.updated_at || application.thoi_gian_ung_tuyen,
          to: '/employer/interviews',
          icon: 'person_remove',
          tone: 'bg-slate-500/10 text-slate-600 dark:text-slate-300',
        }),
      )
    }
  })

  jobs.forEach((job) => {
    if (job?.da_tuyen_du) {
      items.push(
        createNotification({
          id: `employer-quota-full-${job.id}-${job.updated_at || job.created_at}`,
          title: 'Tin tuyển dụng đã đủ chỉ tiêu',
          message: `${job.tieu_de} đã tuyển đủ số lượng cần thiết.`,
          time: job.updated_at || job.created_at,
          to: `/employer/jobs/${job.id}`,
          icon: 'groups',
          tone: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300',
        }),
      )
    } else if (Number(job?.so_luong_con_lai) === 1) {
      items.push(
        createNotification({
          id: `employer-quota-low-${job.id}-${job.updated_at || job.created_at}`,
          title: 'Tin tuyển dụng sắp đủ chỉ tiêu',
          message: `${job.tieu_de} chỉ còn 1 vị trí tuyển dụng.`,
          time: job.updated_at || job.created_at,
          to: `/employer/jobs/${job.id}`,
          icon: 'priority_high',
          tone: 'bg-orange-500/10 text-orange-600 dark:text-orange-300',
        }),
      )
    }
  })

  return items
    .sort((a, b) => normalizeTimestamp(b.time) - normalizeTimestamp(a.time))
    .slice(0, 8)
}

const buildAdminNotifications = async () => {
  const [applicationStatsResponse, profileStatsResponse, userStatsResponse, companyStatsResponse] = await Promise.all([
    adminApplicationService.getStats(),
    adminProfileService.getStats(),
    userService.getUserStats(),
    companyService.getCompanyStats(),
  ])

  const applicationStats = applicationStatsResponse?.data || {}
  const profileStats = profileStatsResponse?.data || {}
  const userStats = userStatsResponse?.data || {}
  const companyStats = companyStatsResponse?.data || {}

  const now = new Date().toISOString()
  const items = []

  if ((applicationStats?.chi_tiet?.cho_duyet || 0) > 0) {
    items.push(
      createNotification({
        id: `admin-pending-applications-${applicationStats.chi_tiet.cho_duyet}`,
        title: 'Có đơn ứng tuyển đang chờ xử lý',
        message: `${applicationStats.chi_tiet.cho_duyet} đơn đang chờ nhà tuyển dụng phản hồi.`,
        time: now,
        to: '/admin/applications',
        icon: 'pending_actions',
        tone: 'bg-amber-500/10 text-amber-600 dark:text-amber-300',
      }),
    )
  }

  if ((profileStats?.da_xoa_mem || 0) > 0) {
    items.push(
      createNotification({
        id: `admin-archived-profiles-${profileStats.da_xoa_mem}`,
        title: 'Hồ sơ đang nằm trong lưu trữ',
        message: `${profileStats.da_xoa_mem} hồ sơ đang được lưu trữ và có thể cần rà soát lại.`,
        time: now,
        to: '/admin/profiles',
        icon: 'inventory_2',
        tone: 'bg-rose-500/10 text-rose-600 dark:text-rose-300',
      }),
    )
  }

  if ((userStats?.bi_khoa || 0) > 0) {
    items.push(
      createNotification({
        id: `admin-locked-users-${userStats.bi_khoa}`,
        title: 'Có tài khoản đang bị khóa',
        message: `${userStats.bi_khoa} tài khoản hiện đang bị khóa hoặc cần kiểm tra lại.`,
        time: now,
        to: '/admin/users',
        icon: 'lock_person',
        tone: 'bg-slate-500/10 text-slate-600 dark:text-slate-300',
      }),
    )
  }

  if ((companyStats?.tam_ngung || 0) > 0) {
    items.push(
      createNotification({
        id: `admin-paused-companies-${companyStats.tam_ngung}`,
        title: 'Có công ty đang tạm ngưng',
        message: `${companyStats.tam_ngung} công ty đang ở trạng thái tạm ngưng hoạt động.`,
        time: now,
        to: '/admin/companies',
        icon: 'business_center',
        tone: 'bg-sky-500/10 text-sky-600 dark:text-sky-300',
      }),
    )
  }

  return items.slice(0, 8)
}

const loaders = {
  candidate: buildCandidateNotifications,
  employer: buildEmployerNotifications,
  admin: buildAdminNotifications,
}

export const useNotifications = (role) => {
  const loading = ref(false)
  const error = ref('')
  const rawItems = ref([])
  const liveItems = ref([])
  const readIds = ref(new Set())
  let refreshTimer = null
  let realtimeChannel = null

  const mergedNotifications = computed(() => {
    const byId = new Map()
    const combinedItems = [...liveItems.value, ...rawItems.value]

    combinedItems
      .sort((a, b) => normalizeTimestamp(b.time) - normalizeTimestamp(a.time))
      .forEach((item) => {
        if (!byId.has(item.id)) {
          byId.set(item.id, item)
        }
      })

    return [...byId.values()]
  })

  const items = computed(() =>
    mergedNotifications.value.map((item) => ({
      ...item,
      read: readIds.value.has(item.id),
    })),
  )

  const unreadCount = computed(() => items.value.filter((item) => !item.read).length)

  const hydrateReadState = () => {
    readIds.value = readStoredIds(role)
  }

  const persistReadState = () => {
    writeStoredIds(role, readIds.value)
  }

  const markAsRead = (id) => {
    if (!id) return
    readIds.value = new Set(readIds.value).add(String(id))
    persistReadState()
  }

  const markAllAsRead = () => {
    const nextReadIds = new Set(readIds.value)
    mergedNotifications.value.forEach((item) => nextReadIds.add(item.id))
    readIds.value = nextReadIds
    persistReadState()
  }

  const pushLiveItem = (item) => {
    if (!item?.id) return

    const nextItems = [item, ...liveItems.value.filter((existing) => existing.id !== item.id)]
    liveItems.value = nextItems
  }

  const subscribeCandidateRealtime = () => {
    if (role !== 'candidate') return

    const user = getStoredUser()
    if (Number(user?.vai_tro) !== 0 || !user?.id) return

    const realtimeChannelName = `candidate.${user.id}`

    realtimeChannel = connectPrivateChannel(realtimeChannelName)

    realtimeChannel?.listen('.company.job-activity', (payload) => {
      const notification = buildFollowedCompanyJobNotification({
        company: payload?.company,
        job: payload?.job,
        notificationId: payload?.notification_id,
        message: payload?.message,
      })

      if (!notification) return

      pushLiveItem(notification)
    })
  }

  const refresh = async () => {
    const loader = loaders[role]
    if (!loader) return

    loading.value = true
    error.value = ''

    try {
      rawItems.value = await loader()
    } catch (err) {
      error.value = err?.message || 'Không tải được thông báo.'
      rawItems.value = []
    } finally {
      loading.value = false
    }
  }

  const handleWindowFocus = () => {
    void refresh()
  }

  onMounted(() => {
    hydrateReadState()
    void refresh()
    subscribeCandidateRealtime()

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
      realtimeChannel.stopListening('.company.job-activity')
      realtimeChannel = null
    }

    if (refreshTimer) {
      window.clearInterval(refreshTimer)
    }
  })

  return {
    items,
    loading,
    error,
    unreadCount,
    refresh,
    markAsRead,
    markAllAsRead,
  }
}
