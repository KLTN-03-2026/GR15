<?php

namespace Database\Seeders;

use App\Models\HoSo;
use App\Models\NguoiDung;
use Illuminate\Database\Seeder;

class HoSoSeeder extends Seeder
{
    /**
     * Seed dữ liệu bảng ho_sos.
     *
     * Tạo:
     *  - 2 hồ sơ cố định cho ứng viên 1 (ID 4 - Phạm Văn An)
     *  - 1 hồ sơ cố định cho ứng viên 2 (ID 5 - Lê Thị Bình)
     *  - 1 hồ sơ ẩn cho ứng viên 1 (để test trạng thái)
     *  - 5 hồ sơ ngẫu nhiên bằng Factory
     */
    public function run(): void
    {
        // =========================================
        // HỒ SƠ CỐ ĐỊNH - Ứng viên 1 (Phạm Văn An)
        // =========================================
        $ungVien1 = NguoiDung::where('email', 'ung.vien1@kltn.com')->first();

        if ($ungVien1) {
            HoSo::create([
                'nguoi_dung_id' => $ungVien1->id,
                'tieu_de_ho_so' => 'Hồ sơ Backend Developer',
                'muc_tieu_nghe_nghiep' => 'Mong muốn ứng tuyển vào vị trí lập trình viên Backend tại công ty công nghệ hàng đầu Việt Nam. Có kinh nghiệm làm việc với Laravel, Node.js, và PostgreSQL.',
                'trinh_do' => 'dai_hoc',
                'kinh_nghiem_nam' => 2,
                'mo_ta_ban_than' => 'Tôi là một lập trình viên đam mê công nghệ, luôn cập nhật kiến thức mới. Có khả năng làm việc nhóm tốt và chịu được áp lực công việc cao.',
                'file_cv' => null,
                'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
            ]);

            HoSo::create([
                'nguoi_dung_id' => $ungVien1->id,
                'tieu_de_ho_so' => 'Hồ sơ Full-stack Developer',
                'muc_tieu_nghe_nghiep' => 'Tìm kiếm cơ hội phát triển sự nghiệp toàn diện với cả Frontend và Backend. Thành thạo React, Vue.js, Laravel.',
                'trinh_do' => 'dai_hoc',
                'kinh_nghiem_nam' => 2,
                'mo_ta_ban_than' => 'Yêu thích cả Frontend lẫn Backend, muốn trở thành Full-stack Developer chuyên nghiệp.',
                'file_cv' => null,
                'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
            ]);

            // Hồ sơ ẩn (để test trạng thái)
            HoSo::create([
                'nguoi_dung_id' => $ungVien1->id,
                'tieu_de_ho_so' => 'Hồ sơ cũ (đã ẩn)',
                'muc_tieu_nghe_nghiep' => 'Hồ sơ cũ không còn sử dụng.',
                'trinh_do' => 'cao_dang',
                'kinh_nghiem_nam' => 0,
                'mo_ta_ban_than' => 'Hồ sơ tạm ẩn.',
                'file_cv' => null,
                'trang_thai' => HoSo::TRANG_THAI_AN,
            ]);
        }

        // =========================================
        // HỒ SƠ CỐ ĐỊNH - Ứng viên 2 (Lê Thị Bình)
        // =========================================
        $ungVien2 = NguoiDung::where('email', 'ung.vien2@kltn.com')->first();

        if ($ungVien2) {
            HoSo::create([
                'nguoi_dung_id' => $ungVien2->id,
                'tieu_de_ho_so' => 'Hồ sơ UI/UX Designer',
                'muc_tieu_nghe_nghiep' => 'Theo đuổi đam mê thiết kế giao diện người dùng. Mong muốn làm việc tại agency hoặc product company.',
                'trinh_do' => 'dai_hoc',
                'kinh_nghiem_nam' => 1,
                'mo_ta_ban_than' => 'Sáng tạo, tỉ mỉ, có eye for detail. Thành thạo Figma, Adobe XD, Sketch.',
                'file_cv' => null,
                'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
            ]);
        }

        // =========================================
        // DỮ LIỆU NGẪU NHIÊN bằng Factory
        // =========================================
        // Lấy danh sách ứng viên active để gán hồ sơ
        $ungViens = NguoiDung::where('vai_tro', NguoiDung::VAI_TRO_UNG_VIEN)
            ->where('trang_thai', 1)
            ->pluck('id');

        foreach ($ungViens->take(5) as $uvId) {
            HoSo::factory()->forNguoiDung($uvId)->create();
        }

        // Thêm 2 hồ sơ ẩn ngẫu nhiên
        if ($ungViens->count() >= 2) {
            HoSo::factory()->forNguoiDung($ungViens->random())->an()->create();
            HoSo::factory()->forNguoiDung($ungViens->random())->an()->create();
        }

        $this->command->info('✅ HoSoSeeder: Đã tạo dữ liệu thành công!');
        $this->command->table(
            ['Loại', 'Số lượng'],
            [
                ['Hồ sơ cố định (UV1 - ung.vien1@kltn.com)', '3 (2 công khai + 1 ẩn)'],
                ['Hồ sơ cố định (UV2 - ung.vien2@kltn.com)', '1 (công khai)'],
                ['Hồ sơ ngẫu nhiên (công khai)', '5'],
                ['Hồ sơ ngẫu nhiên (ẩn)', '2'],
                ['Tổng cộng', '~11'],
            ]
        );
    }
}
