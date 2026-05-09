export const normalizeExperienceYears = (value) => {
  if (value === null || value === undefined || value === '') return 0
  if (typeof value === 'number') return Number.isFinite(value) ? Number(value.toFixed(2)) : 0

  const text = String(value).trim().toLowerCase()
  if (!text) return 0

  const match = text.replace(',', '.').match(/\d+(?:\.\d+)?/)
  if (!match) return value

  const amount = Number(match[0])
  if (!Number.isFinite(amount)) return value

  const isMonthValue =
    text.includes('tháng')
    || text.includes('thang')
    || /\b(month|months|mo)\b/.test(text)

  return Number((isMonthValue ? amount / 12 : amount).toFixed(2))
}

export const formatExperienceYears = (value) => {
  const years = Number(value || 0)
  if (!Number.isFinite(years) || years <= 0) return '0 năm'
  if (years < 1) {
    const months = Math.round(years * 12)
    return `${months} tháng`
  }
  return `${Number(years.toFixed(2)).toString()} năm`
}

export const normalizeExperienceRequirementText = (value) => {
  if (value === null || value === undefined) return ''

  const text = String(value).trim()
  if (!text) return ''

  const normalized = text.toLowerCase()
  const looksLikeSingleDuration = /^[\d\s.,]+(?:năm|nam|year|years|tháng|thang|month|months|mo)?$/i.test(text)

  if (!looksLikeSingleDuration) {
    return text
  }

  const years = normalizeExperienceYears(normalized)
  if (typeof years !== 'number' || !Number.isFinite(years)) {
    return text
  }

  return formatExperienceYears(years)
}
