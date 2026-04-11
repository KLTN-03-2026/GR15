<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CongTy extends Model
{
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

    public const TRANG_THAI_HOAT_DONG = 1;

    public function nguoiDung()
    {
        return $this->belongsTo(NguoiDung::class, 'nguoi_dung_id');
    }

    public function nganhNghe()
    {
        return $this->belongsTo(NganhNghe::class, 'nganh_nghe_id');
    }

    public function tinTuyenDungs()
    {
        return $this->hasMany(TinTuyenDung::class, 'cong_ty_id');
    }

    public function nguoiDungTheoDois()
    {
        return $this->belongsToMany(NguoiDung::class, 'theo_doi_cong_tys', 'cong_ty_id', 'nguoi_dung_id')
            ->withTimestamps();
    }
}
