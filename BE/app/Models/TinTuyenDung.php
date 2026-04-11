<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TinTuyenDung extends Model
{
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
        'published_at',
        'reactivated_at',
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
        'published_at' => 'datetime',
        'reactivated_at' => 'datetime',
    ];

    protected $appends = [
        'so_luong_da_nhan',
        'so_luong_con_lai',
        'da_tuyen_du',
    ];

    public const TRANG_THAI_HOAT_DONG = 1;

    public function congTy()
    {
        return $this->belongsTo(CongTy::class, 'cong_ty_id');
    }

    public function nganhNghes()
    {
        return $this->belongsToMany(NganhNghe::class, 'chi_tiet_nganh_nghes', 'tin_tuyen_dung_id', 'nganh_nghe_id')
            ->withTimestamps();
    }

    public function nguoiDungLuus()
    {
        return $this->belongsToMany(NguoiDung::class, 'luu_tins', 'tin_tuyen_dung_id', 'nguoi_dung_id')
            ->withTimestamps();
    }

    public function ungTuyens()
    {
        return $this->hasMany(UngTuyen::class, 'tin_tuyen_dung_id');
    }

    public function acceptedApplications()
    {
        return $this->hasMany(UngTuyen::class, 'tin_tuyen_dung_id')
            ->where('trang_thai', UngTuyen::TRANG_THAI_CHAP_NHAN)
            ->whereNotNull('thoi_gian_ung_tuyen');
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
