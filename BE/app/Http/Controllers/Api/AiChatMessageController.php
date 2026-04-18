<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\AiChatMessage;
use App\Models\AiChatSession;
use App\Models\HoSo;
use App\Models\KetQuaMatching;
use App\Models\TinTuyenDung;
use App\Models\TuVanNgheNghiep;
use App\Services\Ai\AiClientService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Symfony\Component\HttpFoundation\StreamedResponse;

class AiChatMessageController extends Controller
{
    public function store(Request $request, AiClientService $aiClient): JsonResponse
    {
        $validated = $this->validateMessagePayload($request);
        $session = $this->resolveActiveSession($request->user()->id, (int) $validated['session_id']);

        $userMessage = AiChatMessage::create([
            'session_id' => $session->id,
            'role' => 'user',
            'content' => $validated['message'],
            'metadata' => null,
            'created_at' => now(),
        ]);

        $history = $this->buildHistory($session->id);
        $context = $this->buildContext($request->user()->id, $session, (string) $validated['message']);
        $response = $aiClient->careerChat(
            $session->id,
            $validated['message'],
            $history,
            $context,
            (bool) ($validated['force_model'] ?? false)
        );

        $assistantData = $response['data'] ?? [];
        $assistantMessage = AiChatMessage::create([
            'session_id' => $session->id,
            'role' => 'assistant',
            'content' => (string) ($assistantData['answer'] ?? ''),
            'metadata' => [
                'provider' => $assistantData['provider'] ?? null,
                'guardrail_triggered' => $assistantData['guardrail_triggered'] ?? false,
                'model_version' => $response['model_version'] ?? null,
                'intent' => $assistantData['intent'] ?? null,
            ],
            'created_at' => now(),
        ]);
        $this->refreshSessionSummary(
            $session,
            $context,
            (string) $validated['message'],
            $assistantMessage->content,
            $assistantData['intent'] ?? null
        );

        return response()->json([
            'success' => true,
            'data' => [
                'user_message' => $userMessage,
                'assistant_message' => $assistantMessage,
                'model_version' => $response['model_version'] ?? null,
            ],
        ], 201);
    }

    public function stream(Request $request, AiClientService $aiClient): StreamedResponse
    {
        $validated = $this->validateMessagePayload($request);
        $session = $this->resolveActiveSession($request->user()->id, (int) $validated['session_id']);

        $userMessage = AiChatMessage::create([
            'session_id' => $session->id,
            'role' => 'user',
            'content' => $validated['message'],
            'metadata' => null,
            'created_at' => now(),
        ]);

        $history = $this->buildHistory($session->id);
        $context = $this->buildContext($request->user()->id, $session, (string) $validated['message']);
        $userMessagePayload = $userMessage->toArray();

        return response()->stream(function () use (
            $userMessagePayload,
            $session,
            $validated,
            $history,
            $context,
            $aiClient
        ): void {
            $donePayload = null;
            $partialAnswer = '';
            $streamMeta = [];

            try {
                $aiClient->careerChatStream(
                    $session->id,
                    $validated['message'],
                    $history,
                    $context,
                    (bool) ($validated['force_model'] ?? false),
                    function (string $event, array $payload) use (&$donePayload, &$partialAnswer, &$streamMeta, $userMessagePayload): void {
                        if ($event === 'done') {
                            $donePayload = $payload;
                            return;
                        }

                        if ($event === 'meta') {
                            $streamMeta = $payload;
                            $payload['user_message'] = $userMessagePayload;
                        }

                        if ($event === 'chunk' && !empty($payload['content'])) {
                            $partialAnswer .= (string) $payload['content'];
                        }

                        echo $this->sseEvent($event, $payload);
                        @ob_flush();
                        @flush();
                    }
                );
            } catch (\Throwable $e) {
                $donePayload = $this->fallbackToNonStream(
                    $aiClient,
                    $session->id,
                    $validated['message'],
                    $history,
                    $context,
                    (bool) ($validated['force_model'] ?? false)
                );
            }

            if (!is_array($donePayload) || empty($donePayload['answer'])) {
                $fallbackAnswer = $this->normalizeAssistantAnswer($partialAnswer);
                if ($fallbackAnswer !== '') {
                    $donePayload = [
                        'answer' => $fallbackAnswer,
                        'model_version' => $streamMeta['model_version'] ?? null,
                        'provider' => $streamMeta['provider'] ?? null,
                        'guardrail_triggered' => $streamMeta['guardrail_triggered'] ?? false,
                        'intent' => $streamMeta['intent'] ?? null,
                    ];
                } else {
                    $donePayload = $this->fallbackToNonStream(
                        $aiClient,
                        $session->id,
                        $validated['message'],
                        $history,
                        $context,
                        (bool) ($validated['force_model'] ?? false)
                    );
                    if (!is_array($donePayload) || empty($donePayload['answer'])) {
                        $donePayload = $this->buildGracefulStreamFallbackPayload(
                            (string) $validated['message'],
                            $streamMeta
                        );
                    }
                }
            }

            $assistantMessage = AiChatMessage::create([
                'session_id' => $session->id,
                'role' => 'assistant',
                'content' => (string) ($donePayload['answer'] ?? ''),
                'metadata' => [
                    'provider' => $donePayload['provider'] ?? null,
                    'guardrail_triggered' => $donePayload['guardrail_triggered'] ?? false,
                    'model_version' => $donePayload['model_version'] ?? null,
                    'intent' => $donePayload['intent'] ?? null,
                    'stream_mode' => 'provider_sse',
                ],
                'created_at' => now(),
            ]);
            $this->refreshSessionSummary(
                $session,
                $context,
                (string) $validated['message'],
                $assistantMessage->content,
                $donePayload['intent'] ?? null
            );

            echo $this->sseEvent('done', [
                'assistant_message' => $assistantMessage->toArray(),
                'model_version' => $donePayload['model_version'] ?? null,
                'provider' => $donePayload['provider'] ?? null,
                'guardrail_triggered' => $donePayload['guardrail_triggered'] ?? false,
                'intent' => $donePayload['intent'] ?? null,
                'answer' => $assistantMessage->content,
            ]);
            @ob_flush();
            @flush();
        }, 200, [
            'Content-Type' => 'text/event-stream',
            'Cache-Control' => 'no-cache',
            'Connection' => 'keep-alive',
            'X-Accel-Buffering' => 'no',
        ]);
    }

