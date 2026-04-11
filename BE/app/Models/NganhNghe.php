<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class NganhNghe extends Model
{
    protected $table = 'nganh_nghes';

    protected $fillable = [
        'ten_nganh',
        'slug',
        'mo_ta',
        'danh_muc_cha_id',
        'icon',
        'trang_thai',
    ];

    protected $casts = [
        'danh_muc_cha_id' => 'integer',
        'trang_thai' => 'integer',
    ];

    public const TRANG_THAI_HIEN_THI = 1;

    public function danhMucCha()
    {
        return $this->belongsTo(self::class, 'danh_muc_cha_id');
    }

    public function danhMucCon()
    {
        return $this->hasMany(self::class, 'danh_muc_cha_id');
    }

    public function tinTuyenDungs()
    {
        return $this->belongsToMany(TinTuyenDung::class, 'chi_tiet_nganh_nghes', 'nganh_nghe_id', 'tin_tuyen_dung_id')
            ->withTimestamps();
    }

    public static function taoSlug(string $tenNganh, ?int $excludeId = null): string
    {
        $slug = Str::slug($tenNganh);
        $baseSlug = $slug;
        $count = 1;

        while (
            static::query()
                ->when($excludeId, fn ($query) => $query->where('id', '!=', $excludeId))
                ->where('slug', $slug)
                ->exists()
        ) {
            $slug = "{$baseSlug}-{$count}";
            $count++;
        }

        return $slug;
    }
}
