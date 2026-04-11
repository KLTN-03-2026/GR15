<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class KyNang extends Model
{
    protected $table = 'ky_nangs';

    protected $fillable = [
        'ten_ky_nang',
        'mo_ta',
        'icon',
    ];
}