    private function buildContext(int $nguoiDungId, AiChatSession $session, string $message): array
    {
        $baseContext = Cache::store('file')->remember(
            $this->baseContextCacheKey($nguoiDungId, $session),
            now()->addMinutes(5),
            function () use ($nguoiDungId, $session): array {
                $candidateProfile = [];
                $careerReport = null;
                $topMatches = [];
                $relatedJob = null;

                if ($session->related_ho_so_id) {
                    $hoSo = HoSo::query()
                        ->with(['parsing', 'nguoiDung:id,ho_ten'])
                        ->where('id', $session->related_ho_so_id)
                        ->where('nguoi_dung_id', $nguoiDungId)
                        ->first();

                    if ($hoSo) {
                        $candidateProfile = [
                            'ho_ten' => $hoSo->nguoiDung?->ho_ten,
                            'parsed_name' => $hoSo->parsing?->parsed_name,
                            'tieu_de_ho_so' => $hoSo->tieu_de_ho_so,
                            'kinh_nghiem_nam' => $hoSo->kinh_nghiem_nam,
                            'trinh_do' => $hoSo->trinh_do,
                            'parsed_skills' => collect($hoSo->parsing?->parsed_skills_json ?? [])
                                ->map(fn ($item) => is_array($item) ? ($item['skill_name'] ?? null) : $item)
                                ->filter()
                                ->values()
                                ->all(),
                        ];

                        $careerReport = TuVanNgheNghiep::query()
                            ->where('ho_so_id', $hoSo->id)
                            ->latest('created_at')
                            ->first();

                        $topMatches = KetQuaMatching::query()
                            ->with('tinTuyenDung:id,tieu_de')
                            ->where('ho_so_id', $hoSo->id)
                            ->orderByDesc('diem_phu_hop')
                            ->limit(2)
                            ->get()
                            ->map(function (KetQuaMatching $item): array {
                                return [
                                    'job_title' => $item->tinTuyenDung?->tieu_de ?? 'Vị trí phù hợp',
                                    'score' => $item->diem_phu_hop,
                                    'matched_skills' => collect($item->matched_skills_json ?? [])
                                        ->map(fn ($skill) => is_array($skill) ? ($skill['skill_name'] ?? null) : $skill)
                                        ->filter()
                                        ->values()
                                        ->all(),
                                    'missing_skills' => collect($item->missing_skills_json ?? [])
                                        ->map(fn ($skill) => is_array($skill) ? ($skill['skill_name'] ?? null) : $skill)
                                        ->filter()
                                        ->values()
                                        ->all(),
                                    'explanation' => $item->explanation,
                                ];
                            })
                            ->all();
                    }
                }

                if ($session->related_tin_tuyen_dung_id) {
                    $job = TinTuyenDung::query()->with(['parsing', 'kyNangYeuCaus.kyNang:id,ten_ky_nang'])->find($session->related_tin_tuyen_dung_id);
                    if ($job) {
                        $relatedJob = [
                            'title' => $job->tieu_de,
                            'location' => $job->dia_diem_lam_viec,
                            'level' => $job->cap_bac,
                            'skills' => $job->kyNangYeuCaus
                                ->pluck('kyNang.ten_ky_nang')
                                ->filter()
                                ->values()
                                ->all(),
                        ];
                    }
                }

                return [
                    'candidate_profile' => $candidateProfile,
                    'career_report' => $careerReport ? [
                        'nghe_de_xuat' => $careerReport->nghe_de_xuat,
                        'muc_do_phu_hop' => $careerReport->muc_do_phu_hop,
                        'goi_y_ky_nang_bo_sung' => $careerReport->goi_y_ky_nang_bo_sung,
                        'bao_cao_chi_tiet' => $careerReport->bao_cao_chi_tiet,
                    ] : null,
                    'top_matching_jobs' => $topMatches,
                    'related_job' => $relatedJob,
                ];
            }
        );

        $candidateProfile = $baseContext['candidate_profile'] ?? [];
        $careerReport = $baseContext['career_report'] ?? null;
        $topMatches = $baseContext['top_matching_jobs'] ?? [];
        $relatedJob = $baseContext['related_job'] ?? null;
        $semanticJobs = [];
        $semanticQuery = $this->buildSemanticQuery($candidateProfile, $careerReport, $relatedJob, $message);
        if ($semanticQuery !== null) {
            $semanticJobs = $this->safeSemanticSearch($semanticQuery);
        }

        return [
            'candidate_profile' => $candidateProfile,
            'career_report' => $careerReport,
            'top_matching_jobs' => $topMatches,
            'related_job' => $relatedJob,
            'semantic_jobs' => $semanticJobs,
            'conversation_summary' => $session->summary,
        ];
    }

