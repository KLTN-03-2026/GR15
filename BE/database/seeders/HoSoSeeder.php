<?php

namespace Database\Seeders;

use App\Models\HoSo;
use App\Models\NguoiDung;
use Illuminate\Database\Seeder;

class HoSoSeeder extends Seeder
{
    /**
     * Seed dữ liệu hồ sơ theo chân dung ứng viên cụ thể.
     */
    public function run(): void
    {
        $mauHoSoTheoEmail = [
            'ung.vien1@kltn.com' => [
                [
                    'tieu_de_ho_so' => 'Backend Developer Laravel/PHP',
                    'muc_tieu_nghe_nghiep' => 'Tìm kiếm cơ hội làm Backend Developer trong môi trường product, tham gia xây dựng API ổn định, tối ưu hiệu năng và từng bước phát triển lên vị trí Senior trong 2 năm tới.',
                    'trinh_do' => 'dai_hoc',
                    'kinh_nghiem_nam' => 3,
                    'mo_ta_ban_than' => 'Có kinh nghiệm phát triển hệ thống quản lý bán hàng và CRM nội bộ bằng Laravel, MySQL, Redis. Quen làm việc với Git, Docker, viết tài liệu API và phối hợp chặt chẽ với frontend.',
                    'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
                ],
                [
                    'tieu_de_ho_so' => 'Full-stack Developer cho doanh nghiệp SME',
                    'muc_tieu_nghe_nghiep' => 'Muốn làm việc ở đội ngũ nhỏ nơi có thể tham gia cả backend lẫn frontend, chịu trách nhiệm xuyên suốt từ phân tích yêu cầu đến triển khai và hỗ trợ vận hành.',
                    'trinh_do' => 'dai_hoc',
                    'kinh_nghiem_nam' => 3,
                    'mo_ta_ban_than' => 'Từng tham gia dự án xây landing page, dashboard quản trị và các module báo cáo. Có thể đọc hiểu yêu cầu nghiệp vụ, xây REST API và xử lý bug production.',
                    'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
                ],
                [
                    'tieu_de_ho_so' => 'Junior PHP Developer',
                    'muc_tieu_nghe_nghiep' => 'Hồ sơ cũ phục vụ cho giai đoạn tìm việc đầu tiên sau khi ra trường.',
                    'trinh_do' => 'cao_dang',
                    'kinh_nghiem_nam' => 1,
                    'mo_ta_ban_than' => 'Tập trung vào kỹ năng nền tảng PHP, HTML/CSS và MySQL.',
                    'trang_thai' => HoSo::TRANG_THAI_AN,
                ],
            ],
            'ung.vien2@kltn.com' => [
                [
                    'tieu_de_ho_so' => 'UI/UX Designer cho sản phẩm số',
                    'muc_tieu_nghe_nghiep' => 'Mong muốn đồng hành cùng đội sản phẩm để cải thiện trải nghiệm người dùng, chuẩn hóa design system và tạo ra luồng sử dụng mượt mà trên web/mobile.',
                    'trinh_do' => 'dai_hoc',
                    'kinh_nghiem_nam' => 2,
                    'mo_ta_ban_than' => 'Thành thạo Figma, wireframe, prototype, làm việc với developer để handoff thiết kế. Có kinh nghiệm nghiên cứu người dùng cơ bản, audit giao diện và cải thiện conversion cho landing page.',
                    'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
                ],
                [
                    'tieu_de_ho_so' => 'Frontend Developer Vue/React',
                    'muc_tieu_nghe_nghiep' => 'Định hướng trở thành frontend engineer có nền tảng UX tốt, ưu tiên các dự án SaaS hoặc thương mại điện tử.',
                    'trinh_do' => 'dai_hoc',
                    'kinh_nghiem_nam' => 2,
                    'mo_ta_ban_than' => 'Có thể cắt giao diện responsive từ Figma, làm việc với Vue.js, React, TypeScript ở mức khá và phối hợp test UI trên nhiều trình duyệt.',
                    'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
                ],
            ],
            'ung.vien3@kltn.com' => [
                [
                    'tieu_de_ho_so' => 'Data Analyst BI',
                    'muc_tieu_nghe_nghiep' => 'Tìm vị trí Data Analyst nơi có thể khai thác dữ liệu kinh doanh, xây dashboard và hỗ trợ các phòng ban ra quyết định dựa trên số liệu.',
                    'trinh_do' => 'dai_hoc',
                    'kinh_nghiem_nam' => 4,
                    'mo_ta_ban_than' => 'Thường xuyên làm việc với SQL, Excel nâng cao, Power BI và Python để tổng hợp, làm sạch dữ liệu và trực quan hóa chỉ số vận hành.',
                    'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
                ],
            ],
            'ung.vien4@kltn.com' => [
                [
                    'tieu_de_ho_so' => 'Digital Marketing Executive',
                    'muc_tieu_nghe_nghiep' => 'Mong muốn phát triển theo hướng performance marketing, quản lý ngân sách quảng cáo hiệu quả và tối ưu phễu chuyển đổi cho doanh nghiệp thương mại điện tử.',
                    'trinh_do' => 'dai_hoc',
                    'kinh_nghiem_nam' => 2,
                    'mo_ta_ban_than' => 'Có kinh nghiệm chạy Facebook Ads, Google Ads, phối hợp content và thiết kế để triển khai chiến dịch, theo dõi ROAS và báo cáo hàng tuần.',
                    'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
                ],
            ],
            'ung.vien5@kltn.com' => [
                [
                    'tieu_de_ho_so' => 'QA Engineer Manual/Automation',
                    'muc_tieu_nghe_nghiep' => 'Tìm cơ hội kiểm thử phần mềm trong môi trường agile, từng bước mở rộng sang automation test cho web app và API.',
                    'trinh_do' => 'dai_hoc',
                    'kinh_nghiem_nam' => 5,
                    'mo_ta_ban_than' => 'Có kinh nghiệm viết test case, test plan, kiểm thử hồi quy, kiểm thử API bằng Postman và phối hợp với BA, developer để xác minh lỗi.',
                    'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
                ],
            ],
        ];

        $soHoSoCoDinh = 0;

        foreach ($mauHoSoTheoEmail as $email => $danhSachHoSo) {
            $ungVien = NguoiDung::where('email', $email)->first();
            if (!$ungVien) {
                continue;
            }

            foreach ($danhSachHoSo as $hoSo) {
                HoSo::create([
                    'nguoi_dung_id' => $ungVien->id,
                    'tieu_de_ho_so' => $hoSo['tieu_de_ho_so'],
                    'muc_tieu_nghe_nghiep' => $hoSo['muc_tieu_nghe_nghiep'],
                    'trinh_do' => $hoSo['trinh_do'],
                    'kinh_nghiem_nam' => $hoSo['kinh_nghiem_nam'],
                    'mo_ta_ban_than' => $hoSo['mo_ta_ban_than'],
                    'file_cv' => null,
                    'trang_thai' => $hoSo['trang_thai'],
                ]);
                $soHoSoCoDinh++;
            }
        }

        $ungVienConLai = NguoiDung::where('vai_tro', NguoiDung::VAI_TRO_UNG_VIEN)
            ->where('trang_thai', 1)
            ->whereNotIn('email', array_keys($mauHoSoTheoEmail))
            ->get();

        foreach ($ungVienConLai as $ungVien) {
            HoSo::factory()->forNguoiDung($ungVien->id)->create();

            if (rand(0, 100) > 60) {
                HoSo::factory()->forNguoiDung($ungVien->id)->an()->create();
            }
        }

        $this->command->info('✅ HoSoSeeder: Đã tạo hồ sơ với nội dung gần với ứng viên thực tế.');
        $this->command->table(
            ['Loại', 'Số lượng'],
            [
                ['Hồ sơ cố định theo persona', (string) $soHoSoCoDinh],
                ['Hồ sơ sinh thêm bằng factory', (string) ($ungVienConLai->count())],
                ['Hồ sơ ẩn phát sinh thêm', 'Ngẫu nhiên theo từng ứng viên'],
            ]
        );
    }
}
