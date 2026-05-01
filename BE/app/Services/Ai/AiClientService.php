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

    public function __construct(private readonly AiUsageLogger $usageLogger)
    {
        $this->baseUrl = rtrim((string) config('services.ai_service.base_url', env('AI_SERVICE_URL', 'http://127.0.0.1:8001')), '/');
        $this->timeout = (int) config('services.ai_service.timeout', env('AI_SERVICE_TIMEOUT', 120));
    }

    public function parseCv(int $hoSoId, string $filePath): array
    {
        return $this->post('/parse/cv', [
            'ho_so_id' => $hoSoId,
            'file_path' => $filePath,
        ], 'cv_parse');
    }

    public function parseCvFromRawText(int $hoSoId, string $rawText): array
    {
        return $this->post('/parse/cv', [
            'ho_so_id' => $hoSoId,
            'raw_text' => $rawText,
        ], 'cv_parse_raw_text');
    }

    public function parseJd(int $tinTuyenDungId, string $jobText): array
    {
        return $this->post('/parse/jd', [
            'tin_tuyen_dung_id' => $tinTuyenDungId,
            'job_text' => $jobText,
        ], 'jd_parse');
    }

    public function matchCvJd(int $hoSoId, int $tinTuyenDungId, array $cvProfile = [], array $jdProfile = []): array
    {
        return $this->post('/match/cv-jd', [
            'ho_so_id' => $hoSoId,
            'tin_tuyen_dung_id' => $tinTuyenDungId,
            'cv_profile' => $cvProfile,
            'jd_profile' => $jdProfile,
        ], 'cv_jd_matching');
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
        ], 'cover_letter');
    }

    public function generateCareerReport(int $hoSoId, array $cvProfile = [], array $matchingProfiles = []): array
    {
        return $this->post('/generate/career-report', [
            'ho_so_id' => $hoSoId,
            'cv_profile' => $cvProfile,
            'matching_profiles' => $matchingProfiles,
        ], 'career_report');
    }

    public function tailorCvForJob(int $hoSoId, int $tinTuyenDungId, array $cvProfile = [], array $jdProfile = []): array
    {
        return $this->post('/generate/cv-tailoring', [
            'ho_so_id' => $hoSoId,
            'tin_tuyen_dung_id' => $tinTuyenDungId,
            'cv_profile' => $cvProfile,
            'jd_profile' => $jdProfile,
        ], 'cv_tailoring');
    }

    public function generateCvBuilderWriting(array $cvProfile = [], string $section = 'summary', array $options = []): array
    {
        return $this->post('/generate/cv-builder-writing', [
            'cv_profile' => $cvProfile,
            'section' => $section,
            'options' => $options,
        ], 'cv_builder_ai_writing');
    }

    public function careerChat(int $sessionId, string $message, array $history = [], array $context = [], bool $forceModel = false): array
    {
        return $this->post('/chat/career-consultant', [
            'session_id' => $sessionId,
            'message' => $message,
            'history' => $history,
            'context' => $context,
            'force_model' => $forceModel,
        ], 'career_chat');
    }

    public function careerChatStream(int $sessionId, string $message, array $history = [], array $context = [], bool $forceModel = false, ?callable $onEvent = null): void
    {
        $this->stream('/chat/career-consultant/stream', [
            'session_id' => $sessionId,
            'message' => $message,
            'history' => $history,
            'context' => $context,
            'force_model' => $forceModel,
        ], 'career_chat_stream', $onEvent);
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
        ], 'mock_interview_question');
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
        ], 'mock_interview_answer_evaluation');
    }

    public function generateMockInterviewReport(int $sessionId, array $interviewContext = [], array $transcript = []): array
    {
        return $this->post('/interview/mock/report', [
            'session_id' => $sessionId,
            'interview_context' => $interviewContext,
            'transcript' => $transcript,
        ], 'mock_interview_report');
    }

    public function generateInterviewCopilot(int $ungTuyenId, array $applicationContext = []): array
    {
        return $this->post('/interview/copilot/generate', [
            'ung_tuyen_id' => $ungTuyenId,
            'application_context' => $applicationContext,
        ], 'interview_copilot_generate');
    }

    public function evaluateInterviewCopilot(int $ungTuyenId, array $applicationContext = [], array $interviewNotes = []): array
    {
        return $this->post('/interview/copilot/evaluate', [
            'ung_tuyen_id' => $ungTuyenId,
            'application_context' => $applicationContext,
            'interview_notes' => $interviewNotes,
        ], 'interview_copilot_evaluate');
    }

    public function recordFallback(string $feature, ?string $reason = null, array $payload = [], array $metadata = []): void
    {
        $this->usageLogger->logFallback($feature, $reason, $payload, $metadata);
    }

    private function post(string $uri, array $payload, string $feature): array
    {
        $startedAt = microtime(true);

        try {
            $response = Http::timeout($this->timeout)
                ->acceptJson()
                ->asJson()
                ->post($this->baseUrl . $uri, $payload)
                ->throw();
        } catch (ConnectionException $e) {
            $exception = new RuntimeException('Không thể kết nối tới AI service.', 0, $e);
            $this->usageLogger->logError($feature, $uri, $payload, $exception, $startedAt);
            throw $exception;
        } catch (RequestException $e) {
            $message = $e->response?->json('message')
                ?? $e->response?->body()
                ?? 'AI service trả về lỗi.';

            $exception = new RuntimeException((string) $message, 0, $e);
            $this->usageLogger->logError($feature, $uri, $payload, $exception, $startedAt, $e->response?->status());
            throw $exception;
        }

        $json = $response->json();
        $this->usageLogger->logSuccess($feature, $uri, $payload, $json, $startedAt, $response);

        return $json;
    }

    private function stream(string $uri, array $payload, string $feature, ?callable $onEvent = null): void
    {
        $startedAt = microtime(true);
        $url = $this->baseUrl . $uri;
        $buffer = '';
        $currentEvent = 'message';
        $dataLines = [];
        $lastPayload = [];
        $dispatchEvent = function () use (&$currentEvent, &$dataLines, &$lastPayload, $onEvent): void {
            if ($dataLines === []) {
                return;
            }

            $json = implode("\n", $dataLines);
            try {
                $payload = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
            } catch (Throwable) {
                $payload = ['raw' => $json];
            }

            $lastPayload = $payload;

            if ($onEvent) {
                $onEvent($currentEvent ?: 'message', $payload);
            }

            $currentEvent = 'message';
            $dataLines = [];
        };

        try {
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

            $this->usageLogger->logSuccess($feature, $uri, $payload, $lastPayload, $startedAt);
        } catch (Throwable $exception) {
            $this->usageLogger->logError($feature, $uri, $payload, $exception, $startedAt);
            throw $exception;
        }
    }
}
