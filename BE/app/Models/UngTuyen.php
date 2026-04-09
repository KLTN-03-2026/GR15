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
        'thu_xin_viec',
        'ngay_hen_phong_van',
        'ket_qua_phong_van',
        'ghi_chu',
        'thoi_gian_ung_tuyen'
    ];

    /**
     * Các trạng thái ứng tuyển
     */
    public const TRANG_THAI_CHO_DUYET = 0;
    public const TRANG_THAI_DA_XEM = 1;
    public const TRANG_THAI_CHAP_NHAN = 2;
    public const TRANG_THAI_TU_CHOI = 3;

    public const TRANG_THAI_LIST = [
        self::TRANG_THAI_CHO_DUYET,
        self::TRANG_THAI_DA_XEM,
        self::TRANG_THAI_CHAP_NHAN,
        self::TRANG_THAI_TU_CHOI,
    ];

    protected $casts = [
        'thoi_gian_ung_tuyen' => 'datetime',
        'ngay_hen_phong_van' => 'datetime',
        'trang_thai' => 'integer',
    ];

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
