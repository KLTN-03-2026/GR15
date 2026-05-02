<?php

use App\Models\CongTy;
use App\Models\CongTyVaiTroNoiBo;
use App\Models\NguoiDung;
use App\Models\PermissionDefinition;
use App\Notifications\ResetPasswordLinkNotification;
use Illuminate\Support\Facades\Notification;

it('lets company owner create a new hr account directly', function () {
    Notification::fake();

    $owner = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company = CongTy::factory()->create([
        'nguoi_dung_id' => $owner->id,
    ]);
    $company->thanhViens()->attach($owner->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_OWNER,
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);

    $response = $this->actingAs($owner, 'sanctum')
        ->postJson('/api/v1/nha-tuyen-dung/cong-ty/thanh-viens', [
            'ho_ten' => 'Nguyen HR',
            'email' => 'hr.created@example.com',
            'mat_khau' => 'Password123!',
            'so_dien_thoai' => '0900000001',
            'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_RECRUITER,
        ]);

    $response
        ->assertCreated()
        ->assertJsonPath('success', true)
        ->assertJsonPath('data.hr.email', 'hr.created@example.com')
        ->assertJsonFragment(['email' => 'hr.created@example.com']);

    $hr = NguoiDung::query()->where('email', 'hr.created@example.com')->firstOrFail();

    expect($hr->isNhaTuyenDung())->toBeTrue();
    expect($hr->email_verified_at)->not->toBeNull();
    expect($hr->layVaiTroNoiBoCongTy($company))->toBe(CongTy::VAI_TRO_NOI_BO_RECRUITER);

    Notification::assertNothingSent();
});

it('does not create an hr account with an existing email', function () {
    Notification::fake();

    $owner = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company = CongTy::factory()->create([
        'nguoi_dung_id' => $owner->id,
    ]);
    $company->thanhViens()->attach($owner->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_OWNER,
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);
    NguoiDung::factory()->nhaTuyenDung()->create([
        'email' => 'existing.hr@example.com',
        'email_verified_at' => now(),
    ]);

    $this->actingAs($owner, 'sanctum')
        ->postJson('/api/v1/nha-tuyen-dung/cong-ty/thanh-viens', [
            'ho_ten' => 'Existing HR',
            'email' => 'existing.hr@example.com',
            'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_RECRUITER,
        ])
        ->assertUnprocessable()
        ->assertJsonPath('success', false);

    Notification::assertNothingSent();
});

it('lets company owner manage custom internal roles and assign them to hr accounts', function () {
    Notification::fake();

    $owner = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company = CongTy::factory()->create([
        'nguoi_dung_id' => $owner->id,
    ]);
    $company->thanhViens()->attach($owner->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_OWNER,
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);

    $roleResponse = $this->actingAs($owner, 'sanctum')
        ->postJson('/api/v1/nha-tuyen-dung/cong-ty/vai-tro-noi-bo', [
            'ten_vai_tro' => 'Talent Acquisition Lead',
            'mo_ta' => 'Lead tuyển dụng nội bộ',
            'vai_tro_goc' => CongTy::VAI_TRO_NOI_BO_RECRUITER,
        ]);

    $roleResponse
        ->assertCreated()
        ->assertJsonPath('success', true)
        ->assertJsonPath('data.vai_tro.ten_vai_tro', 'Talent Acquisition Lead')
        ->assertJsonPath('data.vai_tro.vai_tro_goc', CongTy::VAI_TRO_NOI_BO_RECRUITER);

    $roleCode = $roleResponse->json('data.vai_tro.ma_vai_tro');

    $this->actingAs($owner, 'sanctum')
        ->postJson('/api/v1/nha-tuyen-dung/cong-ty/thanh-viens', [
            'ho_ten' => 'Custom HR',
            'email' => 'custom.hr@example.com',
            'mat_khau' => 'Password123!',
            'vai_tro_noi_bo' => $roleCode,
        ])
        ->assertCreated()
        ->assertJsonFragment(['ten_vai_tro_noi_bo' => 'Talent Acquisition Lead']);

    $hr = NguoiDung::query()->where('email', 'custom.hr@example.com')->firstOrFail();

    expect($hr->layVaiTroNoiBoCongTy($company))->toBe($roleCode);
    expect($hr->coVaiTroNoiBoCongTy(CongTy::VAI_TRO_NOI_BO_RECRUITER, $company))->toBeTrue();

    $role = CongTyVaiTroNoiBo::query()->where('ma_vai_tro', $roleCode)->firstOrFail();

    $this->actingAs($owner, 'sanctum')
        ->patchJson("/api/v1/nha-tuyen-dung/cong-ty/vai-tro-noi-bo/{$role->id}", [
            'ten_vai_tro' => 'Senior Talent Lead',
            'mo_ta' => 'Lead tuyển dụng senior',
            'vai_tro_goc' => CongTy::VAI_TRO_NOI_BO_ADMIN_HR,
        ])
        ->assertOk()
        ->assertJsonPath('data.vai_tro.ten_vai_tro', 'Senior Talent Lead')
        ->assertJsonFragment(['ten_vai_tro_noi_bo' => 'Senior Talent Lead']);

    expect($hr->fresh()->coVaiTroNoiBoCongTy(CongTy::VAI_TRO_NOI_BO_ADMIN_HR, $company))->toBeTrue();
});

