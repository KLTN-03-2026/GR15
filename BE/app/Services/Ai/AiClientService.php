<?php

namespace App\Services\Ai;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\RequestException;
use Illuminate\Support\Facades\Http;
use RuntimeException;
use Throwable;

class AiClientService
{
    private string $baseUrl;
    private int $timeout;

    public function __construct()
    {
        $this->baseUrl = rtrim((string) config('services.ai_service.base_url', env('AI_SERVICE_URL', 'http://127.0.0.1:8001')), '/');
        $this->timeout = (int) config('services.ai_service.timeout', env('AI_SERVICE_TIMEOUT', 120));
    }

    public function parseCv(int $hoSoId, string $filePath): array
    {
        return $this->post('/parse/cv', [
            'ho_so_id' => $hoSoId,
            'file_path' => $filePath,
        ]);
    }

    public function parseCvFromRawText(int $hoSoId, string $rawText): array
    {
        return $this->post('/parse/cv', [
            'ho_so_id' => $hoSoId,
            'raw_text' => $rawText,
        ]);
    }

    public function parseJd(int $tinTuyenDungId, string $jobText): array
    {
        return $this->post('/parse/jd', [
            'tin_tuyen_dung_id' => $tinTuyenDungId,
            'job_text' => $jobText,
        ]);
    }

    public function matchCvJd(int $hoSoId, int $tinTuyenDungId, array $cvProfile = [], array $jdProfile = []): array
    {
        return $this->post('/match/cv-jd', [
            'ho_so_id' => $hoSoId,
            'tin_tuyen_dung_id' => $tinTuyenDungId,
            'cv_profile' => $cvProfile,
            'jd_profile' => $jdProfile,
        ]);
    }

    public function generateCoverLetter(
        int $hoSoId,
        int $tinTuyenDungId,
        array $cvProfile = [],
        array $jdProfile = [],
        array $matchingProfile = []
    ): array
    {
        return $this->post('/generate/cover-letter', [
            'ho_so_id' => $hoSoId,
            'tin_tuyen_dung_id' => $tinTuyenDungId,
            'cv_profile' => $cvProfile,
            'jd_profile' => $jdProfile,
            'matching_profile' => $matchingProfile,
        ]);
    }

    public function generateCareerReport(int $hoSoId, array $cvProfile = [], array $matchingProfiles = []): array
    {
        return $this->post('/generate/career-report', [
            'ho_so_id' => $hoSoId,
            'cv_profile' => $cvProfile,
            'matching_profiles' => $matchingProfiles,
        ]);
    }

    public function semanticSearchJobs(string $query, array $documents, int $topK = 10): array
    {
        return $this->post('/search/semantic/jobs', [
            'query' => $query,
            'top_k' => $topK,
            'documents' => $documents,
        ]);
    }

    public function careerChat(int $sessionId, string $message, array $history = [], array $context = [], bool $forceModel = false): array
    {
        return $this->post('/chat/career-consultant', [
            'session_id' => $sessionId,
            'message' => $message,
            'history' => $history,
            'context' => $context,
            'force_model' => $forceModel,
        ]);
    }

    public function careerChatStream(int $sessionId, string $message, array $history = [], array $context = [], bool $forceModel = false, ?callable $onEvent = null): void
    {
        $this->stream('/chat/career-consultant/stream', [
            'session_id' => $sessionId,
            'message' => $message,
            'history' => $history,
            'context' => $context,
            'force_model' => $forceModel,
        ], $onEvent);
    }

    public function generateMockInterviewQuestion(
        int $sessionId,
        array $interviewContext = [],
        array $transcript = [],
        int $questionIndex = 1,
        int $maxQuestions = 5
    ): array
    {
        return $this->post('/interview/mock/question', [
            'session_id' => $sessionId,
            'interview_context' => $interviewContext,
            'transcript' => $transcript,
            'question_index' => $questionIndex,
            'max_questions' => $maxQuestions,
        ]);
    }

