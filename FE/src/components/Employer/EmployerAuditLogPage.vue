<script setup>
import AuditLogTablePage from '@/components/Audit/AuditLogTablePage.vue'
import { employerAuditLogService } from '@/services/api'
</script>

<template>
  <AuditLogTablePage
    title="Nhật ký công ty"
    description="Theo dõi các thao tác của nội bộ công ty: quản lý HR, tin tuyển dụng, ứng viên, lịch phỏng vấn và các thay đổi có ảnh hưởng tới dữ liệu tuyển dụng."
    :fetch-logs="employerAuditLogService.getLogs"
  />
</template>
