<script setup>
import AuditLogTablePage from '@/components/Audit/AuditLogTablePage.vue'
import { adminAuditLogService } from '@/services/api'
</script>

<template>
  <AuditLogTablePage
    admin-mode
    title="Nhật ký hệ thống"
    description="Theo dõi các thao tác quan trọng trên toàn hệ thống: admin, nhà tuyển dụng, ứng viên, tin tuyển dụng, CV template và HR nội bộ."
    :fetch-logs="adminAuditLogService.getLogs"
  />
</template>
