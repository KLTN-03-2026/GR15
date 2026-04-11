<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ApiAccessToken extends Model
{
    protected $table = 'api_access_tokens';

    protected $fillable = [
        'nguoi_dung_id',
        'token_hash',
        'last_used_at',
    ];

    protected $casts = [
        'nguoi_dung_id' => 'integer',
        'last_used_at' => 'datetime',
    ];

    public function nguoiDung()
    {
        return $this->belongsTo(NguoiDung::class, 'nguoi_dung_id');
    }
}
