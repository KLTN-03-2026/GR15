<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CongTy;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class SemanticSearchController extends Controller
{
    public function searchJobs(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'q' => ['required', 'string', 'min:2'],
            'top_k' => ['nullable', 'integer', 'min:1', 'max:20'],
        ]);

        $query = trim((string) $validated['q']);
        $topK = (int) ($validated['top_k'] ?? 8);
        $keywords = collect(preg_split('/\s+/u', Str::lower($query)))
            ->filter(fn ($item) => mb_strlen($item) >= 2)
            ->values();

        $jobs = TinTuyenDung::query()
            ->with([
                'congTy:id,ten_cong_ty,trang_thai',
                'nganhNghes:id,ten_nganh',
            ])
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->where(function ($subQuery) {
                $subQuery->whereNull('ngay_het_han')
                    ->orWhere('ngay_het_han', '>=', now());
            })
            ->whereHas('congTy', fn ($subQuery) => $subQuery->where('trang_thai', CongTy::TRANG_THAI_HOAT_DONG))
            ->get();

        $results = $jobs
            ->map(function (TinTuyenDung $job) use ($keywords) {
                $title = Str::lower((string) $job->tieu_de);
                $description = Str::lower((string) $job->mo_ta_cong_viec);
                $company = Str::lower((string) $job->congTy?->ten_cong_ty);
                $location = Str::lower((string) $job->dia_diem_lam_viec);
                $industries = Str::lower($job->nganhNghes->pluck('ten_nganh')->implode(' '));

                $titleHits = 0;
                $descriptionHits = 0;
                $categoryHits = 0;
                $locationHits = 0;

                foreach ($keywords as $keyword) {
                    if (str_contains($title, $keyword)) {
                        $titleHits++;
                    }
                    if (str_contains($description, $keyword) || str_contains($company, $keyword)) {
                        $descriptionHits++;
                    }
                    if (str_contains($industries, $keyword)) {
                        $categoryHits++;
                    }
                    if (str_contains($location, $keyword)) {
                        $locationHits++;
                    }
                }

                $keywordCount = max(1, $keywords->count());
                $titleScore = min(1, $titleHits / $keywordCount);
                $keywordScore = min(1, $descriptionHits / $keywordCount);
                $categoryScore = min(1, $categoryHits / $keywordCount);
                $semanticScore = min(1, ($titleScore * 0.45) + ($keywordScore * 0.3) + ($categoryScore * 0.15) + (min(1, $locationHits / $keywordCount) * 0.1));

                return [
                    'semantic_score' => round($semanticScore, 4),
                    'keyword_score' => round($keywordScore, 4),
                    'skill_score' => round($keywordScore * 0.75, 4),
                    'category_score' => round($categoryScore, 4),
                    'title_score' => round($titleScore, 4),
                    'final_score' => round($semanticScore, 4),
                    'semantic_reason' => $titleHits > 0 || $descriptionHits > 0 || $categoryHits > 0
                        ? 'Kết quả được xếp hạng theo mức độ khớp giữa tiêu đề, mô tả, công ty và ngành nghề.'
                        : null,
                    'matched_keywords' => $keywords->filter(fn ($keyword) => str_contains($title, $keyword) || str_contains($description, $keyword) || str_contains($industries, $keyword) || str_contains($location, $keyword))->values()->all(),
                    'job' => $job,
                ];
            })
            ->filter(fn ($item) => $item['final_score'] > 0)
            ->sortByDesc('final_score')
            ->take($topK)
            ->values();

        return response()->json([
            'success' => true,
            'data' => [
                'query' => $query,
                'top_k' => $topK,
                'model_version' => 'local-keyword-v1',
                'search_engine' => 'local-semantic-lite',
                'no_relevant_results' => $results->isEmpty(),
                'message' => $results->isEmpty() ? 'Không tìm thấy job đủ liên quan với mô tả này.' : null,
                'total_documents' => $jobs->count(),
                'results' => $results,
            ],
        ]);
    }
}
