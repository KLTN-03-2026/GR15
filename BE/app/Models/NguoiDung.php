<?php

namespace App\Models;

use App\Notifications\ResetPasswordLinkNotification;
use App\Notifications\VerifyEmailLinkNotification;
use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class NguoiDung extends Authenticatable implements MustVerifyEmail
{
    use HasApiTokens, HasFactory, Notifiable;

    /**
     * Tên bảng trong database.
     */
    protected $table = 'nguoi_dungs';

    /**
     * Các trường có thể gán hàng loạt (mass assignment).
     */
    protected $fillable = [
        'ho_ten',
        'email',
        'mat_khau',
        'so_dien_thoai',
        'email_verified_at',
        'ngay_sinh',
        'gioi_tinh',
        'dia_chi',
        'anh_dai_dien',
        'vai_tro',
        'trang_thai',
    ];

    /**
     * Các trường ẩn khi serialize (trả về JSON).
     */
    protected $hidden = [
        'mat_khau',
    ];

    /**
     * Cast kiểu dữ liệu.
     */
    protected $casts = [
        'email_verified_at' => 'datetime',
        'ngay_sinh' => 'date',
        'mat_khau' => 'hashed',
        'vai_tro' => 'integer',
        'trang_thai' => 'integer',
    ];

    // ==========================================
    // CONSTANTS - Vai trò người dùng
    // ==========================================
    const VAI_TRO_UNG_VIEN = 0;
    const VAI_TRO_NHA_TUYEN_DUNG = 1;
    const VAI_TRO_ADMIN = 2;

    // ==========================================
    // HELPER METHODS - Kiểm tra vai trò
    // ==========================================

    public function isAdmin(): bool
    {
        return $this->vai_tro === self::VAI_TRO_ADMIN;
    }

    public function isNhaTuyenDung(): bool
    {
        return $this->vai_tro === self::VAI_TRO_NHA_TUYEN_DUNG;
    }

    public function isUngVien(): bool
    {
        return $this->vai_tro === self::VAI_TRO_UNG_VIEN;
    }

    public function isActive(): bool
    {
        return $this->trang_thai === 1;
    }

    /**
     * Lấy nhãn vai trò dạng text.
     */
    public function getTenVaiTroAttribute(): string
    {
        return match ($this->vai_tro) {
            self::VAI_TRO_ADMIN => 'Admin',
            self::VAI_TRO_NHA_TUYEN_DUNG => 'Nhà tuyển dụng',
            self::VAI_TRO_UNG_VIEN => 'Ứng viên',
            default => 'Không xác định',
        };
    }

    /**
     * Danh sách hồ sơ của người dùng (ứng viên).
     */
    public function hoSos()
    {
        return $this->hasMany(\App\Models\HoSo::class, 'nguoi_dung_id');
    }

    /**
     * Danh sách tin tuyển dụng ứng viên ĐÃ LƯU.
     */
    public function tinDaLuus()
    {
        return $this->belongsToMany(\App\Models\TinTuyenDung::class, 'luu_tins', 'nguoi_dung_id', 'tin_tuyen_dung_id')
            ->withTimestamps();
    }

    /**
     * Công ty của nhà tuyển dụng (mỗi NTD có 1 công ty).
     */
    public function congTy()
    {
        return $this->hasOne(\App\Models\CongTy::class, 'nguoi_dung_id');
    }

    /**
     * Danh sách kỹ năng của người dùng (qua bảng nguoi_dung_ky_nangs).
     */
    public function kyNangs()
    {
        return $this->belongsToMany(\App\Models\KyNang::class, 'nguoi_dung_ky_nangs', 'nguoi_dung_id', 'ky_nang_id')
            ->withPivot('muc_do', 'nam_kinh_nghiem', 'so_chung_chi', 'hinh_anh')
            ->withTimestamps();
    }

    /**
     * Các phiên chat AI của người dùng.
     */
    public function aiChatSessions()
    {
        return $this->hasMany(AiChatSession::class, 'nguoi_dung_id');
    }

    /**
     * Các báo cáo mock interview của người dùng.
     */
    public function aiInterviewReports()
    {
        return $this->hasMany(AiInterviewReport::class, 'nguoi_dung_id');
    }

    /**
     * Các báo cáo tư vấn nghề nghiệp đã sinh cho người dùng.
     */
    public function tuVanNgheNghieps()
    {
        return $this->hasMany(TuVanNgheNghiep::class, 'nguoi_dung_id');
    }

    /**
     * Override tên field password cho Laravel Auth.
     */
    public function getAuthPassword(): string
    {
        return $this->mat_khau;
    }

    public function sendPasswordResetNotification($token): void
    {
        $this->notify(new ResetPasswordLinkNotification($token));
    }

    public function sendEmailVerificationNotification(): void
    {
        $this->notify(new VerifyEmailLinkNotification());
    }
}
