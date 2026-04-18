<?php

namespace App\Notifications;

use App\Models\UngTuyen;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;
use Illuminate\Support\Facades\URL;

class InterviewScheduledNotification extends Notification
{
    use Queueable;

    private const DISPLAY_TIMEZONE = 'Asia/Ho_Chi_Minh';
    private const FRONTEND_FALLBACK = 'http://localhost:5173';

    private function getLockedResponseMessage(UngTuyen $ungTuyen): ?string
    {
        if ($ungTuyen->da_rut_don) {
            return 'Đơn ứng tuyển này đã được rút, vì vậy bạn không thể phản hồi lịch phỏng vấn nữa.';
        }

        return match ((int) $ungTuyen->trang_thai) {
            UngTuyen::TRANG_THAI_QUA_PHONG_VAN => 'Hồ sơ của bạn đã được cập nhật sang trạng thái qua phỏng vấn nên không cần phản hồi lịch phỏng vấn nữa.',
            UngTuyen::TRANG_THAI_TRUNG_TUYEN => 'Hồ sơ của bạn đã chuyển sang trạng thái trúng tuyển nên không thể phản hồi lịch phỏng vấn nữa.',
            UngTuyen::TRANG_THAI_TU_CHOI => 'Hồ sơ của bạn đã có kết quả từ chối nên không thể phản hồi lịch phỏng vấn nữa.',
            default => null,
        };
    }

    public function __construct(
        private readonly UngTuyen $ungTuyen,
        private readonly bool $isRescheduled = false,
    ) {
    }

    public function via(object $notifiable): array
    {
        return ['mail'];
    }

    public function toMail(object $notifiable): MailMessage
    {
        $ungTuyen = $this->ungTuyen;
        $tin = $ungTuyen->tinTuyenDung;
        $congTy = $tin?->congTy;
        $tenViTri = $tin?->tieu_de ?: 'Chưa xác định';
        $tenCongTy = $congTy?->ten_cong_ty ?: 'Chưa xác định';
        $ngayHen = $ungTuyen->ngay_hen_phong_van;
        $hinhThuc = match ((string) ($ungTuyen->hinh_thuc_phong_van ?? '')) {
            'online' => 'Phỏng vấn online',
            'offline' => 'Phỏng vấn trực tiếp',
            'phone' => 'Phỏng vấn qua điện thoại',
            default => null,
        };
        $nguoiPhongVan = trim((string) ($ungTuyen->nguoi_phong_van ?? ''));
        $linkPhongVan = trim((string) ($ungTuyen->link_phong_van ?? ''));
        $thoiGian = $ngayHen
            ? $ngayHen->timezone(self::DISPLAY_TIMEZONE)->format('H:i d/m/Y')
            : 'Chưa xác định';
        $subject = $this->isRescheduled
            ? "Cap nhat lich phong van - {$tenViTri} tai {$tenCongTy}"
            : "Thu moi phong van - {$tenViTri} tai {$tenCongTy}";
        $previewText = $this->isRescheduled
            ? 'Nha tuyen dung vua cap nhat lich phong van cua ban.'
            : 'Nha tuyen dung vua dat lich phong van cho ho so ung tuyen cua ban.';
        $candidateId = (int) ($ungTuyen->hoSo?->nguoiDung?->id ?? $notifiable->id ?? 0);
        $acceptUrl = null;
        $declineUrl = null;
        $lockedResponseMessage = $this->getLockedResponseMessage($ungTuyen);
        $canRespondFromEmail = !$lockedResponseMessage && in_array(
            (int) ($ungTuyen->trang_thai_tham_gia_phong_van ?? UngTuyen::PHONG_VAN_CHO_XAC_NHAN),
            [UngTuyen::PHONG_VAN_CHO_XAC_NHAN],
            true,
        );

        if ($canRespondFromEmail && $candidateId > 0 && $ngayHen && $ngayHen->isFuture()) {
            $expiresAt = $ngayHen->copy()->timezone('UTC')->subHours(1);

            if ($expiresAt->isPast()) {
                $expiresAt = now('UTC')->addDays(2);
            }

            $acceptUrl = URL::temporarySignedRoute(
                'ung-vien.ung-tuyens.confirm-interview-email',
                $expiresAt,
                [
                    'id' => $ungTuyen->id,
                    'action' => 'accept',
                    'user' => $candidateId,
                ],
            );

            $declineUrl = URL::temporarySignedRoute(
                'ung-vien.ung-tuyens.confirm-interview-email',
                $expiresAt,
                [
                    'id' => $ungTuyen->id,
                    'action' => 'decline',
                    'user' => $candidateId,
                ],
            );
        }

        return (new MailMessage)
            ->subject($subject)
            ->view('emails.interview-scheduled', [
                'subjectText' => $subject,
                'previewText' => $previewText,
                'isRescheduled' => $this->isRescheduled,
                'candidateName' => $notifiable->ho_ten ?: 'bạn',
                'jobTitle' => $tenViTri,
                'companyName' => $tenCongTy,
                'interviewTime' => $thoiGian,
                'interviewMode' => $hinhThuc,
                'interviewerName' => $nguoiPhongVan,
                'locationOrLink' => $linkPhongVan,
                'canRespondFromEmail' => $canRespondFromEmail,
                'attendanceStatus' => (int) ($ungTuyen->trang_thai_tham_gia_phong_van ?? UngTuyen::PHONG_VAN_CHO_XAC_NHAN),
                'lockedResponseMessage' => $lockedResponseMessage,
                'acceptUrl' => $acceptUrl,
                'declineUrl' => $declineUrl,
                'actionUrl' => rtrim((string) env('FRONTEND_URL', self::FRONTEND_FALLBACK), '/') . '/applications',
            ]);
    }
}
