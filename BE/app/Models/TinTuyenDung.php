<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class TinTuyenDung extends Model
{
    use HasFactory;

    protected $table = 'tin_tuyen_dungs';

    protected $fillable = [
        'tieu_de',
        'mo_ta_cong_viec',
        'dia_diem_lam_viec',
        'hinh_thuc_lam_viec',
        'cap_bac',
        'so_luong_tuyen',
        'muc_luong',
        'kinh_nghiem_yeu_cau',
        'ngay_het_han',
        'luot_xem',
        'cong_ty_id',
        'trang_thai',
    ];

    protected $casts = [
        'so_luong_tuyen' => 'integer',
        'muc_luong' => 'integer',
        'luot_xem' => 'integer',
        'cong_ty_id' => 'integer',
        'trang_thai' => 'integer',
        'ngay_het_han' => 'date',
    ];

    const TRANG_THAI_HOAT_DONG = 1;
    const TRANG_THAI_TAM_NGUNG = 0;

    const HINH_THUC_LIST = [
        'Toàn thời gian',
        'Bán thời gian',
        'Thực tập',
        'Remote',
        'Freelance'
    ];

    /**
     * Thuộc về 1 công ty
     */
    public function congTy()
    {
        return $this->belongsTo(CongTy::class, 'cong_ty_id');
    }

    /**
     * Một tin tuyển dụng có thể thuộc nhiều ngành nghề
     */
    public function nganhNghes()
    {
        return $this->belongsToMany(NganhNghe::class, 'chi_tiet_nganh_nghes', 'tin_tuyen_dung_id', 'nganh_nghe_id')
            ->withTimestamps();
    }

    /**
     * Danh sách người dùng đã lưu tin này.
     */
    public function nguoiDungLuus()
    {
        return $this->belongsToMany(NguoiDung::class, 'luu_tins', 'tin_tuyen_dung_id', 'nguoi_dung_id')
            ->withTimestamps();
    }

    /**
     * Danh sách đơn ứng tuyển vào tin này.
     */
    public function ungTuyens()
    {
        return $this->hasMany(\App\Models\UngTuyen::class, 'tin_tuyen_dung_id');
    }
}
