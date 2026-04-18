<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\MarketStatsDaily;
use App\Models\TinTuyenDung;
use App\Models\UngTuyen;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

class AdminMarketDashboardController extends Controller
{
    public function overview(): JsonResponse
    {
        $overview = $this->buildOverview();
        $latestMarketSnapshot = $this->getLatestMarketSnapshot();

        return response()->json([
            'success' => true,
            'data' => [
                'overview' => $overview,
                'top_categories' => $this->buildTopCategories($latestMarketSnapshot),
                'top_skills' => $this->buildTopSkills(),
                'work_modes' => $this->buildGroupedDistribution('hinh_thuc_lam_viec'),
                'seniority_levels' => $this->buildGroupedDistribution('cap_bac'),
                'salary_ranges' => $this->buildSalaryRanges(),
                'monthly_job_trend' => $this->buildMonthlyJobTrend(),
                'insights' => $this->buildInsights($overview, $latestMarketSnapshot),
                'data_source' => $latestMarketSnapshot->isNotEmpty() ? 'market_stats_daily + live_jobs' : 'live_jobs',
            ],
        ]);
    }

    private function buildOverview(): array
    {
        $activeJobsQuery = TinTuyenDung::query()->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG);

        $activeJobCount = (clone $activeJobsQuery)->count();
        $applicationCount = UngTuyen::query()->count();
        $averageSalary = (int) round((clone $activeJobsQuery)->whereNotNull('muc_luong')->avg('muc_luong') ?? 0);
        $salaryValues = (clone $activeJobsQuery)
            ->whereNotNull('muc_luong')
            ->orderBy('muc_luong')
            ->pluck('muc_luong')
            ->values();

