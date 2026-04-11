<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class HoSo extends Model
{
    use SoftDeletes;

    protected $table = 'ho_sos';

    protected $fillable = [
        'nguoi_dung_id',
        'tieu_de_ho_so',
        'muc_tieu_nghe_nghiep',
        'trinh_do',
        'kinh_nghiem_nam',
        'mo_ta_ban_than',
        'file_cv',
        'trang_thai',
    ];

    protected $casts = [
        'nguoi_dung_id' => 'integer',
        'kinh_nghiem_nam' => 'integer',
        'trang_thai' => 'integer',
    ];

    public function nguoiDung()
    {
        return $this->belongsTo(NguoiDung::class, 'nguoi_dung_id');
    }

    public function parsing()
    {
        return $this->hasOne(HoSoParsing::class, 'ho_so_id');
    }

    public function ungTuyens()
    {
        return $this->hasMany(UngTuyen::class, 'ho_so_id');
    }

    public function ketQuaMatchings()
    {
        return $this->hasMany(KetQuaMatching::class, 'ho_so_id');
    }

    public function tuVanNgheNghieps()
    {
        return $this->hasMany(TuVanNgheNghiep::class, 'ho_so_id');
    }
}
