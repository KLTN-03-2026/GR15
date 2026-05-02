export const APPLICATION_STATUS = {
  PENDING: 0,
  REVIEWED: 1,
  INTERVIEW_SCHEDULED: 2,
  INTERVIEW_PASSED: 3,
  HIRED: 4,
  REJECTED: 5,
}

export const FINAL_APPLICATION_STATUSES = [
  APPLICATION_STATUS.HIRED,
  APPLICATION_STATUS.REJECTED,
]

export const OFFER_STATUS = {
  NOT_SENT: 0,
  SENT: 1,
  ACCEPTED: 2,
  DECLINED: 3,
}

export const APPLICATION_STATUS_OPTIONS = [
  { value: APPLICATION_STATUS.PENDING, label: 'Đang chờ' },
  { value: APPLICATION_STATUS.REVIEWED, label: 'Đã xem' },
  { value: APPLICATION_STATUS.INTERVIEW_SCHEDULED, label: 'Đã hẹn phỏng vấn' },
  { value: APPLICATION_STATUS.INTERVIEW_PASSED, label: 'Qua phỏng vấn' },
  { value: APPLICATION_STATUS.HIRED, label: 'Trúng tuyển' },
  { value: APPLICATION_STATUS.REJECTED, label: 'Từ chối' },
]

export const getApplicationStatusMeta = (status) => {
  switch (Number(status)) {
    case APPLICATION_STATUS.REVIEWED:
      return {
        label: 'Đã xem',
        classes: 'bg-sky-500/10 text-sky-600 dark:text-sky-300',
        dot: 'bg-sky-500',
      }
    case APPLICATION_STATUS.INTERVIEW_SCHEDULED:
      return {
        label: 'Đã hẹn phỏng vấn',
        classes: 'bg-violet-500/10 text-violet-700 dark:text-violet-300',
        dot: 'bg-violet-500',
      }
    case APPLICATION_STATUS.INTERVIEW_PASSED:
      return {
        label: 'Qua phỏng vấn',
        classes: 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300',
        dot: 'bg-indigo-500',
      }
    case APPLICATION_STATUS.HIRED:
      return {
        label: 'Trúng tuyển',
        classes: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
        dot: 'bg-emerald-500',
      }
    case APPLICATION_STATUS.REJECTED:
      return {
        label: 'Từ chối',
        classes: 'bg-rose-500/10 text-rose-700 dark:text-rose-300',
        dot: 'bg-rose-500',
      }
    case APPLICATION_STATUS.PENDING:
    default:
      return {
        label: 'Đang chờ',
        classes: 'bg-amber-500/10 text-amber-700 dark:text-amber-300',
        dot: 'bg-amber-500',
      }
  }
}

export const getApplicationStatusLabel = (status) => getApplicationStatusMeta(status).label

export const isFinalApplicationStatus = (status) =>
  FINAL_APPLICATION_STATUSES.includes(Number(status))

export const getOfferStatusMeta = (status) => {
  switch (Number(status)) {
    case OFFER_STATUS.SENT:
      return {
        label: 'Đã gửi offer',
        classes: 'bg-blue-500/10 text-blue-700 dark:text-blue-300',
        dot: 'bg-blue-500',
      }
    case OFFER_STATUS.ACCEPTED:
      return {
        label: 'Đã nhận việc',
        classes: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
        dot: 'bg-emerald-500',
      }
    case OFFER_STATUS.DECLINED:
      return {
        label: 'Từ chối offer',
        classes: 'bg-rose-500/10 text-rose-700 dark:text-rose-300',
        dot: 'bg-rose-500',
      }
    case OFFER_STATUS.NOT_SENT:
    default:
      return {
        label: 'Chưa gửi offer',
        classes: 'bg-slate-500/10 text-slate-600 dark:text-slate-300',
        dot: 'bg-slate-400',
      }
  }
}