        return [
            'active_job_count' => $activeJobCount,
            'application_count' => $applicationCount,
            'average_salary' => $averageSalary,
            'median_salary' => $this->calculateMedian($salaryValues),
            'remote_job_count' => (clone $activeJobsQuery)->where('hinh_thuc_lam_viec', 'like', '%Remote%')->count(),
            'company_count' => (clone $activeJobsQuery)->distinct('cong_ty_id')->count('cong_ty_id'),
        ];
    }

    private function getLatestMarketSnapshot(): Collection
    {
        $latestDate = MarketStatsDaily::query()->max('stat_date');

        if (!$latestDate) {
            return collect();
        }

        return MarketStatsDaily::query()
            ->with('nganhNghe:id,ten_nganh')
            ->whereDate('stat_date', $latestDate)
            ->orderByDesc('demand_count')
            ->get();
    }

    private function buildTopCategories(Collection $snapshot): array
    {
        if ($snapshot->isNotEmpty()) {
            return $snapshot
                ->take(5)
                ->map(function (MarketStatsDaily $item) {
                    return [
                        'name' => $item->nganhNghe?->ten_nganh ?? 'Chưa phân loại',
                        'job_count' => $item->demand_count,
                        'average_salary' => $item->avg_salary ?? 0,
                        'top_skills' => collect($item->top_skills ?? [])->take(4)->values()->all(),
                    ];
                })
                ->values()
                ->all();
        }

        return DB::table('chi_tiet_nganh_nghes as ct')
            ->join('nganh_nghes as nn', 'nn.id', '=', 'ct.nganh_nghe_id')
            ->join('tin_tuyen_dungs as ttd', 'ttd.id', '=', 'ct.tin_tuyen_dung_id')
            ->where('ttd.trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->select(
                'nn.ten_nganh as name',
                DB::raw('COUNT(DISTINCT ttd.id) as job_count'),
                DB::raw('ROUND(AVG(ttd.muc_luong)) as average_salary')
            )
            ->groupBy('nn.id', 'nn.ten_nganh')
            ->orderByDesc('job_count')
            ->limit(5)
            ->get()
            ->map(fn ($row) => [
                'name' => $row->name,
                'job_count' => (int) $row->job_count,
                'average_salary' => (int) ($row->average_salary ?? 0),
                'top_skills' => [],
            ])
            ->all();
    }

    private function buildTopSkills(): array
    {
        return DB::table('tin_tuyen_dung_ky_nangs as ttdkn')
            ->join('ky_nangs as kn', 'kn.id', '=', 'ttdkn.ky_nang_id')
            ->join('tin_tuyen_dungs as ttd', 'ttd.id', '=', 'ttdkn.tin_tuyen_dung_id')
            ->where('ttd.trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->select(
                'kn.ten_ky_nang as name',
                DB::raw('COUNT(DISTINCT ttd.id) as job_count'),
                DB::raw('SUM(CASE WHEN ttdkn.bat_buoc = 1 THEN 1 ELSE 0 END) as required_count')
            )
            ->groupBy('kn.id', 'kn.ten_ky_nang')
            ->orderByDesc('job_count')
            ->limit(8)
            ->get()
            ->map(fn ($row) => [
                'name' => $row->name,
                'job_count' => (int) $row->job_count,
                'required_count' => (int) $row->required_count,
            ])
            ->all();
    }

    private function buildGroupedDistribution(string $column): array
    {
        return TinTuyenDung::query()
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->select($column, DB::raw('COUNT(*) as total'))
            ->groupBy($column)
            ->orderByDesc('total')
            ->get()
            ->map(fn ($row) => [
                'label' => $row->{$column} ?: 'Chưa cập nhật',
                'count' => (int) $row->total,
            ])
            ->all();
    }

    private function buildSalaryRanges(): array
    {
        $ranges = [
            ['label' => 'Dưới 10 triệu', 'min' => 0, 'max' => 9999999],
            ['label' => '10 - 20 triệu', 'min' => 10000000, 'max' => 20000000],
            ['label' => '20 - 30 triệu', 'min' => 20000001, 'max' => 30000000],
            ['label' => 'Trên 30 triệu', 'min' => 30000001, 'max' => null],
        ];

        return collect($ranges)->map(function (array $range) {
            $query = TinTuyenDung::query()
                ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
                ->whereNotNull('muc_luong');

            if ($range['min'] !== null) {
                $query->where('muc_luong', '>=', $range['min']);
            }

            if ($range['max'] !== null) {
                $query->where('muc_luong', '<=', $range['max']);
            }

            return [
                'label' => $range['label'],
                'count' => $query->count(),
            ];
        })->all();
    }

    private function buildMonthlyJobTrend(): array
    {
        $months = collect(range(5, 0))->map(function (int $offset) {
            $date = Carbon::now()->startOfMonth()->subMonths($offset);

            return [
                'key' => $date->format('Y-m'),
                'label' => 'Tháng '.$date->format('m'),
            ];
        });

        $counts = TinTuyenDung::query()
            ->select(DB::raw("DATE_FORMAT(created_at, '%Y-%m') as month_key"), DB::raw('COUNT(*) as total'))
            ->where('created_at', '>=', Carbon::now()->startOfMonth()->subMonths(5))
            ->groupBy('month_key')
            ->pluck('total', 'month_key');

        return $months->map(fn (array $month) => [
            'label' => $month['label'],
            'count' => (int) ($counts[$month['key']] ?? 0),
        ])->all();
    }

    private function buildInsights(array $overview, Collection $snapshot): array
    {
        $topCategory = collect($this->buildTopCategories($snapshot))->first();
        $topSkill = collect($this->buildTopSkills())->first();
        $topWorkMode = collect($this->buildGroupedDistribution('hinh_thuc_lam_viec'))->first();

        return array_values(array_filter([
            $topCategory
                ? sprintf('Ngành nổi bật nhất hiện tại là %s với %d tin đang hoạt động.', $topCategory['name'], $topCategory['job_count'])
                : null,
            $topSkill
                ? sprintf('Kỹ năng được yêu cầu nhiều nhất là %s, xuất hiện trong %d tin tuyển dụng.', $topSkill['name'], $topSkill['job_count'])
                : null,
            $topWorkMode
                ? sprintf('Hình thức làm việc phổ biến nhất là %s với %d vị trí.', $topWorkMode['label'], $topWorkMode['count'])
                : null,
            $overview['average_salary'] > 0
                ? sprintf('Mức lương trung bình của các tin đang hoạt động hiện khoảng %s.', $this->formatCurrency($overview['average_salary']))
                : null,
        ]));
    }

    private function calculateMedian(Collection $values): int
    {
        $count = $values->count();

        if ($count === 0) {
            return 0;
        }

        $middle = intdiv($count, 2);

        if ($count % 2 === 1) {
            return (int) $values[$middle];
        }

        return (int) round(($values[$middle - 1] + $values[$middle]) / 2);
    }

    private function formatCurrency(int $amount): string
    {
        return number_format($amount, 0, ',', '.').' VND';
    }
}
