<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UngTuyen extends Model
{
    use HasFactory;

    protected $table = 'ung_tuyens';

    protected $fillable = [
        'tin_tuyen_dung_id',
        'ho_so_id',
        'trang_thai',
        'da_rut_don',
        'thoi_gian_rut_don',
        'thu_xin_viec',
        'thu_xin_viec_ai',
        'ngay_hen_phong_van',
        'vong_phong_van_hien_tai',
        'trang_thai_tham_gia_phong_van',
        'thoi_gian_phan_hoi_phong_van',
        'thoi_gian_gui_nhac_lich',
        'hinh_thuc_phong_van',
        'nguoi_phong_van',
        'link_phong_van',
        'ket_qua_phong_van',
        'rubric_danh_gia_phong_van',
        'thoi_gian_gui_offer',
        'thoi_gian_phan_hoi_offer',
        'ghi_chu_offer',
        'link_offer',
        'ghi_chu',
        'lich_su_xu_ly',
        'thoi_gian_ung_tuyen'
    ];

    /**
     * Các trạng thái ứng tuyển
     */
    public const TRANG_THAI_CHO_DUYET = 0;
    public const TRANG_THAI_DA_XEM = 1;
    public const TRANG_THAI_DA_HEN_PHONG_VAN = 2;
    public const TRANG_THAI_QUA_PHONG_VAN = 3;
    public const TRANG_THAI_TRUNG_TUYEN = 4;
    public const TRANG_THAI_TU_CHOI = 5;
    public const TRANG_THAI_DA_GUI_OFFER = 6;
    public const TRANG_THAI_DA_NHAN_VIEC = 7;
    public const TRANG_THAI_TU_CHOI_OFFER = 8;

    // Alias tương thích ngược với các chỗ đang dùng tên cũ.
    public const TRANG_THAI_CHAP_NHAN = self::TRANG_THAI_TRUNG_TUYEN;

    public const TRANG_THAI_LIST = [
        self::TRANG_THAI_CHO_DUYET,
        self::TRANG_THAI_DA_XEM,
        self::TRANG_THAI_DA_HEN_PHONG_VAN,
        self::TRANG_THAI_QUA_PHONG_VAN,
        self::TRANG_THAI_TRUNG_TUYEN,
        self::TRANG_THAI_TU_CHOI,
        self::TRANG_THAI_DA_GUI_OFFER,
        self::TRANG_THAI_DA_NHAN_VIEC,
        self::TRANG_THAI_TU_CHOI_OFFER,
    ];

    public const TRANG_THAI_CUOI = [
        self::TRANG_THAI_TU_CHOI,
        self::TRANG_THAI_DA_NHAN_VIEC,
        self::TRANG_THAI_TU_CHOI_OFFER,
    ];

    public const VONG_PHONG_VAN_HR = 'hr';
    public const VONG_PHONG_VAN_TECHNICAL = 'technical';
    public const VONG_PHONG_VAN_FINAL = 'final';

    public const VONG_PHONG_VAN_LIST = [
        self::VONG_PHONG_VAN_HR,
        self::VONG_PHONG_VAN_TECHNICAL,
        self::VONG_PHONG_VAN_FINAL,
    ];

    public const PHONG_VAN_CHO_XAC_NHAN = 0;
    public const PHONG_VAN_DA_XAC_NHAN = 1;
    public const PHONG_VAN_KHONG_THAM_GIA = 2;

    public const PHONG_VAN_TRANG_THAI_LIST = [
        self::PHONG_VAN_CHO_XAC_NHAN,
        self::PHONG_VAN_DA_XAC_NHAN,
        self::PHONG_VAN_KHONG_THAM_GIA,
    ];

    protected $casts = [
        'thoi_gian_ung_tuyen' => 'datetime',
        'thoi_gian_rut_don' => 'datetime',
        'ngay_hen_phong_van' => 'datetime',
        'thoi_gian_phan_hoi_phong_van' => 'datetime',
        'thoi_gian_gui_nhac_lich' => 'datetime',
        'thoi_gian_gui_offer' => 'datetime',
        'thoi_gian_phan_hoi_offer' => 'datetime',
        'trang_thai' => 'integer',
        'da_rut_don' => 'boolean',
        'trang_thai_tham_gia_phong_van' => 'integer',
        'lich_su_xu_ly' => 'array',
    ];

    public static function getTrangThaiLabel(int|string|null $status): string
    {
        return match ((int) $status) {
            self::TRANG_THAI_DA_XEM => 'Đã xem',
            self::TRANG_THAI_DA_HEN_PHONG_VAN => 'Đã hẹn phỏng vấn',
            self::TRANG_THAI_QUA_PHONG_VAN => 'Qua phỏng vấn',
            self::TRANG_THAI_TRUNG_TUYEN => 'Trúng tuyển',
            self::TRANG_THAI_TU_CHOI => 'Từ chối',
            self::TRANG_THAI_DA_GUI_OFFER => 'Đã gửi offer',
            self::TRANG_THAI_DA_NHAN_VIEC => 'Đã nhận việc',
            self::TRANG_THAI_TU_CHOI_OFFER => 'Từ chối offer',
            default => 'Đang chờ',
        };
    }

    public static function getVongPhongVanLabel(?string $round): string
    {
        return match ((string) $round) {
            self::VONG_PHONG_VAN_HR => 'Vòng HR',
            self::VONG_PHONG_VAN_TECHNICAL => 'Vòng Technical',
            self::VONG_PHONG_VAN_FINAL => 'Vòng Final',
            default => 'Chưa xác định',
        };
    }

    public function appendHistory(array $entry): void
    {
        $history = collect($this->lich_su_xu_ly ?? [])
            ->push(array_merge([
                'at' => now('UTC')->toISOString(),
            ], $entry))
            ->values()
            ->all();

        $this->lich_su_xu_ly = $history;
    }

    /**
     * Tin tuyển dụng mà hồ sơ nộp vào.
     */
    public function tinTuyenDung()
    {
        return $this->belongsTo(TinTuyenDung::class, 'tin_tuyen_dung_id');
    }

    /**
     * Hồ sơ được nộp.
     */
    public function hoSo()
    {
        return $this->belongsTo(HoSo::class, 'ho_so_id')->withTrashed(); // Lấy cả hồ sơ bị xoá mềm để lưu vết
    }
}
