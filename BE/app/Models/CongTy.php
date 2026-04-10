<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class CongTy extends Model
{
    use HasFactory;

    protected $table = 'cong_tys';

    protected $fillable = [
        'nguoi_dung_id',
        'ten_cong_ty',
        'ma_so_thue',
        'mo_ta',
        'dia_chi',
        'dien_thoai',
        'email',
        'website',
        'logo',
        'nganh_nghe_id',
        'quy_mo',
        'trang_thai',
    ];

    protected $casts = [
        'nguoi_dung_id' => 'integer',
        'nganh_nghe_id' => 'integer',
        'trang_thai' => 'integer',
    ];

    // ==========================================
    // CONSTANTS
    // ==========================================
    const TRANG_THAI_HOAT_DONG = 1;
    const TRANG_THAI_TAM_NGUNG = 0;

    const QUY_MO_LIST = [
        '1-10',
        '11-50',
        '51-200',
        '201-500',
        '500+',
    ];

    // ==========================================
    // RELATIONSHIPS
    // ==========================================

    /**
     * NTD sở hữu công ty.
     */
    public function nguoiDung()
    {
        return $this->belongsTo(NguoiDung::class, 'nguoi_dung_id');
    }

    /**
     * Danh sách HR thuộc công ty.
     */
    public function thanhViens()
    {
        return $this->belongsToMany(NguoiDung::class, 'cong_ty_nguoi_dungs', 'cong_ty_id', 'nguoi_dung_id')
            ->withPivot('id', 'vai_tro_noi_bo', 'duoc_tao_boi')
            ->withTimestamps();
    }

    /**
     * Ngành nghề chính.
     */
    public function nganhNghe()
    {
        return $this->belongsTo(NganhNghe::class, 'nganh_nghe_id');
    }

    /**
     * Danh sách tin tuyển dụng của công ty.
     */
    public function tinTuyenDungs()
    {
        return $this->hasMany(\App\Models\TinTuyenDung::class, 'cong_ty_id');
    }

    /**
     * Danh sách ứng viên đang theo dõi công ty.
     */
    public function nguoiDungTheoDois()
    {
        return $this->belongsToMany(NguoiDung::class, 'theo_doi_cong_tys', 'cong_ty_id', 'nguoi_dung_id')
            ->withTimestamps();
    }

    // ==========================================
    // HELPERS
    // ==========================================

    public function isHoatDong(): bool
    {
        return $this->trang_thai === self::TRANG_THAI_HOAT_DONG;
    }
}
