<?php

namespace App\Services;

use App\Events\AppNotificationCreated;
use App\Models\AppNotification;
use App\Models\CongTy;
use App\Models\NguoiDung;
use Illuminate\Support\Collection;

class AppNotificationService
{
    public function createForUser(
        int|NguoiDung|null $recipient,
        string $type,
        string $title,
        string $message,
        ?string $path = null,
        array $metadata = [],
        bool $broadcast = true,
    ): ?AppNotification {
        $recipientId = $recipient instanceof NguoiDung ? $recipient->id : $recipient;

        if (!$recipientId) {
            return null;
        }

        $notification = AppNotification::create([
            'nguoi_dung_id' => (int) $recipientId,
            'loai' => $type,
            'tieu_de' => $title,
            'noi_dung' => $message,
            'duong_dan' => $path,
            'du_lieu_bo_sung' => $metadata ?: null,
        ]);

        if ($broadcast) {
            try {
                broadcast(new AppNotificationCreated($notification));
            } catch (\Throwable $exception) {
                report($exception);
            }
        }

        return $notification;
    }

    /**
     * @param  iterable<int|NguoiDung>  $recipients
     */
    public function createForUsers(
        iterable $recipients,
        string $type,
        string $title,
        string $message,
        ?string $path = null,
        array $metadata = [],
    ): void {
        foreach ($this->normalizeRecipientIds($recipients) as $recipientId) {
            $this->createForUser($recipientId, $type, $title, $message, $path, $metadata);
        }
    }

    public function recruitmentRecipients(CongTy $company, ?int $preferredHrId = null): Collection
    {
        $roleRecipients = $company->thanhViens()
            ->where('nguoi_dungs.trang_thai', 1)
            ->wherePivotIn('vai_tro_noi_bo', [
                CongTy::VAI_TRO_NOI_BO_OWNER,
                CongTy::VAI_TRO_NOI_BO_ADMIN_HR,
                CongTy::VAI_TRO_NOI_BO_RECRUITER,
            ])
            ->pluck('nguoi_dungs.id');

        return collect([
            $company->nguoi_dung_id,
            $preferredHrId,
            ...$roleRecipients->all(),
        ])
            ->filter()
            ->map(fn ($id) => (int) $id)
            ->unique()
            ->values();
    }

    private function normalizeRecipientIds(iterable $recipients): array
    {
        return collect($recipients)
            ->map(fn ($recipient) => $recipient instanceof NguoiDung ? $recipient->id : $recipient)
            ->filter()
            ->map(fn ($id) => (int) $id)
            ->unique()
            ->values()
            ->all();
    }
}
