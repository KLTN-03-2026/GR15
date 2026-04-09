<?php

namespace Database\Seeders;

use App\Models\NganhNghe;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;

class NganhNgheSeeder extends Seeder
{
    /**
     * Seed dữ liệu bảng nganh_nghes.
     *
     * Cấu trúc 2 cấp:
     *   Ngành gốc (danh_muc_cha_id = null)
     *     └── Ngành con
     */
    public function run(): void
    {
        // =========================================
        // NGÀNH GỐC + NGÀNH CON (Dữ liệu cố định)
        // =========================================
        $danhMuc = [
            [
                'ten_nganh' => 'Công nghệ thông tin',
                'icon' => 'fa-solid fa-laptop-code',
                'mo_ta' => 'Lĩnh vực công nghệ thông tin, phần mềm, hệ thống.',
                'con' => [
                    ['ten_nganh' => 'Lập trình Backend', 'icon' => 'fa-solid fa-server', 'mo_ta' => 'PHP, Java, Node.js, Python, Go...'],
                    ['ten_nganh' => 'Lập trình Frontend', 'icon' => 'fa-solid fa-code', 'mo_ta' => 'React, Vue.js, Angular, HTML/CSS...'],
                    ['ten_nganh' => 'Lập trình Mobile', 'icon' => 'fa-solid fa-mobile-screen-button', 'mo_ta' => 'iOS, Android, Flutter, React Native...'],
                    ['ten_nganh' => 'DevOps / SysAdmin', 'icon' => 'fa-solid fa-gears', 'mo_ta' => 'Docker, Kubernetes, CI/CD, Linux...'],
                    ['ten_nganh' => 'Kiểm thử phần mềm (QA)', 'icon' => 'fa-solid fa-bug', 'mo_ta' => 'Manual Testing, Automation, Performance...'],
                    ['ten_nganh' => 'Phân tích dữ liệu', 'icon' => 'fa-solid fa-chart-line', 'mo_ta' => 'Data Analysis, BI, SQL, Python...'],
                ],
            ],
            [
                'ten_nganh' => 'Kinh doanh / Bán hàng',
                'icon' => 'fa-solid fa-sack-dollar',
                'mo_ta' => 'Lĩnh vực kinh doanh, thương mại, bán hàng.',
                'con' => [
                    ['ten_nganh' => 'Nhân viên kinh doanh', 'icon' => 'fa-solid fa-handshake', 'mo_ta' => 'B2B, B2C, telesales...'],
                    ['ten_nganh' => 'Quản lý bán hàng', 'icon' => 'fa-solid fa-list-check', 'mo_ta' => 'Sales Manager, Key Account...'],
                    ['ten_nganh' => 'Thương mại điện tử', 'icon' => 'fa-solid fa-cart-shopping', 'mo_ta' => 'E-commerce, Shopee, Lazada...'],
                ],
            ],
            [
                'ten_nganh' => 'Marketing / Truyền thông',
                'icon' => 'fa-solid fa-bullhorn',
                'mo_ta' => 'Lĩnh vực marketing, quảng cáo, truyền thông.',
                'con' => [
                    ['ten_nganh' => 'Digital Marketing', 'icon' => 'fa-solid fa-globe', 'mo_ta' => 'SEO, SEM, Social Media, Google Ads...'],
                    ['ten_nganh' => 'Content Marketing', 'icon' => 'fa-solid fa-pen-nib', 'mo_ta' => 'Copywriting, Content Strategy...'],
                    ['ten_nganh' => 'Thiết kế đồ hoạ', 'icon' => 'fa-solid fa-palette', 'mo_ta' => 'Photoshop, Illustrator, Figma...'],
                ],
            ],
            [
                'ten_nganh' => 'Kế toán / Tài chính',
                'icon' => 'fa-solid fa-building-columns',
                'mo_ta' => 'Lĩnh vực kế toán, kiểm toán, tài chính, ngân hàng.',
                'con' => [
                    ['ten_nganh' => 'Kế toán tổng hợp', 'icon' => 'fa-solid fa-book', 'mo_ta' => 'Kế toán nội bộ, thuế, báo cáo...'],
                    ['ten_nganh' => 'Tài chính doanh nghiệp', 'icon' => 'fa-solid fa-money-bill-trend-up', 'mo_ta' => 'Corporate Finance, FP&A...'],
                ],
            ],
            [
                'ten_nganh' => 'Nhân sự / Hành chính',
                'icon' => 'fa-solid fa-users',
                'mo_ta' => 'Lĩnh vực nhân sự, tuyển dụng, đào tạo, hành chính.',
                'con' => [
                    ['ten_nganh' => 'Tuyển dụng (Recruiter)', 'icon' => 'fa-solid fa-magnifying-glass', 'mo_ta' => 'Headhunter, In-house Recruiter...'],
                    ['ten_nganh' => 'Đào tạo & Phát triển', 'icon' => 'fa-solid fa-book-open-reader', 'mo_ta' => 'Training, L&D, OD...'],
                ],
            ],
            [
                'ten_nganh' => 'Giáo dục / Đào tạo',
                'icon' => 'fa-solid fa-graduation-cap',
                'mo_ta' => 'Lĩnh vực giáo dục, giảng dạy, nghiên cứu.',
                'con' => [
                    ['ten_nganh' => 'Giảng viên / Giáo viên', 'icon' => 'fa-solid fa-chalkboard-user', 'mo_ta' => 'Giảng dạy tại trường, trung tâm...'],
                    ['ten_nganh' => 'Gia sư / Dạy kèm', 'icon' => 'fa-solid fa-book-open', 'mo_ta' => 'Dạy kèm, gia sư online/offline...'],
                ],
            ],
            [
                'ten_nganh' => 'Y tế / Sức khoẻ',
                'icon' => 'fa-solid fa-hospital',
                'mo_ta' => 'Lĩnh vực chăm sóc sức khoẻ, y tế, dược phẩm.',
                'con' => [],
            ],
            [
                'ten_nganh' => 'Xây dựng / Bất động sản',
                'icon' => 'fa-solid fa-compass-drafting',
                'mo_ta' => 'Lĩnh vực xây dựng, kiến trúc, bất động sản.',
                'con' => [],
            ],
        ];

        $tongGoc = 0;
        $tongCon = 0;

        foreach ($danhMuc as $goc) {
            $nganhGoc = NganhNghe::create([
                'ten_nganh' => $goc['ten_nganh'],
                'slug' => Str::slug($goc['ten_nganh']),
                'mo_ta' => $goc['mo_ta'],
                'danh_muc_cha_id' => null,
                'icon' => $goc['icon'],
                'trang_thai' => NganhNghe::TRANG_THAI_HIEN_THI,
            ]);
            $tongGoc++;

            foreach ($goc['con'] as $con) {
                NganhNghe::create([
                    'ten_nganh' => $con['ten_nganh'],
                    'slug' => Str::slug($con['ten_nganh']),
                    'mo_ta' => $con['mo_ta'],
                    'danh_muc_cha_id' => $nganhGoc->id,
                    'icon' => $con['icon'],
                    'trang_thai' => NganhNghe::TRANG_THAI_HIEN_THI,
                ]);
                $tongCon++;
            }
        }

        // Tạo 1 ngành bị ẩn (để test)
        NganhNghe::create([
            'ten_nganh' => 'Ngành test (ẩn)',
            'slug' => 'nganh-test-an',
            'mo_ta' => 'Ngành nghề tạm ẩn để test.',
            'danh_muc_cha_id' => null,
            'icon' => 'fa-solid fa-ban',
            'trang_thai' => NganhNghe::TRANG_THAI_AN,
        ]);
        $tongGoc++;

        $this->command->info('✅ NganhNgheSeeder: Đã tạo dữ liệu thành công!');
        $this->command->table(
            ['Loại', 'Số lượng'],
            [
                ['Ngành gốc (hiển thị)', $tongGoc - 1],
                ['Ngành gốc (ẩn)', '1'],
                ['Ngành con', $tongCon],
                ['Tổng cộng', $tongGoc + $tongCon],
            ]
        );
    }
}
