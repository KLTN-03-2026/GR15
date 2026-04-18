<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MarketStatsDaily extends Model
{
    use HasFactory;

    public $timestamps = false;

    protected $table = 'market_stats_daily';

    protected $fillable = [
        'stat_date',
        'nganh_nghe_id',
        'avg_salary',
        'median_salary',
        'demand_count',
        'top_skills',
        'created_at',
    ];

    protected $casts = [
        'stat_date' => 'date',
        'nganh_nghe_id' => 'integer',
        'avg_salary' => 'integer',
        'median_salary' => 'integer',
        'demand_count' => 'integer',
        'top_skills' => 'array',
        'created_at' => 'datetime',
    ];

    public function nganhNghe()
    {
        return $this->belongsTo(NganhNghe::class, 'nganh_nghe_id');
    }
}
