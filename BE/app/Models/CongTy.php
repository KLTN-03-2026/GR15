<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Str;

class CongTy extends Model
{
    use HasFactory;

    protected $table = 'cong_tys';

    protected $fillable = [
        'nguoi_dung_id',
        'ten_cong_ty',
        'ma_so_thue',
        'mo_ta',
        'dia_chi',
        'dien_thoai',
        'email',
        'website',
        'logo',
        'nganh_nghe_id',
        'quy_mo',
        'trang_thai',
    ];

    protected $casts = [
        'nguoi_dung_id' => 'integer',
        'nganh_nghe_id' => 'integer',
        'trang_thai' => 'integer',
    ];

    // ==========================================
    // CONSTANTS
    // ==========================================
    const TRANG_THAI_HOAT_DONG = 1;
    const TRANG_THAI_TAM_NGUNG = 0;

    const VAI_TRO_NOI_BO_OWNER = 'owner';
    const VAI_TRO_NOI_BO_ADMIN_HR = 'admin_hr';
    const VAI_TRO_NOI_BO_RECRUITER = 'recruiter';
    const VAI_TRO_NOI_BO_INTERVIEWER = 'interviewer';
    const VAI_TRO_NOI_BO_VIEWER = 'viewer';

    const QUY_MO_LIST = [
        '1-10',
        '11-50',
        '51-200',
        '201-500',
        '500+',
    ];

    const VAI_TRO_NOI_BO_LABELS = [
        self::VAI_TRO_NOI_BO_OWNER => 'Owner',
        self::VAI_TRO_NOI_BO_ADMIN_HR => 'Admin HR',
        self::VAI_TRO_NOI_BO_RECRUITER => 'Recruiter',
        self::VAI_TRO_NOI_BO_INTERVIEWER => 'Interviewer',
        self::VAI_TRO_NOI_BO_VIEWER => 'Viewer',
    ];

    const VAI_TRO_NOI_BO_CO_THE_QUAN_LY_CONG_TY = [
        self::VAI_TRO_NOI_BO_OWNER,
        self::VAI_TRO_NOI_BO_ADMIN_HR,
    ];

    const VAI_TRO_NOI_BO_CO_THE_QUAN_LY_TIN_TUYEN_DUNG = [
        self::VAI_TRO_NOI_BO_OWNER,
        self::VAI_TRO_NOI_BO_ADMIN_HR,
        self::VAI_TRO_NOI_BO_RECRUITER,
    ];

    const VAI_TRO_NOI_BO_CO_THE_XU_LY_UNG_TUYEN = [
        self::VAI_TRO_NOI_BO_OWNER,
        self::VAI_TRO_NOI_BO_ADMIN_HR,
        self::VAI_TRO_NOI_BO_RECRUITER,
        self::VAI_TRO_NOI_BO_INTERVIEWER,
    ];

    const HR_PERMISSION_CATALOG = [
        [
            'key' => 'company_profile',
            'label' => 'Hồ sơ công ty',
            'description' => 'Cập nhật thông tin công ty, logo, ngành nghề, địa chỉ và trạng thái hồ sơ doanh nghiệp.',
        ],
        [
            'key' => 'members',
            'label' => 'Nhân sự HR',
            'description' => 'Tạo HR mới, gỡ thành viên, cập nhật vai trò và cấp quyền chức năng cho từng tài khoản HR.',
        ],
        [
            'key' => 'jobs',
            'label' => 'Tin tuyển dụng',
            'description' => 'Tạo, cập nhật, xuất bản và quản lý các tin tuyển dụng của công ty.',
        ],
        [
            'key' => 'applications',
            'label' => 'Ứng tuyển',
            'description' => 'Xem, phân công và xử lý hồ sơ ứng tuyển trong pipeline tuyển dụng.',
        ],
        [
            'key' => 'interviews',
            'label' => 'Phỏng vấn',
            'description' => 'Tạo vòng phỏng vấn, cập nhật lịch, đánh giá và kết quả phỏng vấn.',
        ],
        [
            'key' => 'billing',
            'label' => 'Ví & Billing',
            'description' => 'Xem số dư ví AI, lịch sử biến động, bảng giá, quyền lợi gói và thực hiện nạp ví employer.',
        ],
        [
            'key' => 'offers',
            'label' => 'Offer',
            'description' => 'Tạo, gửi và theo dõi phản hồi offer của ứng viên.',
        ],
        [
            'key' => 'onboarding',
            'label' => 'Onboarding',
            'description' => 'Quản lý kế hoạch onboarding, checklist và tài liệu sau khi ứng viên nhận offer.',
        ],
        [
            'key' => 'exports',
            'label' => 'PDF / Export',
            'description' => 'Tải các bản PDF hồ sơ ứng tuyển, báo cáo phỏng vấn, offer và onboarding.',
        ],
        [
            'key' => 'audit_logs',
            'label' => 'Nhật ký thao tác',
            'description' => 'Xem lịch sử thao tác nội bộ của công ty và module HR.',
        ],
    ];

