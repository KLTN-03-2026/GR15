<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\NguoiDung;
use App\Models\CongTy;
use App\Models\TinTuyenDung;
use App\Models\NganhNghe;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Carbon\Carbon;

class AdminMarketDashboardController extends Controller
{
    /**
     * GET /api/v1/admin/dashboard/market
     */
    public function overview(Request $request): JsonResponse
    {
        return response()->json([
            'overview' => $this->buildOverview(),
            'top_categories' => $this->buildTopCategories(),
            'monthly_job_trend' => $this->buildMonthlyJobTrend(),
            'hints' => [
                'Doanh nghiệp IT chiếm tỷ trọng lớn trong tháng này.',
                'Kỹ năng lập trình web đang là xu hướng hàng đầu.'
            ]
        ]);
    }

    private function buildOverview(): array
    {
        return [
            'total_users' => NguoiDung::count(),
            'total_companies' => CongTy::count(),
            'active_jobs' => TinTuyenDung::where('trang_thai', 'active')->count()
        ];
    }

    private function buildTopCategories(): array
    {
        // Phân tích Top list ngành nghề
        return NganhNghe::withCount('tinTuyenDungs')
            ->orderByDesc('tin_tuyen_dungs_count')
            ->limit(5)
            ->get()
            ->map(function ($item) {
                return [
                    'name' => $item->ten_nganh,
                    'count' => $item->tin_tuyen_dungs_count
                ];
            })->toArray();
    }

    private function buildMonthlyJobTrend(): array
    {
        $trends = [];
        for ($i = 5; $i >= 0; $i--) {
            $month = Carbon::now()->subMonths($i);
            $trends[] = [
                'month' => $month->format('m/Y'),
                'jobs' => TinTuyenDung::whereMonth('created_at', $month->month)
                                        ->whereYear('created_at', $month->year)
                                        ->count()
            ];
        }
        return $trends;
    }
}
