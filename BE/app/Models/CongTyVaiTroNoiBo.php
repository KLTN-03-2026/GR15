<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CongTyVaiTroNoiBo extends Model
{
    use HasFactory;

    protected $table = 'cong_ty_vai_tro_noi_bos';

    protected $fillable = [
        'cong_ty_id',
        'ma_vai_tro',
        'ten_vai_tro',
        'mo_ta',
        'vai_tro_goc',
        'duoc_tao_boi',
    ];

    protected $casts = [
        'cong_ty_id' => 'integer',
        'duoc_tao_boi' => 'integer',
    ];

    public function congTy()
    {
        return $this->belongsTo(CongTy::class, 'cong_ty_id');
    }

    public function nguoiTao()
    {
        return $this->belongsTo(NguoiDung::class, 'duoc_tao_boi');
    }
}
