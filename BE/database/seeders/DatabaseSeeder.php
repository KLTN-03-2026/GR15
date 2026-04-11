<?php

namespace Database\Seeders;

use App\Models\CongTy;
use App\Models\HoSo;
use App\Models\KetQuaMatching;
use App\Models\KyNang;
use App\Models\NganhNghe;
use App\Models\NguoiDung;
use App\Models\NguoiDungKyNang;
use App\Models\TinTuyenDung;
use App\Models\TuVanNgheNghiep;
use App\Models\UngTuyen;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Carbon;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $candidate = NguoiDung::query()->firstOrCreate(
            ['email' => 'candidate@hoanglong.local'],
            [
                'ho_ten' => 'Ứng viên Hoàng Long',
                'mat_khau' => '123456',
                'so_dien_thoai' => '0901234567',
                'vai_tro' => 0,
                'trang_thai' => 1,
                'email_verified_at' => now(),
            ]
        );

        $employer = NguoiDung::query()->firstOrCreate(
            ['email' => 'employer@hoanglong.local'],
            [
                'ho_ten' => 'Nhà tuyển dụng Hoàng Long',
                'mat_khau' => '123456',
                'so_dien_thoai' => '0912345678',
                'vai_tro' => 1,
                'trang_thai' => 1,
                'email_verified_at' => now(),
            ]
        );

        $backend = NganhNghe::query()->firstOrCreate(
            ['slug' => 'backend-development'],
            [
                'ten_nganh' => 'Backend Development',
                'mo_ta' => 'Phát triển dịch vụ, API và hệ thống dữ liệu.',
                'trang_thai' => 1,
            ]
        );

        $frontend = NganhNghe::query()->firstOrCreate(
            ['slug' => 'frontend-development'],
            [
                'ten_nganh' => 'Frontend Development',
                'mo_ta' => 'Phát triển giao diện web hiện đại.',
                'trang_thai' => 1,
            ]
        );

        foreach (['Laravel', 'Vue.js', 'MySQL', 'REST API', 'Tailwind CSS'] as $skillName) {
            KyNang::query()->firstOrCreate(
                ['ten_ky_nang' => $skillName],
                ['mo_ta' => $skillName]
            );
        }

        $company = CongTy::query()->firstOrCreate(
            ['ma_so_thue' => '0312345678'],
            [
                'nguoi_dung_id' => $employer->id,
                'ten_cong_ty' => 'Hoang Long Digital',
                'mo_ta' => 'Doanh nghiệp công nghệ tập trung vào nền tảng tuyển dụng và tự động hóa quy trình nhân sự.',
                'dia_chi' => 'Quận 1, TP. Hồ Chí Minh',
                'website' => 'https://hoanglong.example.com',
                'email' => 'hr@hoanglong.example.com',
                'dien_thoai' => '02812345678',
                'nganh_nghe_id' => $backend->id,
                'quy_mo' => '51-200',
                'trang_thai' => 1,
            ]
        );

        $jobs = [
            [
                'tieu_de' => 'Backend Laravel Developer',
                'nganh' => $backend,
                'dia_diem_lam_viec' => 'TP. Hồ Chí Minh',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 3,
                'muc_luong_tu' => 18000000,
                'muc_luong_den' => 28000000,
                'kinh_nghiem_yeu_cau' => '2 năm',
                'trinh_do_yeu_cau' => 'Đại học',
                'mo_ta_cong_viec' => 'Xây dựng REST API, tối ưu truy vấn MySQL và tích hợp nghiệp vụ tuyển dụng.',
            ],
            [
                'tieu_de' => 'Frontend Vue Developer',
                'nganh' => $frontend,
                'dia_diem_lam_viec' => 'Remote',
                'hinh_thuc_lam_viec' => 'Remote',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 2,
                'muc_luong_tu' => 15000000,
                'muc_luong_den' => 24000000,
                'kinh_nghiem_yeu_cau' => '1-2 năm',
                'trinh_do_yeu_cau' => 'Cao đẳng',
                'mo_ta_cong_viec' => 'Phát triển giao diện Vue 3, tối ưu UX và phối hợp chặt với backend Laravel.',
            ],
            [
                'tieu_de' => 'Fullstack Intern',
                'nganh' => $backend,
                'dia_diem_lam_viec' => 'Đà Nẵng',
                'hinh_thuc_lam_viec' => 'Thực tập',
                'cap_bac' => 'Thực tập sinh',
                'so_luong_tuyen' => 4,
                'muc_luong_tu' => 4000000,
                'muc_luong_den' => 7000000,
                'kinh_nghiem_yeu_cau' => 'Không yêu cầu',
                'trinh_do_yeu_cau' => 'Sinh viên',
                'mo_ta_cong_viec' => 'Tham gia xây dựng sản phẩm web tuyển dụng, học quy trình làm việc thực tế cùng đội kỹ thuật.',
            ],
        ];

        foreach ($jobs as $jobData) {
            $job = TinTuyenDung::query()->firstOrCreate(
                [
                    'cong_ty_id' => $company->id,
                    'tieu_de' => $jobData['tieu_de'],
                ],
                [
                    'mo_ta_cong_viec' => $jobData['mo_ta_cong_viec'],
                    'dia_diem_lam_viec' => $jobData['dia_diem_lam_viec'],
                    'hinh_thuc_lam_viec' => $jobData['hinh_thuc_lam_viec'],
                    'cap_bac' => $jobData['cap_bac'],
                    'so_luong_tuyen' => $jobData['so_luong_tuyen'],
                    'muc_luong_tu' => $jobData['muc_luong_tu'],
                    'muc_luong_den' => $jobData['muc_luong_den'],
                    'don_vi_luong' => 'VND',
                    'kinh_nghiem_yeu_cau' => $jobData['kinh_nghiem_yeu_cau'],
                    'trinh_do_yeu_cau' => $jobData['trinh_do_yeu_cau'],
                    'ngay_het_han' => Carbon::now()->addDays(45),
                    'published_at' => now(),
                    'trang_thai' => 1,
                    'luot_xem' => 0,
                ]
            );

            $job->nganhNghes()->syncWithoutDetaching([$jobData['nganh']->id]);
        }

        $profiles = [
            [
                'tieu_de_ho_so' => 'Backend Laravel Developer',
                'muc_tieu_nghe_nghiep' => 'Tìm môi trường phát triển sản phẩm SaaS và API quy mô thực tế.',
                'trinh_do' => 'Đại học',
                'kinh_nghiem_nam' => 2,
                'mo_ta_ban_than' => 'Có kinh nghiệm Laravel, MySQL, REST API và triển khai module tuyển dụng.',
                'trang_thai' => 1,
            ],
            [
                'tieu_de_ho_so' => 'Frontend Vue Developer',
                'muc_tieu_nghe_nghiep' => 'Phát triển giao diện Vue 3, UX tốt và tối ưu hiệu năng.',
                'trinh_do' => 'Cao đẳng',
                'kinh_nghiem_nam' => 1,
                'mo_ta_ban_than' => 'Tập trung vào Vue.js, Tailwind CSS và trải nghiệm người dùng.',
                'trang_thai' => 1,
            ],
        ];

        $profileModels = [];

        foreach ($profiles as $profileData) {
            $profileModels[] = HoSo::query()->firstOrCreate(
                [
                    'nguoi_dung_id' => $candidate->id,
                    'tieu_de_ho_so' => $profileData['tieu_de_ho_so'],
                ],
                $profileData
            );
        }

        $skillMap = KyNang::query()
            ->whereIn('ten_ky_nang', ['Laravel', 'Vue.js', 'MySQL', 'REST API', 'Tailwind CSS'])
            ->get()
            ->keyBy('ten_ky_nang');

        $candidateSkills = [
            ['name' => 'Laravel', 'muc_do' => 4, 'nam_kinh_nghiem' => 2],
            ['name' => 'MySQL', 'muc_do' => 4, 'nam_kinh_nghiem' => 2],
            ['name' => 'REST API', 'muc_do' => 4, 'nam_kinh_nghiem' => 2],
            ['name' => 'Vue.js', 'muc_do' => 3, 'nam_kinh_nghiem' => 1],
            ['name' => 'Tailwind CSS', 'muc_do' => 3, 'nam_kinh_nghiem' => 1],
        ];

        foreach ($candidateSkills as $skillData) {
            $skill = $skillMap->get($skillData['name']);

            if (!$skill) {
                continue;
            }

            NguoiDungKyNang::query()->updateOrCreate(
                [
                    'nguoi_dung_id' => $candidate->id,
                    'ky_nang_id' => $skill->id,
                ],
                [
                    'muc_do' => $skillData['muc_do'],
                    'nam_kinh_nghiem' => $skillData['nam_kinh_nghiem'],
                    'so_chung_chi' => 1,
                ]
            );
        }

        $allJobs = TinTuyenDung::query()->with('congTy')->orderBy('id')->get();

        $candidate->tinDaLuus()->syncWithoutDetaching($allJobs->take(2)->pluck('id')->all());
        $candidate->congTyTheoDois()->syncWithoutDetaching([$company->id]);

        if (isset($profileModels[0])) {
            $application1 = UngTuyen::query()->updateOrCreate(
                [
                    'tin_tuyen_dung_id' => $allJobs[0]->id,
                    'ho_so_id' => $profileModels[0]->id,
                ],
                [
                    'trang_thai' => UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN,
                    'thu_xin_viec' => 'Tôi mong muốn đóng góp kinh nghiệm Laravel và tối ưu API cho đội ngũ.',
                    'thoi_gian_ung_tuyen' => now()->subDays(3),
                    'ngay_hen_phong_van' => now()->addDays(2),
                    'hinh_thuc_phong_van' => 'online',
                    'link_phong_van' => 'https://meet.google.com/demo-hoanglong',
                    'nguoi_phong_van' => 'HR Hoang Long',
                    'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_CHO_PHAN_HOI,
                    'da_rut_don' => false,
                ]
            );

            KetQuaMatching::query()->updateOrCreate(
                [
                    'ho_so_id' => $profileModels[0]->id,
                    'tin_tuyen_dung_id' => $allJobs[0]->id,
                    'model_version' => 'local-matching-v1',
                ],
                [
                    'diem_phu_hop' => 92,
                    'diem_ky_nang' => 94,
                    'diem_kinh_nghiem' => 88,
                    'diem_hoc_van' => 85,
                    'chi_tiet_diem' => ['skill_score' => 94, 'experience_score' => 88, 'education_score' => 85],
                    'matched_skills_json' => ['laravel', 'mysql', 'rest api'],
                    'missing_skills_json' => ['docker'],
                    'danh_sach_ky_nang_thieu' => 'docker',
                    'explanation' => 'Hồ sơ backend hiện tại có độ phù hợp cao với vị trí Laravel Developer.',
                    'thoi_gian_match' => now(),
                ]
            );

            TuVanNgheNghiep::query()->updateOrCreate(
                [
                    'nguoi_dung_id' => $candidate->id,
                    'ho_so_id' => $profileModels[0]->id,
                    'nghe_de_xuat' => 'Backend Developer',
                ],
                [
                    'muc_do_phu_hop' => 90,
                    'goi_y_ky_nang_bo_sung' => ['Docker', 'System Design', 'Testing'],
                    'bao_cao_chi_tiet' => 'Bạn phù hợp với hướng Backend Developer. Nên ưu tiên bổ sung Docker, System Design và kiểm thử tự động để tăng lợi thế.',
                    'model_version' => 'local-career-report-v1',
                ]
            );

            if (isset($allJobs[2])) {
                KetQuaMatching::query()->updateOrCreate(
                    [
                        'ho_so_id' => $profileModels[0]->id,
                        'tin_tuyen_dung_id' => $allJobs[2]->id,
                        'model_version' => 'local-matching-v1',
                    ],
                    [
                        'diem_phu_hop' => 81,
                        'diem_ky_nang' => 80,
                        'diem_kinh_nghiem' => 78,
                        'diem_hoc_van' => 82,
                        'chi_tiet_diem' => ['skill_score' => 80, 'experience_score' => 78, 'education_score' => 82],
                        'matched_skills_json' => ['laravel', 'vue.js'],
                        'missing_skills_json' => ['git workflow'],
                        'danh_sach_ky_nang_thieu' => 'git workflow',
                        'explanation' => 'Vị trí thực tập fullstack vẫn phù hợp nếu bạn muốn mở rộng thêm phần frontend.',
                        'thoi_gian_match' => now()->subHour(),
                    ]
                );
            }

            $application1->refresh();
        }

        if (isset($profileModels[1]) && isset($allJobs[1])) {
            UngTuyen::query()->updateOrCreate(
                [
                    'tin_tuyen_dung_id' => $allJobs[1]->id,
                    'ho_so_id' => $profileModels[1]->id,
                ],
                [
                    'trang_thai' => UngTuyen::TRANG_THAI_CHO_DUYET,
                    'thu_xin_viec' => 'Tôi muốn tham gia đội ngũ frontend để phát triển sản phẩm Vue 3 có trải nghiệm tốt.',
                    'thoi_gian_ung_tuyen' => now()->subDay(),
                    'da_rut_don' => false,
                ]
            );

            KetQuaMatching::query()->updateOrCreate(
                [
                    'ho_so_id' => $profileModels[1]->id,
                    'tin_tuyen_dung_id' => $allJobs[1]->id,
                    'model_version' => 'local-matching-v1',
                ],
                [
                    'diem_phu_hop' => 88,
                    'diem_ky_nang' => 90,
                    'diem_kinh_nghiem' => 76,
                    'diem_hoc_van' => 82,
                    'chi_tiet_diem' => ['skill_score' => 90, 'experience_score' => 76, 'education_score' => 82],
                    'matched_skills_json' => ['vue.js', 'tailwind css'],
                    'missing_skills_json' => ['typescript'],
                    'danh_sach_ky_nang_thieu' => 'typescript',
                    'explanation' => 'Hồ sơ frontend có nền tảng phù hợp với vị trí Vue Developer.',
                    'thoi_gian_match' => now()->subMinutes(30),
                ]
            );
        }
    }
}
