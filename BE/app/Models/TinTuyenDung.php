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
        'muc_luong_tu',
        'muc_luong_den',
        'don_vi_luong',
        'kinh_nghiem_yeu_cau',
        'trinh_do_yeu_cau',
        'ngay_het_han',
        'luot_xem',
        'cong_ty_id',
        'trang_thai',
    ];

    protected $casts = [
        'so_luong_tuyen' => 'integer',
        'muc_luong' => 'integer',
        'muc_luong_tu' => 'integer',
        'muc_luong_den' => 'integer',
        'luot_xem' => 'integer',
        'cong_ty_id' => 'integer',
        'trang_thai' => 'integer',
        'ngay_het_han' => 'datetime',
    ];

    protected $appends = [
        'so_luong_da_nhan',
        'so_luong_con_lai',
        'da_tuyen_du',
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

    public function acceptedApplications()
    {
        return $this->hasMany(\App\Models\UngTuyen::class, 'tin_tuyen_dung_id')
            ->where('trang_thai', \App\Models\UngTuyen::TRANG_THAI_CHAP_NHAN)
            ->whereNotNull('thoi_gian_ung_tuyen');
    }

    /**
     * Kết quả parse JD gần nhất của tin tuyển dụng.
     */
    public function parsing()
    {
        return $this->hasOne(TinTuyenDungParsing::class, 'tin_tuyen_dung_id');
    }

    /**
     * Các kỹ năng yêu cầu đã chuẩn hóa cho JD.
     */
    public function kyNangYeuCaus()
    {
        return $this->hasMany(TinTuyenDungKyNang::class, 'tin_tuyen_dung_id');
    }

    /**
     * Các kết quả matching sinh ra cho JD này.
     */
    public function ketQuaMatchings()
    {
        return $this->hasMany(KetQuaMatching::class, 'tin_tuyen_dung_id');
    }

    public function getSoLuongDaNhanAttribute(): int
    {
        return (int) (
            $this->attributes['so_luong_da_nhan']
            ?? $this->attributes['accepted_applications_count']
            ?? ($this->relationLoaded('acceptedApplications') ? $this->acceptedApplications->count() : 0)
        );
    }

    public function getSoLuongConLaiAttribute(): int
    {
        return max(0, (int) $this->so_luong_tuyen - (int) $this->so_luong_da_nhan);
    }

    public function getDaTuyenDuAttribute(): bool
    {
        return $this->so_luong_con_lai <= 0;
    }
}