    public function evaluateMockInterviewAnswer(
        int $sessionId,
        array $questionPayload,
        string $answer,
        array $interviewContext = [],
        array $transcript = [],
        int $maxQuestions = 5
    ): array {
        return $this->post('/interview/mock/evaluate', [
            'session_id' => $sessionId,
            'question_payload' => $questionPayload,
            'answer' => $answer,
            'interview_context' => $interviewContext,
            'transcript' => $transcript,
            'max_questions' => $maxQuestions,
        ]);
    }

    public function generateMockInterviewReport(int $sessionId, array $interviewContext = [], array $transcript = []): array
    {
        return $this->post('/interview/mock/report', [
            'session_id' => $sessionId,
            'interview_context' => $interviewContext,
            'transcript' => $transcript,
        ]);
    }

    private function post(string $uri, array $payload): array
    {
        try {
            $response = Http::timeout($this->timeout)
                ->acceptJson()
                ->asJson()
                ->post($this->baseUrl . $uri, $payload)
                ->throw();
        } catch (ConnectionException $e) {
            throw new RuntimeException('Không thể kết nối tới AI service.', 0, $e);
        } catch (RequestException $e) {
            $message = $e->response?->json('message')
                ?? $e->response?->body()
                ?? 'AI service trả về lỗi.';

            throw new RuntimeException((string) $message, 0, $e);
        }

        return $response->json();
    }

    private function stream(string $uri, array $payload, ?callable $onEvent = null): void
    {
        $url = $this->baseUrl . $uri;
        $buffer = '';
        $currentEvent = 'message';
        $dataLines = [];
        $dispatchEvent = function () use (&$currentEvent, &$dataLines, $onEvent): void {
            if ($dataLines === []) {
                return;
            }

            $json = implode("\n", $dataLines);
            try {
                $payload = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
            } catch (Throwable $e) {
                $payload = ['raw' => $json];
            }

            if ($onEvent) {
                $onEvent($currentEvent ?: 'message', $payload);
            }

            $currentEvent = 'message';
            $dataLines = [];
        };

        $curl = curl_init($url);

        if ($curl === false) {
            throw new RuntimeException('Không thể khởi tạo kết nối stream tới AI service.');
        }

        curl_setopt_array($curl, [
            CURLOPT_POST => true,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Accept: text/event-stream',
            ],
            CURLOPT_POSTFIELDS => json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_RETURNTRANSFER => false,
            CURLOPT_HEADER => false,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_WRITEFUNCTION => function ($ch, string $chunk) use (&$buffer, &$currentEvent, &$dataLines, $dispatchEvent) {
                $buffer .= $chunk;

                while (($position = strpos($buffer, "\n")) !== false) {
                    $line = substr($buffer, 0, $position);
                    $buffer = substr($buffer, $position + 1);
                    $line = rtrim($line, "\r");

                    if ($line === '') {
                        $dispatchEvent();
                        continue;
                    }

                    if (str_starts_with($line, 'event:')) {
                        $currentEvent = trim(substr($line, 6));
                        continue;
                    }

                    if (str_starts_with($line, 'data:')) {
                        $dataLines[] = trim(substr($line, 5));
                    }
                }

                return strlen($chunk);
            },
        ]);

        $result = curl_exec($curl);

        if ($result === false) {
            $error = curl_error($curl) ?: 'Không thể stream dữ liệu từ AI service.';
            curl_close($curl);
            throw new RuntimeException($error);
        }

        $remaining = trim(str_replace("\r", '', $buffer));
        if ($remaining !== '') {
            foreach (explode("\n", $remaining) as $line) {
                if (str_starts_with($line, 'event:')) {
                    $currentEvent = trim(substr($line, 6));
                    continue;
                }

                if (str_starts_with($line, 'data:')) {
                    $dataLines[] = trim(substr($line, 5));
                }
            }
        }

        $dispatchEvent();

        $statusCode = (int) curl_getinfo($curl, CURLINFO_RESPONSE_CODE);
        curl_close($curl);

        if ($statusCode >= 400) {
            throw new RuntimeException('AI service trả về lỗi khi stream hội thoại.');
        }
    }
}