    // ==========================================
    // RELATIONSHIPS
    // ==========================================

    /**
     * NTD sở hữu công ty.
     */
    public function nguoiDung()
    {
        return $this->belongsTo(NguoiDung::class, 'nguoi_dung_id');
    }

    /**
     * Danh sách HR thuộc công ty.
     */
    public function thanhViens()
    {
        return $this->belongsToMany(NguoiDung::class, 'cong_ty_nguoi_dungs', 'cong_ty_id', 'nguoi_dung_id')
            ->withPivot('id', 'vai_tro_noi_bo', 'quyen_noi_bo', 'duoc_tao_boi')
            ->withTimestamps();
    }

    public function vaiTroNoiBos()
    {
        return $this->hasMany(CongTyVaiTroNoiBo::class, 'cong_ty_id');
    }

    /**
     * Ngành nghề chính.
     */
    public function nganhNghe()
    {
        return $this->belongsTo(NganhNghe::class, 'nganh_nghe_id');
    }

    /**
     * Danh sách tin tuyển dụng của công ty.
     */
    public function tinTuyenDungs()
    {
        return $this->hasMany(\App\Models\TinTuyenDung::class, 'cong_ty_id');
    }

    /**
     * Danh sách ứng viên đang theo dõi công ty.
     */
    public function nguoiDungTheoDois()
    {
        return $this->belongsToMany(NguoiDung::class, 'theo_doi_cong_tys', 'cong_ty_id', 'nguoi_dung_id')
            ->withTimestamps();
    }

    // ==========================================
    // HELPERS
    // ==========================================

    public function isHoatDong(): bool
    {
        return $this->trang_thai === self::TRANG_THAI_HOAT_DONG;
    }

    public static function danhSachVaiTroNoiBo(?self $congTy = null): array
    {
        $roles = array_keys(self::VAI_TRO_NOI_BO_LABELS);

        if ($congTy) {
            $customRoles = $congTy->relationLoaded('vaiTroNoiBos')
                ? $congTy->vaiTroNoiBos
                : $congTy->vaiTroNoiBos()->get(['ma_vai_tro']);

            $roles = array_merge($roles, $customRoles->pluck('ma_vai_tro')->all());
        }

        return array_values(array_unique($roles));
    }

    public static function nhanVaiTroNoiBo(?string $role, ?self $congTy = null): string
    {
        if (isset(self::VAI_TRO_NOI_BO_LABELS[$role ?? ''])) {
            return self::VAI_TRO_NOI_BO_LABELS[$role];
        }

        if ($role && $congTy) {
            $customRole = $congTy->relationLoaded('vaiTroNoiBos')
                ? $congTy->vaiTroNoiBos->firstWhere('ma_vai_tro', $role)
                : $congTy->vaiTroNoiBos()->where('ma_vai_tro', $role)->first();

            if ($customRole) {
                return $customRole->ten_vai_tro;
            }
        }

        return 'HR Member';
    }

    public static function vaiTroGocNoiBo(?string $role, ?self $congTy = null): ?string
    {
        if (!$role) {
            return null;
        }

        if (isset(self::VAI_TRO_NOI_BO_LABELS[$role])) {
            return $role;
        }

        if ($congTy) {
            $customRole = $congTy->relationLoaded('vaiTroNoiBos')
                ? $congTy->vaiTroNoiBos->firstWhere('ma_vai_tro', $role)
                : $congTy->vaiTroNoiBos()->where('ma_vai_tro', $role)->first();

            return $customRole?->vai_tro_goc;
        }

        return null;
    }

