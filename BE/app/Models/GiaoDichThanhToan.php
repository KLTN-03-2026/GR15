<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Carbon;

class GiaoDichThanhToan extends Model
{
    use HasFactory;

    protected $table = 'giao_dich_thanh_toans';

    // ── Hằng số Gateway ──────────────────────────────────────────────────────
    const GATEWAY_MOMO   = 'momo';
    const GATEWAY_VNPAY  = 'vnpay';
    const GATEWAY_WALLET = 'wallet';

    // ── Hằng số Loại giao dịch ───────────────────────────────────────────────
    const LOAI_NAP_VI    = 'topup_wallet';
    const LOAI_MUA_GOI   = 'buy_subscription';

    // ── Hằng số Trạng thái ───────────────────────────────────────────────────
    const TRANG_THAI_PENDING    = 'pending';
    const TRANG_THAI_THANH_CONG = 'thanh_cong';
    const TRANG_THAI_THAT_BAI   = 'that_bai';
    const TRANG_THAI_HUY        = 'huy';

    // ── Thời gian hết hạn link thanh toán theo gateway (phút) ────────────────
    const PAYMENT_LINK_TTL = [
        self::GATEWAY_MOMO  => 15,
        self::GATEWAY_VNPAY => 15,
    ];

    protected $fillable = [
        'nguoi_dung_id',
        'vi_nguoi_dung_id',
        'goi_dich_vu_id',
        'gateway',
        'ma_giao_dich_noi_bo',
        'ma_giao_dich_gateway',
        'loai_giao_dich',
        'so_tien',
        'noi_dung',
        'redirect_url',
        'trang_thai',
        'paid_at',
    ];

    protected $casts = [
        'so_tien' => 'integer',
        'paid_at' => 'datetime',
    ];

    protected $appends = [
        'payment_link_expires_at',
        'is_payment_link_expired',
    ];

    // ── Accessors ─────────────────────────────────────────────────────────────

    /**
     * Thời điểm hết hạn link thanh toán (dựa vào gateway config)
     */
    public function getPaymentLinkExpiresAtAttribute(): ?string
    {
        $ttl = self::PAYMENT_LINK_TTL[$this->gateway] ?? null;

        if ($ttl === null || $this->trang_thai !== self::TRANG_THAI_PENDING) {
            return null;
        }

        return $this->created_at->addMinutes($ttl)->toIso8601String();
    }

    /**
     * Link thanh toán đã hết hạn chưa
     */
    public function getIsPaymentLinkExpiredAttribute(): bool
    {
        $ttl = self::PAYMENT_LINK_TTL[$this->gateway] ?? null;

        if ($ttl === null) {
            return false; // gateway = wallet không có TTL
        }

        return Carbon::now()->isAfter($this->created_at->addMinutes($ttl));
    }

    // ── Relationships ─────────────────────────────────────────────────────────

    public function nguoiDung(): BelongsTo
    {
        return $this->belongsTo(NguoiDung::class, 'nguoi_dung_id');
    }

    public function viNguoiDung(): BelongsTo
    {
        return $this->belongsTo(ViNguoiDung::class, 'vi_nguoi_dung_id');
    }

    public function goiDichVu(): BelongsTo
    {
        return $this->belongsTo(GoiDichVu::class, 'goi_dich_vu_id');
    }
}
