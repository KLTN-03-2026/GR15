<?php

use App\Models\AppNotification;
use App\Models\InterviewRound;
use App\Models\NguoiDung;
use App\Models\UngTuyen;
use Illuminate\Support\Facades\URL;

it('lets employer create interview round and candidate confirm attendance', function () {
    $candidate = NguoiDung::factory()->ungVien()->create();
    $employer = NguoiDung::factory()->nhaTuyenDung()->create();
    $company = createCompanyForEmployer($employer);
    $job = createJobForCompany($company, ['tieu_de' => 'Backend Developer Laravel']);
    $application = createApplicationForCandidate($candidate, $job, [], [
        'trang_thai' => UngTuyen::TRANG_THAI_DA_XEM,
    ]);

    $scheduledAt = now('Asia/Ho_Chi_Minh')->addDays(3)->setTime(9, 30);

    $this->actingAs($employer, 'sanctum')
        ->postJson("/api/v1/nha-tuyen-dung/ung-tuyens/{$application->id}/interview-rounds", [
            'ten_vong' => 'Technical Interview',
            'loai_vong' => 'technical',
            'ngay_hen_phong_van' => $scheduledAt->format('Y-m-d H:i:s'),
            'hinh_thuc_phong_van' => 'online',
            'nguoi_phong_van' => 'Tech Lead',
            'link_phong_van' => 'https://meet.example.test/backend',
        ])
        ->assertCreated()
        ->assertJsonPath('success', true)
        ->assertJsonPath('data.ten_vong', 'Technical Interview');

    $round = InterviewRound::where('ung_tuyen_id', $application->id)->firstOrFail();

    expect($application->fresh()->vong_phong_van_hien_tai)->toBe('technical');
    expect(AppNotification::where('nguoi_dung_id', $candidate->id)
        ->where('loai', 'candidate_interview_round_scheduled')
        ->where('du_lieu_bo_sung->interview_round_id', $round->id)
        ->exists())->toBeTrue();

    $this->actingAs($candidate, 'sanctum')
        ->patchJson("/api/v1/ung-vien/ung-tuyens/{$application->id}/interview-rounds/{$round->id}/xac-nhan", [
            'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_DA_XAC_NHAN,
        ])
        ->assertOk()
        ->assertJsonPath('success', true);

    expect($round->fresh()->trang_thai_tham_gia)->toBe(UngTuyen::PHONG_VAN_DA_XAC_NHAN);
    expect($application->fresh()->trang_thai_tham_gia_phong_van)->toBe(UngTuyen::PHONG_VAN_DA_XAC_NHAN);

    $timelineResponse = $this->actingAs($candidate, 'sanctum')
        ->getJson('/api/v1/ung-vien/ung-tuyens');

    $timelineResponse
        ->assertOk()
        ->assertJsonPath('data.data.0.application_timeline.0.key', 'application_submitted');

    expect(collect($timelineResponse->json('data.data.0.application_timeline'))->pluck('key')->all())
        ->toContain('interview_round_' . $round->id);
});

it('blocks creating interview round for final application', function () {
    $candidate = NguoiDung::factory()->ungVien()->create();
    $employer = NguoiDung::factory()->nhaTuyenDung()->create();
    $company = createCompanyForEmployer($employer);
    $job = createJobForCompany($company);
    $application = createApplicationForCandidate($candidate, $job, [], [
        'trang_thai' => UngTuyen::TRANG_THAI_TU_CHOI,
    ]);

    $this->actingAs($employer, 'sanctum')
        ->postJson("/api/v1/nha-tuyen-dung/ung-tuyens/{$application->id}/interview-rounds", [
            'ten_vong' => 'Final Interview',
            'ngay_hen_phong_van' => now('Asia/Ho_Chi_Minh')->addDays(2)->format('Y-m-d H:i:s'),
        ])
        ->assertUnprocessable();
});

it('redirects email interview actions to frontend result page', function () {
    $candidate = NguoiDung::factory()->ungVien()->create();
    $employer = NguoiDung::factory()->nhaTuyenDung()->create();
    $company = createCompanyForEmployer($employer);
    $job = createJobForCompany($company);
    $application = createApplicationForCandidate($candidate, $job, [], [
        'trang_thai' => UngTuyen::TRANG_THAI_DA_XEM,
        'ngay_hen_phong_van' => now()->addDays(3),
        'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_CHO_XAC_NHAN,
    ]);

    $validUrl = URL::temporarySignedRoute(
        'ung-vien.ung-tuyens.confirm-interview-email',
        now()->addDay(),
        [
            'id' => $application->id,
            'action' => 'accept',
            'user' => $candidate->id,
        ],
    );

    $validResponse = $this->get($validUrl);
    $validResponse->assertRedirect();
    expect($validResponse->headers->get('Location'))
        ->toContain('/application-action-result?type=interview')
        ->toContain('status=accepted')
        ->toContain('application_id=' . $application->id);

    $expiredUrl = URL::temporarySignedRoute(
        'ung-vien.ung-tuyens.confirm-interview-email',
        now()->subMinute(),
        [
            'id' => $application->id,
            'action' => 'decline',
            'user' => $candidate->id,
        ],
    );

    $expiredResponse = $this->get($expiredUrl);
    $expiredResponse->assertRedirect();
    expect($expiredResponse->headers->get('Location'))
        ->toContain('/application-action-result?type=interview')
        ->toContain('status=expired');
});