    private function validateMessagePayload(Request $request): array
    {
        return $request->validate([
            'session_id' => ['required', 'integer'],
            'message' => ['required', 'string', 'min:2'],
            'force_model' => ['nullable', 'boolean'],
        ]);
    }

    private function resolveActiveSession(int $nguoiDungId, int $sessionId): AiChatSession
    {
        return AiChatSession::query()
            ->where('id', $sessionId)
            ->where('nguoi_dung_id', $nguoiDungId)
            ->where('session_type', 'career_consultant')
            ->where('status', 1)
            ->firstOrFail();
    }

    private function buildHistory(int $sessionId): array
    {
        return AiChatMessage::query()
            ->where('session_id', $sessionId)
            ->orderByDesc('created_at')
            ->limit(4)
            ->get()
            ->reverse()
            ->values()
            ->map(fn (AiChatMessage $item) => [
                'role' => $item->role,
                'content' => $item->content,
                'intent' => $item->metadata['intent'] ?? null,
            ])
            ->all();
    }

    public function index(Request $request, int $sessionId): JsonResponse
    {
        $session = $this->resolveActiveSession($request->user()->id, $sessionId);

        $messages = AiChatMessage::query()
            ->where('session_id', $session->id)
            ->orderBy('created_at', 'asc')
            ->orderBy('id', 'asc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $messages,
        ]);
    }

    private function buildSemanticQuery(array $candidateProfile, ?array $careerReport, ?array $relatedJob, string $message): ?string
    {
        if (!$this->shouldUseSemanticSearch($message)) {
            return null;
        }

        $parts = [];

        foreach ($this->extractSemanticTerms($message) as $term) {
            $parts[] = $term;
        }

        if (!empty($candidateProfile['parsed_skills'])) {
            $parts = array_merge($parts, array_slice($candidateProfile['parsed_skills'], 0, 4));
        }

        if (!empty($careerReport['nghe_de_xuat'])) {
            $parts[] = (string) $careerReport['nghe_de_xuat'];
        }

        if (!empty($relatedJob['title'])) {
            $parts[] = (string) $relatedJob['title'];
        }

        $parts = array_values(array_unique(array_filter(array_map(function ($item) {
            return is_string($item) ? trim($item) : null;
        }, $parts))));

        if (count($parts) < 2) {
            return null;
        }

        return implode(' ', array_slice($parts, 0, 6));
    }

    private function extractSemanticTerms(string $message): array
    {
        $normalized = mb_strtolower($message);
        $normalized = preg_replace('/[^\p{L}\p{N}\s]+/u', ' ', $normalized) ?? '';
        $tokens = preg_split('/\s+/u', trim($normalized)) ?: [];

        $stopWords = [
            'toi', 'tôi', 'la', 'là', 'co', 'có', 'gi', 'gì', 'nao', 'nào', 'trong',
            'he', 'hệ', 'thong', 'thống', 'hien', 'hiện', 'tai', 'tại', 'cho', 'de',
            'để', 'voi', 'với', 'nhat', 'nhất', 'ngay', 'tu', 'từ', 'ho', 'so', 'hồ',
            'cua', 'của', 'ban', 'bạn', 'toi', 'tôi', 'nen', 'nên', 'lam', 'làm',
            'truoc', 'trước', 'tuan', 'tuần', 'nay', 'này',
        ];

        return array_values(array_unique(array_filter($tokens, function ($token) use ($stopWords) {
            return mb_strlen($token) >= 3 && !in_array($token, $stopWords, true);
        })));
    }

    private function shouldUseSemanticSearch(string $message): bool
    {
        $normalized = mb_strtolower($message);
        foreach ([
            'job nào',
            'job nao',
            'công việc',
            'cong viec',
            'ứng tuyển',
            'ung tuyen',
            'vị trí',
            'vi tri',
            'gợi ý job',
            'goi y job',
        ] as $keyword) {
            if (str_contains($normalized, $keyword)) {
                return true;
            }
        }

        return false;
    }

    private function safeSemanticSearch(string $query): array
    {
        try {
            return Cache::store('file')->remember(
                'ai-chat-semantic:' . md5($query),
                now()->addMinutes(5),
                function () use ($query): array {
                    $jobs = TinTuyenDung::query()
                        ->with([
                            'congTy:id,ten_cong_ty,trang_thai',
                            'nganhNghes:id,ten_nganh',
                            'parsing:id,tin_tuyen_dung_id,parsed_skills_json,parsed_requirements_json,parsed_benefits_json',
                            'kyNangYeuCaus.kyNang:id,ten_ky_nang',
                        ])
                        ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
                        ->where(function ($q) {
                            $q->whereNull('ngay_het_han')
                                ->orWhere('ngay_het_han', '>=', now());
                        })
                        ->limit(6)
                        ->get();

                    if ($jobs->isEmpty()) {
                        return [];
                    }

                    $documents = $jobs->map(function (TinTuyenDung $job): array {
                        return [
                            'entity_id' => $job->id,
                            'title' => $job->tieu_de,
                            'text_content' => $this->buildSemanticText($job),
                            'company_name' => $job->congTy?->ten_cong_ty,
                            'location' => $job->dia_diem_lam_viec,
                            'level' => $job->cap_bac,
                            'metadata' => [
                                'nganh_nghes' => $job->nganhNghes->pluck('ten_nganh')->values()->all(),
                                'skills' => $job->kyNangYeuCaus->pluck('kyNang.ten_ky_nang')->filter()->values()->all(),
                            ],
                        ];
                    })->values()->all();

                    $response = app(AiClientService::class)->semanticSearchJobs($query, $documents, 2);
                    $results = $response['data']['results'] ?? [];

                    return collect($results)->map(function (array $item): array {
                        $job = $item['job'] ?? [];

                        return [
                            'title' => $job['tieu_de'] ?? null,
                            'company_name' => $job['cong_ty']['ten_cong_ty'] ?? null,
                            'final_score' => $item['final_score'] ?? null,
                            'semantic_reason' => $item['semantic_reason'] ?? null,
                        ];
                    })->filter(fn (array $item) => !empty($item['title']))->values()->all();
                }
            );
        } catch (\Throwable $e) {
            return [];
        }
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

        return trim(implode('. ', array_filter(array_map(function ($item) {
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

    private function sseEvent(string $event, array $payload): string
    {
        return "event: {$event}\n" .
            'data: ' . json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n\n";
    }

    private function normalizeAssistantAnswer(string $text): string
    {
        $cleaned = trim(str_replace(['**', '__', '`', '#'], '', $text));
        $lines = preg_split('/\R/u', $cleaned) ?: [];
        $normalizedLines = [];
        $previousBlank = false;

        foreach ($lines as $rawLine) {
            $line = preg_replace('/[ \t]+/u', ' ', trim($rawLine)) ?? '';
            if ($line === '') {
                if (!$previousBlank && !empty($normalizedLines)) {
                    $normalizedLines[] = '';
                }
                $previousBlank = true;
                continue;
            }

            $normalizedLines[] = $line;
            $previousBlank = false;
        }

        $cleaned = trim(implode("\n", $normalizedLines));

        if ($cleaned === '') {
            return '';
        }

        if (preg_match('/[.!?]$/u', $cleaned)) {
            return $cleaned;
        }

        $lastStop = max(
            strrpos($cleaned, '.'),
            strrpos($cleaned, '!'),
            strrpos($cleaned, '?')
        );

        if ($lastStop !== false && $lastStop >= (int) (strlen($cleaned) * 0.6)) {
            return trim(substr($cleaned, 0, $lastStop + 1));
        }

        return $cleaned . '.';
    }

    private function fallbackToNonStream(
        AiClientService $aiClient,
        int $sessionId,
        string $message,
        array $history,
        array $context,
        bool $forceModel
    ): ?array {
        try {
            $response = $aiClient->careerChat($sessionId, $message, $history, $context, $forceModel);
            $data = $response['data'] ?? [];
            $answer = $this->normalizeAssistantAnswer((string) ($data['answer'] ?? ''));

            if ($answer === '') {
                return null;
            }

            return [
                'answer' => $answer,
                'model_version' => $response['model_version'] ?? null,
                'provider' => $data['provider'] ?? null,
                'guardrail_triggered' => $data['guardrail_triggered'] ?? false,
                'intent' => $data['intent'] ?? null,
            ];
        } catch (\Throwable $e) {
            return null;
        }
    }

    private function buildGracefulStreamFallbackPayload(string $message, array $streamMeta = []): array
    {
        $trimmedMessage = trim($message);
        $fallbackAnswer = 'Mình chưa thể hoàn tất phản hồi AI ở chế độ stream lúc này. ';

        if ($trimmedMessage !== '') {
            $fallbackAnswer .= 'Bạn có thể gửi lại câu hỏi';

            if (mb_strlen($trimmedMessage) <= 80) {
                $fallbackAnswer .= ' "' . $trimmedMessage . '"';
            }

            $fallbackAnswer .= ' hoặc tắt SSE để nhận phản hồi ổn định hơn.';
        } else {
            $fallbackAnswer .= 'Bạn có thể gửi lại câu hỏi hoặc tắt SSE để nhận phản hồi ổn định hơn.';
        }

        return [
            'answer' => $fallbackAnswer,
            'model_version' => $streamMeta['model_version'] ?? null,
            'provider' => $streamMeta['provider'] ?? 'graceful_stream_fallback',
            'guardrail_triggered' => false,
            'intent' => $streamMeta['intent'] ?? null,
        ];
    }

    private function baseContextCacheKey(int $nguoiDungId, AiChatSession $session): string
    {
        return implode(':', [
            'ai-chat-context',
            $nguoiDungId,
            $session->id,
            $session->related_ho_so_id ?: 'none',
            $session->related_tin_tuyen_dung_id ?: 'none',
        ]);
    }

    private function refreshSessionSummary(
        AiChatSession $session,
        array $context,
        string $latestQuestion,
        string $latestAnswer,
        ?string $latestIntent = null
    ): void
    {
        $summary = $this->buildSessionSummary($context, $latestQuestion, $latestAnswer, $latestIntent);
        if ($summary === '') {
            return;
        }

        $session->forceFill([
            'summary' => $summary,
        ])->save();
    }

    private function buildSessionSummary(array $context, string $latestQuestion, string $latestAnswer, ?string $latestIntent = null): string
    {
        $careerReport = $context['career_report'] ?? [];
        $relatedJob = $context['related_job'] ?? [];
        $topMatches = $context['top_matching_jobs'] ?? [];
        $candidateProfile = $context['candidate_profile'] ?? [];

        $parts = [];

        $intentLabel = $latestIntent ? $this->intentCodeToLabel($latestIntent) : $this->summarizeIntentLabel($latestQuestion);
        if ($intentLabel !== null) {
            $parts[] = 'Chủ đề gần nhất: ' . $intentLabel . '.';
        }

        if (!empty($careerReport['nghe_de_xuat'])) {
            $parts[] = 'Hướng nghề đang ưu tiên: ' . $careerReport['nghe_de_xuat'] . '.';
        }

        if (!empty($relatedJob['title'])) {
            $parts[] = 'Job đang tham chiếu: ' . $relatedJob['title'] . '.';
        }

        $skills = array_slice($candidateProfile['parsed_skills'] ?? [], 0, 4);
        if (!empty($skills)) {
            $parts[] = 'Kỹ năng nền hiện có: ' . implode(', ', $skills) . '.';
        }

        $missingSkills = [];
        foreach ($topMatches as $match) {
            foreach (($match['missing_skills'] ?? []) as $skill) {
                if (is_string($skill) && $skill !== '' && !in_array($skill, $missingSkills, true)) {
                    $missingSkills[] = $skill;
                }
            }
        }
        if (!empty($missingSkills)) {
            $parts[] = 'Kỹ năng còn thiếu nổi bật: ' . implode(', ', array_slice($missingSkills, 0, 4)) . '.';
        }

        $answerSummary = $this->shortenText($latestAnswer, 220);
        if ($answerSummary !== '') {
            $parts[] = 'Kết luận gần nhất: ' . $answerSummary;
        }

        return trim(implode(' ', $parts));
    }

    private function summarizeIntentLabel(string $message): ?string
    {
        $normalized = mb_strtolower($message);

        $map = [
            'giải thích matching' => ['matching', 'điểm', 'vì sao'],
            'thiếu kỹ năng' => ['thiếu kỹ năng', 'thieu ky nang', 'học gì', 'hoc gi', 'bổ sung'],
            'gợi ý công việc' => ['job nào', 'job nao', 'công việc', 'cong viec', 'ứng tuyển'],
            'định hướng nghề nghiệp' => ['nên theo', 'hướng khác', 'định hướng', 'hướng chính', 'hướng thay thế'],
            'lộ trình học' => ['kế hoạch', 'lộ trình', '3 tháng', '6 tháng', 'giai đoạn'],
            'cải thiện CV' => ['cv', 'hồ sơ', 'ho so', 'sửa', 'chỉnh'],
            'chuẩn bị phỏng vấn' => ['phỏng vấn', 'phong van', 'interview'],
        ];

        foreach ($map as $label => $keywords) {
            foreach ($keywords as $keyword) {
                if (str_contains($normalized, $keyword)) {
                    return $label;
                }
            }
        }

        return null;
    }

    private function intentCodeToLabel(string $intent): ?string
    {
        $map = [
            'matching_explanation' => 'giải thích matching',
            'skill_gap' => 'thiếu kỹ năng',
            'job_recommendation' => 'gợi ý công việc',
            'career_direction' => 'định hướng nghề nghiệp',
            'learning_plan' => 'lộ trình học',
            'cv_improvement' => 'cải thiện CV',
            'interview_prep' => 'chuẩn bị phỏng vấn',
            'cover_letter' => 'thư xin việc',
            'next_step_action' => 'nên làm gì trước',
            'general_career' => 'tư vấn nghề nghiệp',
        ];

        return $map[$intent] ?? null;
    }

    private function shortenText(string $text, int $maxLength): string
    {
        $cleaned = trim(preg_replace('/\s+/u', ' ', str_replace(['**', '__', '`', '#'], '', $text)) ?? '');
        if ($cleaned === '') {
            return '';
        }

        if (mb_strlen($cleaned) <= $maxLength) {
            return $cleaned;
        }

        return rtrim(mb_substr($cleaned, 0, $maxLength - 1)) . '…';
    }
}
