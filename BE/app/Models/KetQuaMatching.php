<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class KetQuaMatching extends Model
{
    use HasFactory;

    protected $table = 'ket_qua_matchings';

    protected $fillable = [
        'ho_so_id',
        'tin_tuyen_dung_id',
        'diem_phu_hop',
        'chi_tiet_diem',
        'danh_sach_ky_nang_thieu',
        'model_version',
        'thoi_gian_match'
    ];

    protected $casts = [
        'diem_phu_hop' => 'float',
        'chi_tiet_diem' => 'array',
        'thoi_gian_match' => 'datetime',
    ];

    /**
     * Hồ sơ được AI chấm điểm.
     */
    public function hoSo()
    {
        return $this->belongsTo(HoSo::class, 'ho_so_id')->withTrashed();
    }

    /**
     * Tin tuyển dụng được AI mang ra so khớp với Hồ sơ.
     */
    public function tinTuyenDung()
    {
        return $this->belongsTo(TinTuyenDung::class, 'tin_tuyen_dung_id');
    }
}
