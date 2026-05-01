import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const read = (path) => readFileSync(resolve(root, path), 'utf8')

const api = read('src/services/api.js')
const router = read('src/router/index.js')
const savedJobsPage = read('src/components/Dashboard/SavedJobsPage.vue')
const aiChatPage = read('src/components/Dashboard/AICenterChatPage.vue')
const applicationsPage = read('src/components/Dashboard/ApplicationsPage.vue')
const notifications = read('src/composables/useNotifications.js')

assert.match(api, /export const reEngagementService/, 'reEngagementService must be exported')
assert.match(api, /\/ung-vien\/re-engagement\/insights/, 're-engagement insights endpoint must be wired')
assert.match(api, /confirmInterviewRoundAttendance/, 'interview round candidate API must be wired')
assert.match(api, /respondOffer/, 'offer response API must be wired')
assert.match(api, /getOnboarding/, 'onboarding API must be wired')
assert.match(api, /downloadExport/, 'server-side application PDF export APIs must be wired')
assert.match(api, /blobApiCall/, 'binary PDF download helper must exist')

assert.match(router, /\/smart-job-alerts/, 'Smart Job Alerts route must exist')
assert.match(router, /\/ai-center/, 'AI Center route must exist')
assert.match(router, /\/saved-jobs/, 'Saved jobs route must exist')

assert.match(savedJobsPage, /fetchReEngagementInsights/, 'SavedJobsPage must fetch re-engagement insights')
assert.match(savedJobsPage, /Nhắc bạn quay lại đúng lúc/, 'SavedJobsPage must render re-engagement panel')
assert.match(aiChatPage, /streamMessage|sendMessage/, 'AI chat page must keep message send flow')
assert.match(applicationsPage, /confirmInterviewRoundAttendance/, 'Applications page must support interview round confirmation')
assert.match(applicationsPage, /respondOffer/, 'Applications page must support offer response')
assert.match(applicationsPage, /focusApplicationDeepLink/, 'Applications page must support focused notification deeplinks')
assert.match(applicationsPage, /downloadApplicationExport/, 'Applications page must expose server-side PDF export')
assert.match(notifications, /focus_section/, 'Notification deeplinks must carry section focus')
assert.match(notifications, /payload\.data/, 'Realtime notifications must preserve metadata for deeplinks')

console.log('Frontend smoke checks passed.')
