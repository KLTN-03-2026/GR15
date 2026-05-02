import Echo from 'laravel-echo'
import Pusher from 'pusher-js'

import { getAuthToken } from '@/utils/authStorage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const REVERB_APP_KEY = import.meta.env.VITE_REVERB_APP_KEY || ''
const REVERB_HOST = import.meta.env.VITE_REVERB_HOST || (typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1')
const REVERB_PORT = Number(import.meta.env.VITE_REVERB_PORT || 8080)
const REVERB_SCHEME = (import.meta.env.VITE_REVERB_SCHEME || 'http').toLowerCase()

let echoInstance = null
let currentToken = null
let authListenersRegistered = false
const statusListeners = new Set()

const isRealtimeConfigured = () => Boolean(REVERB_APP_KEY && REVERB_HOST && REVERB_PORT)
let connectionStatus = isRealtimeConfigured() ? 'idle' : 'disabled'

const notifyStatusListeners = (status, detail = {}) => {
  connectionStatus = status

  statusListeners.forEach((listener) => {
    try {
      listener(status, detail)
    } catch {
      // UI listeners should not be able to break realtime connection handling.
    }
  })
}

const bindConnectionStatusEvents = (echo) => {
  const connection = echo?.connector?.pusher?.connection
  if (!connection?.bind) return

  connection.bind('state_change', (states = {}) => {
    const nextStatus = states.current || 'unknown'

    if (['connecting', 'connected', 'unavailable', 'failed', 'disconnected'].includes(nextStatus)) {
      notifyStatusListeners(nextStatus, states)
      return
    }

    notifyStatusListeners('unknown', states)
  })

  connection.bind('connected', () => notifyStatusListeners('connected'))
  connection.bind('unavailable', () => notifyStatusListeners('unavailable'))
  connection.bind('failed', () => notifyStatusListeners('failed'))
  connection.bind('disconnected', () => notifyStatusListeners('disconnected'))
  connection.bind('error', (error) => notifyStatusListeners('error', { error }))
}

const getBackendOrigin = () => {
  if (typeof window === 'undefined') return ''

  try {
    return new URL(API_BASE_URL).origin
  } catch {
    return window.location.origin
  }
}

const registerAuthListeners = () => {
  if (authListenersRegistered || typeof window === 'undefined') return

  const handleAuthReset = () => {
    disconnectRealtime()
  }

  window.addEventListener('auth-changed', handleAuthReset)
  window.addEventListener('auth-invalidated', handleAuthReset)

  authListenersRegistered = true
}

const createEcho = () => {
  if (typeof window === 'undefined' || !isRealtimeConfigured()) {
    notifyStatusListeners('disabled')
    return null
  }

  const token = getAuthToken()

  if (echoInstance && currentToken === token) {
    return echoInstance
  }

  if (echoInstance) {
    echoInstance.disconnect()
    echoInstance = null
    currentToken = null
  }

  window.Pusher = Pusher
  notifyStatusListeners('connecting')

  echoInstance = new Echo({
    broadcaster: 'reverb',
    key: REVERB_APP_KEY,
    wsHost: REVERB_HOST,
    wsPort: REVERB_PORT,
    wssPort: REVERB_PORT,
    forceTLS: REVERB_SCHEME === 'https',
    enabledTransports: ['ws', 'wss'],
    authEndpoint: `${getBackendOrigin()}/broadcasting/auth`,
    auth: {
      headers: {
        Accept: 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    },
  })

  bindConnectionStatusEvents(echoInstance)
  currentToken = token
  registerAuthListeners()

  return echoInstance
}

export const connectPublicChannel = (channelName) => createEcho()?.channel(channelName) || null

export const connectPrivateChannel = (channelName) => {
  if (!getAuthToken()) return null

  return createEcho()?.private(channelName) || null
}

export const leaveRealtimeChannel = (channelName) => {
  echoInstance?.leave(channelName)
}

export const disconnectRealtime = () => {
  if (!echoInstance) return

  echoInstance.disconnect()
  echoInstance = null
  currentToken = null
  notifyStatusListeners(isRealtimeConfigured() ? 'disconnected' : 'disabled')
}

export const realtimeEnabled = () => isRealtimeConfigured()

export const getRealtimeStatus = () => connectionStatus

export const subscribeRealtimeStatus = (listener) => {
  if (typeof listener !== 'function') {
    return () => {}
  }

  statusListeners.add(listener)
  listener(connectionStatus)

  return () => {
    statusListeners.delete(listener)
  }
}
