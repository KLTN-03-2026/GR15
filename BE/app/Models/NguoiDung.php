<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;

class NguoiDung extends Authenticatable
{
    protected $table = 'nguoi_dungs';

    protected $fillable = [
        'ho_ten',
        'email',
        'mat_khau',
        'so_dien_thoai',
        'email_verified_at',
        'ngay_sinh',
        'gioi_tinh',
        'dia_chi',
        'anh_dai_dien',
        'vai_tro',
        'trang_thai',
    ];

    protected $hidden = [
        'mat_khau',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'ngay_sinh' => 'date',
        'mat_khau' => 'hashed',
        'vai_tro' => 'integer',
        'trang_thai' => 'integer',
    ];

    public const VAI_TRO_UNG_VIEN = 0;
    public const VAI_TRO_NHA_TUYEN_DUNG = 1;
    public const VAI_TRO_ADMIN = 2;

    public function isUngVien(): bool
    {
        return $this->vai_tro === self::VAI_TRO_UNG_VIEN;
    }

    public function isNhaTuyenDung(): bool
    {
        return $this->vai_tro === self::VAI_TRO_NHA_TUYEN_DUNG;
    }

    public function isAdmin(): bool
    {
        return $this->vai_tro === self::VAI_TRO_ADMIN;
    }

    public function isActive(): bool
    {
        return (int) $this->trang_thai === 1;
    }

    public function getTenVaiTroAttribute(): string
    {
        return match ((int) $this->vai_tro) {
            self::VAI_TRO_ADMIN => 'Admin',
            self::VAI_TRO_NHA_TUYEN_DUNG => 'Nhà tuyển dụng',
            default => 'Ứng viên',
        };
    }

    public function hoSos()
    {
        return $this->hasMany(HoSo::class, 'nguoi_dung_id');
    }

    public function nguoiDungKyNangs()
    {
        return $this->hasMany(NguoiDungKyNang::class, 'nguoi_dung_id');
    }

    public function tinDaLuus()
    {
        return $this->belongsToMany(TinTuyenDung::class, 'luu_tins', 'nguoi_dung_id', 'tin_tuyen_dung_id')
            ->withTimestamps();
    }

    public function congTy()
    {
        return $this->hasOne(CongTy::class, 'nguoi_dung_id');
    }

    public function congTyTheoDois()
    {
        return $this->belongsToMany(CongTy::class, 'theo_doi_cong_tys', 'nguoi_dung_id', 'cong_ty_id')
            ->withTimestamps();
    }

    public function apiTokens()
    {
        return $this->hasMany(ApiAccessToken::class, 'nguoi_dung_id');
    }

    public function getAuthPassword(): string
    {
        return $this->mat_khau;
    }
}
