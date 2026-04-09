<?php

namespace Database\Seeders;

use App\Models\KyNang;
use Illuminate\Database\Seeder;

class KyNangSeeder extends Seeder
{
    /**
     * Seed dữ liệu bảng ky_nangs.
     *
     * Bảng catalog: Admin quản lý tên + mô tả + icon.
     * so_chung_chi và hinh_anh đã chuyển sang nguoi_dung_ky_nangs (ứng viên quản lý).
     */
    public function run(): void
    {
        $kyNangs = [
            // === Lập trình ===
            ['ten_ky_nang' => 'PHP', 'mo_ta' => 'Ngôn ngữ lập trình web phổ biến', 'icon' => 'fa-brands fa-php'],
            ['ten_ky_nang' => 'JavaScript', 'mo_ta' => 'Ngôn ngữ lập trình web phía client & server', 'icon' => 'fa-brands fa-js'],
            ['ten_ky_nang' => 'Python', 'mo_ta' => 'Ngôn ngữ đa năng, phổ biến trong AI/ML', 'icon' => 'fa-brands fa-python'],
            ['ten_ky_nang' => 'Java', 'mo_ta' => 'Ngôn ngữ OOP mạnh mẽ cho enterprise', 'icon' => 'fa-brands fa-java'],
            ['ten_ky_nang' => 'C#', 'mo_ta' => 'Ngôn ngữ lập trình .NET framework', 'icon' => 'fa-solid fa-code'],
            ['ten_ky_nang' => 'Go', 'mo_ta' => 'Ngôn ngữ của Google, hiệu năng cao', 'icon' => 'fa-solid fa-g'],
            ['ten_ky_nang' => 'TypeScript', 'mo_ta' => 'JavaScript với kiểu dữ liệu tĩnh', 'icon' => 'fa-solid fa-code'],
            ['ten_ky_nang' => 'Swift', 'mo_ta' => 'Ngôn ngữ phát triển iOS/macOS', 'icon' => 'fa-brands fa-swift'],
            ['ten_ky_nang' => 'Kotlin', 'mo_ta' => 'Ngôn ngữ phát triển Android', 'icon' => 'fa-solid fa-mobile-screen-button'],

            // === Framework ===
            ['ten_ky_nang' => 'Laravel', 'mo_ta' => 'PHP framework phổ biến nhất', 'icon' => 'fa-brands fa-laravel'],
            ['ten_ky_nang' => 'React', 'mo_ta' => 'Thư viện UI JavaScript của Meta', 'icon' => 'fa-brands fa-react'],
            ['ten_ky_nang' => 'Vue.js', 'mo_ta' => 'JavaScript framework linh hoạt', 'icon' => 'fa-brands fa-vuejs'],
            ['ten_ky_nang' => 'Angular', 'mo_ta' => 'Framework TypeScript của Google', 'icon' => 'fa-brands fa-angular'],
            ['ten_ky_nang' => 'Node.js', 'mo_ta' => 'Runtime JavaScript phía server', 'icon' => 'fa-brands fa-node-js'],
            ['ten_ky_nang' => 'Django', 'mo_ta' => 'Python web framework full-featured', 'icon' => 'fa-solid fa-server'],
            ['ten_ky_nang' => 'Spring Boot', 'mo_ta' => 'Java framework cho microservices', 'icon' => 'fa-solid fa-leaf'],
            ['ten_ky_nang' => 'Flutter', 'mo_ta' => 'Framework cross-platform của Google', 'icon' => 'fa-solid fa-mobile-screen'],
            ['ten_ky_nang' => 'React Native', 'mo_ta' => 'Framework mobile cross-platform', 'icon' => 'fa-brands fa-react'],
            ['ten_ky_nang' => 'Next.js', 'mo_ta' => 'React framework full-stack', 'icon' => 'fa-solid fa-n'],

            // === Database ===
            ['ten_ky_nang' => 'MySQL', 'mo_ta' => 'Hệ quản trị CSDL quan hệ phổ biến', 'icon' => 'fa-solid fa-database'],
            ['ten_ky_nang' => 'PostgreSQL', 'mo_ta' => 'CSDL quan hệ mã nguồn mở mạnh mẽ', 'icon' => 'fa-solid fa-database'],
            ['ten_ky_nang' => 'MongoDB', 'mo_ta' => 'CSDL NoSQL hướng document', 'icon' => 'fa-solid fa-leaf'],
            ['ten_ky_nang' => 'Redis', 'mo_ta' => 'In-memory data store, cache', 'icon' => 'fa-solid fa-memory'],

            // === DevOps / Cloud ===
            ['ten_ky_nang' => 'Docker', 'mo_ta' => 'Containerization platform', 'icon' => 'fa-brands fa-docker'],
            ['ten_ky_nang' => 'Kubernetes', 'mo_ta' => 'Container orchestration', 'icon' => 'fa-solid fa-dharmachakra'],
            ['ten_ky_nang' => 'AWS', 'mo_ta' => 'Amazon Web Services - Cloud platform', 'icon' => 'fa-brands fa-aws'],
            ['ten_ky_nang' => 'Azure', 'mo_ta' => 'Microsoft Cloud platform', 'icon' => 'fa-brands fa-microsoft'],
            ['ten_ky_nang' => 'CI/CD', 'mo_ta' => 'Tích hợp và triển khai liên tục', 'icon' => 'fa-solid fa-arrows-rotate'],
            ['ten_ky_nang' => 'Git', 'mo_ta' => 'Hệ thống quản lý phiên bản', 'icon' => 'fa-brands fa-git-alt'],
            ['ten_ky_nang' => 'Linux', 'mo_ta' => 'Hệ điều hành mã nguồn mở', 'icon' => 'fa-brands fa-linux'],

            // === Khác ===
            ['ten_ky_nang' => 'Figma', 'mo_ta' => 'Công cụ thiết kế UI/UX', 'icon' => 'fa-brands fa-figma'],
            ['ten_ky_nang' => 'Adobe Photoshop', 'mo_ta' => 'Phần mềm chỉnh sửa ảnh chuyên nghiệp', 'icon' => 'fa-solid fa-image'],
            ['ten_ky_nang' => 'SEO', 'mo_ta' => 'Tối ưu hoá công cụ tìm kiếm', 'icon' => 'fa-solid fa-magnifying-glass'],
            ['ten_ky_nang' => 'Google Ads', 'mo_ta' => 'Quảng cáo trực tuyến Google', 'icon' => 'fa-brands fa-google'],
            ['ten_ky_nang' => 'Microsoft Excel', 'mo_ta' => 'Bảng tính và phân tích dữ liệu', 'icon' => 'fa-solid fa-file-excel'],
            ['ten_ky_nang' => 'Tiếng Anh', 'mo_ta' => 'Ngôn ngữ quốc tế', 'icon' => 'fa-solid fa-language'],
            ['ten_ky_nang' => 'Tiếng Nhật', 'mo_ta' => 'Ngôn ngữ Nhật Bản', 'icon' => 'fa-solid fa-language'],
            ['ten_ky_nang' => 'Quản lý dự án (PMP)', 'mo_ta' => 'Quản lý dự án chuyên nghiệp', 'icon' => 'fa-solid fa-list-check'],
            ['ten_ky_nang' => 'Agile / Scrum', 'mo_ta' => 'Phương pháp phát triển phần mềm linh hoạt', 'icon' => 'fa-solid fa-person-running'],
            ['ten_ky_nang' => 'REST API', 'mo_ta' => 'Thiết kế & phát triển API RESTful', 'icon' => 'fa-solid fa-link'],
        ];

        foreach ($kyNangs as $kn) {
            KyNang::create($kn);
        }

        $this->command->info('✅ KyNangSeeder: Đã tạo ' . count($kyNangs) . ' kỹ năng thành công!');
    }
}
