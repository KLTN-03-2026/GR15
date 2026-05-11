export const routeId = (value) => {
  if (value && typeof value === 'object') {
    return value.encoded_id || value.route_id || value.public_id || value.id
  }

  return value
}

export const encodedRouteParam = (value) => encodeURIComponent(String(routeId(value) || ''))
