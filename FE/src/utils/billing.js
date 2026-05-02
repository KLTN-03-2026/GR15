export const FEATURE_DISPLAY_ORDER = [
  'cover_letter_generation',
  'career_report_generation',
  'chatbot_message',
  'mock_interview_session',
  'employer_featured_job_7d',
  'employer_featured_job_30d',
  'employer_shortlist_ai_explanation',
  'employer_candidate_compare_ai',
  'interview_copilot_generate',
  'interview_copilot_evaluate',
]

export const getBillingFeatureLabel = (featureCode) => {
  if (featureCode === 'cover_letter_generation') return 'Cover Letter AI'
  if (featureCode === 'career_report_generation') return 'Career Report'
  if (featureCode === 'chatbot_message') return 'Chatbot tư vấn nghề nghiệp'
  if (featureCode === 'mock_interview_session') return 'Mock Interview'
  if (featureCode === 'employer_featured_job_7d') return 'Featured Job 7 ngày'
  if (featureCode === 'employer_featured_job_30d') return 'Featured Job 30 ngày'
  if (featureCode === 'employer_shortlist_ai_explanation') return 'AI Shortlist ứng viên'
  if (featureCode === 'employer_candidate_compare_ai') return 'AI Compare ứng viên'
  if (featureCode === 'interview_copilot_generate') return 'AI Interview Copilot'
  if (featureCode === 'interview_copilot_evaluate') return 'AI Evaluate Interview'
  return featureCode || 'Tính năng AI'
}

export const sortEntitlementsByFeature = (entitlements = []) =>
  [...entitlements].sort((left, right) => {
    const leftIndex = FEATURE_DISPLAY_ORDER.indexOf(left.feature_code)
    const rightIndex = FEATURE_DISPLAY_ORDER.indexOf(right.feature_code)

    if (leftIndex === -1 && rightIndex === -1) {
      return String(left.feature_label || '').localeCompare(String(right.feature_label || ''))
    }

    if (leftIndex === -1) return 1
    if (rightIndex === -1) return -1
    return leftIndex - rightIndex
  })

export const getEntitlementLabel = (item) =>
  item?.feature_label || getBillingFeatureLabel(item?.feature_code)

export const getFreeQuotaText = (item, options = {}) => {
  if (!item?.has_free_quota) {
    return options.emptyLabel || 'Không có'
  }

  return `${Number(item.free_quota_remaining || 0)}/${Number(item.free_quota_total || 0)}`
}

export const getSubscriptionQuotaText = (item, options = {}) => {
  if (!item?.subscription_included) {
    if (options.hasCurrentSubscription) {
      return options.excludedLabel || 'Không có'
    }

    return options.inactiveLabel || 'Chưa kích hoạt'
  }

  if (item.subscription_is_unlimited) {
    return options.unlimitedLabel || 'Không giới hạn'
  }

  return `${Number(item.subscription_quota_remaining || 0)}/${Number(item.subscription_quota_total || 0)}`
}

export const getCompactAiQuotaText = (item, options = {}) => {
  const unit = options.unit || 'lượt'
  const inactiveLabel = options.inactiveLabel || 'Dùng ví AI'

  if (!item) {
    return options.emptyLabel || 'Đang cập nhật'
  }

  if (item.subscription_is_unlimited) {
    return 'Không giới hạn'
  }

  if (item.subscription_included && Number(item.subscription_quota_total || 0) > 0) {
    return `${Number(item.subscription_quota_remaining || 0)}/${Number(item.subscription_quota_total || 0)} ${unit}`
  }

  if (item.has_free_quota && Number(item.free_quota_total || 0) > 0) {
    return `${Number(item.free_quota_remaining || 0)}/${Number(item.free_quota_total || 0)} ${unit}`
  }

  return inactiveLabel
}

export const getEntitlementActionLabel = (
  item,
  {
    actionLabel = 'Dùng AI',
    price = 0,
    formatCurrency = (value) => String(value),
  } = {},
) => {
  if (Number(item?.subscription_quota_remaining || 0) > 0) {
    return `${actionLabel} · ${item.subscription_quota_remaining}/${item.subscription_quota_total}`
  }

  if (Number(item?.free_quota_remaining || 0) > 0) {
    return `${actionLabel} · Miễn phí ${item.free_quota_remaining}/${item.free_quota_total}`
  }

  if (Number(price || 0) > 0) {
    return `${actionLabel} · ${formatCurrency(price)}`
  }

  return `${actionLabel} · Theo ví AI`
}

export const getEntitlementCoverageNote = (
  item,
  {
    currentSubscription = null,
    featureLabel = getEntitlementLabel(item),
    price = 0,
    formatCurrency = (value) => String(value),
  } = {},
) => {
  if (Number(item?.subscription_quota_remaining || 0) > 0) {
    return `Gói ${currentSubscription?.goi_dich_vu?.ten_goi || 'Pro'} đang còn ${item.subscription_quota_remaining}/${item.subscription_quota_total} lượt ${featureLabel}.`
  }

  if (Number(item?.free_quota_remaining || 0) > 0) {
    return `Bạn còn ${item.free_quota_remaining}/${item.free_quota_total} lượt miễn phí cho ${featureLabel}.`
  }

  if (Number(price || 0) > 0) {
    return `Mỗi lần dùng ${featureLabel} hiện được tính ${formatCurrency(price)} khi không còn quota.`
  }

  return `${featureLabel} sẽ dùng ví AI khi không còn quota miễn phí hoặc quota Pro.`
}

export const getEntitlementUsageHint = (
  item,
  {
    currentSubscription = null,
    successOutcomeText = 'yêu cầu hoàn tất thành công',
  } = {},
) => {
  if (Number(item?.subscription_quota_remaining || 0) > 0) {
    return `Yêu cầu này sẽ dùng quota ${currentSubscription?.goi_dich_vu?.ten_goi || 'Pro'} trước khi fallback sang ví AI.`
  }

  if (Number(item?.free_quota_remaining || 0) > 0) {
    return 'Yêu cầu này sẽ dùng lượt miễn phí hiện có trước khi fallback sang ví AI.'
  }

  return `Yêu cầu này sẽ trừ ví sau khi ${successOutcomeText}.`
}