it('lets company owner configure feature permissions for each hr account', function () {
    $owner = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company = CongTy::factory()->create([
        'nguoi_dung_id' => $owner->id,
    ]);
    $company->thanhViens()->attach($owner->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_OWNER,
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);
    $hr = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company->thanhViens()->attach($hr->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_VIEWER,
        'quyen_noi_bo' => json_encode(CongTy::normalizeHrPermissions(null)),
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);

    $permissions = CongTy::normalizeHrPermissions([
        'jobs' => true,
        'applications' => true,
    ]);

    $this->actingAs($owner, 'sanctum')
        ->putJson("/api/v1/nha-tuyen-dung/cong-ty/thanh-viens/{$hr->id}/permissions", [
            'quyen_noi_bo' => $permissions,
        ])
        ->assertOk()
        ->assertJsonPath('data.quyen_noi_bo.jobs', true)
        ->assertJsonPath('data.quyen_noi_bo.members', false);

    expect($hr->fresh()->coQuyenNoiBoCongTy('jobs', $company))->toBeTrue();
    expect($hr->fresh()->coQuyenNoiBoCongTy('members', $company))->toBeFalse();
});

it('maps a newly created hr permission to an existing employer feature', function () {
    $owner = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company = CongTy::factory()->create([
        'nguoi_dung_id' => $owner->id,
    ]);
    $company->thanhViens()->attach($owner->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_OWNER,
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);
    $hr = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company->thanhViens()->attach($hr->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_VIEWER,
        'quyen_noi_bo' => json_encode(CongTy::normalizeHrPermissions(null)),
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);

    $definitionResponse = $this->actingAs($owner, 'sanctum')
        ->postJson('/api/v1/nha-tuyen-dung/cong-ty/thanh-viens/permissions/definitions', [
            'label' => 'Quản lý ví',
            'description' => 'Cho phép HR thao tác ví employer.',
            'mapped_permission_key' => 'billing',
        ]);

    $definitionResponse
        ->assertCreated()
        ->assertJsonPath('data.permission.mapped_permission_key', 'billing');

    $permissionKey = $definitionResponse->json('data.permission.key');
    $permissions = CongTy::normalizeHrPermissions([
        $permissionKey => true,
    ]);

    $this->actingAs($owner, 'sanctum')
        ->putJson("/api/v1/nha-tuyen-dung/cong-ty/thanh-viens/{$hr->id}/permissions", [
            'quyen_noi_bo' => $permissions,
        ])
        ->assertOk()
        ->assertJsonPath("data.quyen_noi_bo.{$permissionKey}", true)
        ->assertJsonPath('data.quyen_noi_bo.billing', true);

    expect(PermissionDefinition::query()->where('key', $permissionKey)->value('mapped_permission_key'))->toBe('billing');
    expect($hr->fresh()->coQuyenNoiBoCongTy('billing', $company))->toBeTrue();
});

it('prevents hr without members permission from reading hr management data', function () {
    $owner = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company = CongTy::factory()->create([
        'nguoi_dung_id' => $owner->id,
    ]);
    $company->thanhViens()->attach($owner->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_OWNER,
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);
    $hr = NguoiDung::factory()->nhaTuyenDung()->create([
        'email_verified_at' => now(),
    ]);
    $company->thanhViens()->attach($hr->id, [
        'vai_tro_noi_bo' => CongTy::VAI_TRO_NOI_BO_VIEWER,
        'quyen_noi_bo' => json_encode(CongTy::normalizeHrPermissions([
            'company_profile' => true,
            'jobs' => true,
            'applications' => true,
        ])),
        'duoc_tao_boi' => $owner->id,
        'created_at' => now(),
        'updated_at' => now(),
    ]);

    $this->actingAs($hr, 'sanctum')
        ->getJson('/api/v1/nha-tuyen-dung/cong-ty/thanh-viens')
        ->assertForbidden()
        ->assertJsonPath('code', 'COMPANY_ROLE_FORBIDDEN');

    $this->actingAs($hr, 'sanctum')
        ->getJson('/api/v1/nha-tuyen-dung/cong-ty/vai-tro-noi-bo')
        ->assertForbidden()
        ->assertJsonPath('code', 'COMPANY_ROLE_FORBIDDEN');

    $this->actingAs($hr, 'sanctum')
        ->getJson('/api/v1/nha-tuyen-dung/cong-ty')
        ->assertOk()
        ->assertJsonPath('data.quyen_noi_bo.members', false)
        ->assertJsonPath('data.thanh_viens', [])
        ->assertJsonPath('data.catalog_quyen_noi_bo', []);
});
