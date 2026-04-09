const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

const getPublicBaseUrls = () => {
  const bases = []

  if (apiBaseUrl) {
    try {
      const apiUrl = new URL(apiBaseUrl)
      bases.push(apiUrl.origin)

      if (apiUrl.hostname === '127.0.0.1') {
        bases.push(`${apiUrl.protocol}//localhost${apiUrl.port ? `:${apiUrl.port}` : ''}`)
      }

      if (apiUrl.hostname === 'localhost') {
        bases.push(`${apiUrl.protocol}//127.0.0.1${apiUrl.port ? `:${apiUrl.port}` : ''}`)
      }
    } catch {
      bases.push(apiBaseUrl.replace(/\/api(?:\/v\d+)?$/, ''))
    }
  }


  return [...new Set(bases.filter(Boolean))]
}

export const buildStorageAssetCandidates = (value) => {
  if (!value) {
    return []
  }

  if (
    value.startsWith('http://') ||
    value.startsWith('https://') ||
    value.startsWith('blob:') ||
    value.startsWith('data:')
  ) {
    return [value]
  }

  const trimmedValue = value.replace(/^\/+/, '')
  const normalizedPath = trimmedValue.replace(/^storage\//, '').replace(/^public\/storage\//, '')
  const baseUrls = getPublicBaseUrls()
  const candidates = []

  baseUrls.forEach((baseUrl) => {
    candidates.push(`${baseUrl}/storage/${normalizedPath}`)
  })

  return [...new Set(candidates)]
}

export const resolvePrimaryStorageAssetUrl = (value) => {
  return buildStorageAssetCandidates(value)[0] || ''
}
