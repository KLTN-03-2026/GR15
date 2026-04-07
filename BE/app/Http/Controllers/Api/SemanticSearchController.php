<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CongTy;
use App\Models\TinTuyenDung;
use App\Models\VectorEmbedding;
use App\Services\Ai\AiClientService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SemanticSearchController extends Controller
{
    public function searchJobs(Request $request, AiClientService $aiClient): JsonResponse
    {
        $validated = $request->validate([
            'q' => ['required', 'string', 'min:2'],
            'top_k' => ['nullable', 'integer', 'min:1', 'max:20'],
        ]);

        $query = (string) $validated['q'];
        $topK = (int) ($validated['top_k'] ?? 10);

        $jobs = TinTuyenDung::with([
                'congTy:id,ten_cong_ty,trang_thai',
                'nganhNghes:id,ten_nganh',
                'parsing:id,tin_tuyen_dung_id,parsed_skills_json,parsed_requirements_json,parsed_benefits_json,parsed_salary_json,parsed_location_json',
                'kyNangYeuCaus.kyNang:id,ten_ky_nang',
            ])
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->where(function ($q) {
                $q->whereNull('ngay_het_han')
                    ->orWhere('ngay_het_han', '>=', now());
            })
            ->whereHas('congTy', function ($q) {
                $q->where('trang_thai', CongTy::TRANG_THAI_HOAT_DONG);
            })
            ->get();

        $documents = $jobs->map(function (TinTuyenDung $job): array {
            $textContent = $this->buildSemanticText($job);

            return [
                'entity_id' => $job->id,
                'title' => $job->tieu_de,
                'text_content' => $textContent,
                'company_name' => $job->congTy?->ten_cong_ty,
                'location' => $job->dia_diem_lam_viec,
                'level' => $job->cap_bac,
                'metadata' => [
                    'nganh_nghes' => $job->nganhNghes->pluck('ten_nganh')->values()->all(),
                    'skills' => $job->kyNangYeuCaus
                        ->pluck('kyNang.ten_ky_nang')
                        ->filter()
                        ->values()
                        ->all(),
                ],
            ];
        })->values()->all();

        $response = $aiClient->semanticSearchJobs($query, $documents, $topK);
        $data = $response['data'] ?? [];

        $this->syncEmbeddings($data['document_embeddings'] ?? []);

        $jobMap = $jobs->keyBy('id');
        $results = collect($data['results'] ?? [])
            ->map(function (array $item) use ($jobMap) {
                $job = $jobMap->get((int) ($item['entity_id'] ?? 0));
                if (!$job) {
                    return null;
                }

                return [
                    'semantic_score' => $item['semantic_score'] ?? 0,
                    'keyword_score' => $item['keyword_score'] ?? 0,
                    'skill_score' => $item['skill_score'] ?? 0,
                    'category_score' => $item['category_score'] ?? 0,
                    'title_score' => $item['title_score'] ?? 0,
                    'final_score' => $item['final_score'] ?? 0,
                    'semantic_reason' => $item['semantic_reason'] ?? null,
                    'matched_keywords' => $item['matched_keywords'] ?? [],
                    'job' => $job,
                ];
            })
            ->filter()
            ->values();

        return response()->json([
            'success' => true,
            'data' => [
                'query' => $query,
                'top_k' => $topK,
                'model_version' => $response['model_version'] ?? null,
                'search_engine' => $data['search_engine'] ?? null,
                'no_relevant_results' => (bool) ($data['no_relevant_results'] ?? false),
                'message' => $data['message'] ?? null,
                'total_documents' => $data['total_documents'] ?? count($documents),
                'results' => $results,
            ],
        ]);
    }

    private function buildSemanticText(TinTuyenDung $job): string
    {
        $parts = [
            $job->tieu_de,
            $job->mo_ta_cong_viec,
            $job->dia_diem_lam_viec,
            $job->hinh_thuc_lam_viec,
            $job->cap_bac,
            $job->kinh_nghiem_yeu_cau,
            $job->trinh_do_yeu_cau,
            $job->congTy?->ten_cong_ty,
        ];

        $parts = array_merge(
            $parts,
            $job->nganhNghes->pluck('ten_nganh')->filter()->values()->all(),
            $job->kyNangYeuCaus->pluck('kyNang.ten_ky_nang')->filter()->values()->all(),
            $this->flattenParsedBlock($job->parsing?->parsed_skills_json),
            $this->flattenParsedBlock($job->parsing?->parsed_requirements_json),
            $this->flattenParsedBlock($job->parsing?->parsed_benefits_json)
        );

        return trim(implode(". ", array_filter(array_map(function ($item) {
            return is_string($item) ? trim($item) : null;
        }, $parts))));
    }

    private function flattenParsedBlock($value): array
    {
        if (!is_array($value)) {
            return [];
        }

        $flat = [];
        foreach ($value as $item) {
            if (is_string($item)) {
                $flat[] = $item;
                continue;
            }

            if (is_array($item)) {
                foreach (['skill_name', 'ten_ky_nang', 'requirement', 'benefit', 'name', 'value'] as $key) {
                    if (!empty($item[$key]) && is_string($item[$key])) {
                        $flat[] = $item[$key];
                        break;
                    }
                }
            }
        }

        return $flat;
    }

    private function syncEmbeddings(array $embeddings): void
    {
        foreach ($embeddings as $item) {
            if (
                empty($item['entity_type']) ||
                empty($item['entity_id']) ||
                !isset($item['chunk_index']) ||
                empty($item['text_content']) ||
                !isset($item['embedding_vector']) ||
                empty($item['model_name'])
            ) {
                continue;
            }

            VectorEmbedding::updateOrCreate(
                [
                    'entity_type' => $item['entity_type'],
                    'entity_id' => (int) $item['entity_id'],
                    'chunk_index' => (int) $item['chunk_index'],
                ],
                [
                    'text_content' => (string) $item['text_content'],
                    'embedding_vector' => $item['embedding_vector'],
                    'model_name' => (string) $item['model_name'],
                    'embedding_hash' => hash('sha256', (string) $item['text_content'] . '|' . (string) $item['model_name']),
                    'metadata_json' => $item['metadata_json'] ?? null,
                ]
            );
        }
    }
}