    public static function quyenTheoVaiTroNoiBo(?string $role, ?self $congTy = null): array
    {
        $normalizedRole = self::vaiTroGocNoiBo($role, $congTy) ?? '';

        return [
            'co_the_xem' => $role !== null && in_array($role, self::danhSachVaiTroNoiBo($congTy), true),
            'co_the_quan_ly_cong_ty' => in_array($normalizedRole, self::VAI_TRO_NOI_BO_CO_THE_QUAN_LY_CONG_TY, true),
            'co_the_quan_ly_tin_tuyen_dung' => in_array($normalizedRole, self::VAI_TRO_NOI_BO_CO_THE_QUAN_LY_TIN_TUYEN_DUNG, true),
            'co_the_xu_ly_ung_tuyen' => in_array($normalizedRole, self::VAI_TRO_NOI_BO_CO_THE_XU_LY_UNG_TUYEN, true),
            'co_the_quan_ly_thanh_vien' => $role === self::VAI_TRO_NOI_BO_OWNER,
        ];
    }

    public static function hrPermissionCatalog(): array
    {
        $catalog = self::HR_PERMISSION_CATALOG;

        if (Schema::hasTable('permission_definitions')) {
            $hasMappedColumn = Schema::hasColumn('permission_definitions', 'mapped_permission_key');
            $customPermissions = PermissionDefinition::query()
                ->where('scope', PermissionDefinition::SCOPE_EMPLOYER)
                ->orderBy('id')
                ->get($hasMappedColumn ? ['key', 'label', 'description', 'mapped_permission_key'] : ['key', 'label', 'description'])
                ->map(fn (PermissionDefinition $permission) => [
                    'key' => $permission->key,
                    'label' => $permission->label,
                    'description' => $permission->description,
                    'mapped_permission_key' => $hasMappedColumn ? $permission->mapped_permission_key : null,
                    'is_custom' => true,
                ])
                ->all();

            $catalog = [
                ...$catalog,
                ...array_filter(
                    $customPermissions,
                    fn (array $permission) => !in_array($permission['key'], array_column($catalog, 'key'), true),
                ),
            ];
        }

        return array_values($catalog);
    }

    public static function hrPermissionKeys(): array
    {
        return array_column(self::hrPermissionCatalog(), 'key');
    }

    public static function hrSystemPermissionKeys(): array
    {
        return array_column(self::HR_PERMISSION_CATALOG, 'key');
    }

    public static function hrMappedPermissionKeys(): array
    {
        if (!Schema::hasTable('permission_definitions') || !Schema::hasColumn('permission_definitions', 'mapped_permission_key')) {
            return [];
        }

        return PermissionDefinition::query()
            ->where('scope', PermissionDefinition::SCOPE_EMPLOYER)
            ->whereNotNull('mapped_permission_key')
            ->pluck('mapped_permission_key', 'key')
            ->filter()
            ->all();
    }

    public static function defaultHrPermissions(): array
    {
        return array_fill_keys(self::hrPermissionKeys(), true);
    }

    public static function defaultHrPermissionsForRole(?string $role): array
    {
        $permissions = array_fill_keys(self::hrPermissionKeys(), false);
        $baseRole = self::vaiTroGocNoiBo($role) ?? $role;

        if ($baseRole === self::VAI_TRO_NOI_BO_OWNER) {
            return self::defaultHrPermissions();
        }

        if ($baseRole === self::VAI_TRO_NOI_BO_ADMIN_HR) {
            return [
                ...$permissions,
                'company_profile' => true,
                'jobs' => true,
                'applications' => true,
                'interviews' => true,
                'offers' => true,
                'onboarding' => true,
                'exports' => true,
                'audit_logs' => true,
            ];
        }

        if ($baseRole === self::VAI_TRO_NOI_BO_RECRUITER) {
            return [
                ...$permissions,
                'jobs' => true,
                'applications' => true,
                'interviews' => true,
                'offers' => true,
                'onboarding' => true,
                'exports' => true,
            ];
        }

        if ($baseRole === self::VAI_TRO_NOI_BO_INTERVIEWER) {
            return [
                ...$permissions,
                'applications' => true,
                'interviews' => true,
                'exports' => true,
            ];
        }

        return [
            ...$permissions,
            'applications' => true,
        ];
    }

    public static function normalizeHrPermissions(?array $permissions): array
    {
        $defaults = array_fill_keys(self::hrPermissionKeys(), false);

        if (!$permissions) {
            return $defaults;
        }

        $normalized = [];
        foreach ($defaults as $key => $defaultValue) {
            $normalized[$key] = array_key_exists($key, $permissions)
                ? (bool) $permissions[$key]
                : $defaultValue;
        }

        foreach (self::hrMappedPermissionKeys() as $customKey => $mappedKey) {
            if (($normalized[$customKey] ?? false) && array_key_exists($mappedKey, $normalized)) {
                $normalized[$mappedKey] = true;
            }
        }

        return $normalized;
    }
}
