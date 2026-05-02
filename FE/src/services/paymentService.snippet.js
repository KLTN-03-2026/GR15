export const paymentService = {
  getPayments: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.loai_giao_dich) params.append('loai_giao_dich', options.loai_giao_dich)
    if (options.trang_thai) params.append('trang_thai', options.trang_thai)

    const query = params.toString()
    return apiCall(`/ung-vien/payments${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getPaymentDetail: (maGiaoDichNoiBo) =>
    apiCall(`/ung-vien/payments/${maGiaoDichNoiBo}`, {
      method: 'GET',
    }),
}
