<?php

namespace Database\Seeders;

use App\Models\CongTy;
use App\Models\NganhNghe;
use App\Models\TinTuyenDung;
use Illuminate\Database\Seeder;
use Carbon\Carbon;

class TinTuyenDungSeeder extends Seeder
{
    public function run(): void
    {
        $congTys = CongTy::all();
        $nganhNghes = NganhNghe::all();

        if ($congTys->isEmpty() || $nganhNghes->isEmpty()) {
            return;
        }

        $mauTin = [
            [
                'tieu_de' => 'Lập trình viên PHP/Laravel (Senior)',
                'mo_ta_cong_viec' => "Phát triển các ứng dụng web phức tạp sử dụng Laravel framework.\nTham gia phân tích thiết kế hệ thống, review code.\nTối ưu hóa hiệu năng, bảo mật cho ứng dụng.",
                'dia_diem_lam_viec' => 'Quận 1, TP.HCM',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Senior',
                'so_luong_tuyen' => 2,
                'muc_luong' => 30000000,
                'kinh_nghiem_yeu_cau' => '3 - 5 năm',
                'ngay_het_han' => Carbon::now()->addDays(30),
            ],
            [
                'tieu_de' => 'Chuyên viên Marketing Digital',
                'mo_ta_cong_viec' => "Lên kế hoạch và triển khai các chiến dịch quảng cáo Facebook, Google.\nPhân tích dữ liệu, tối ưu hóa ROI.\nQuản lý đội ngũ content creator.",
                'dia_diem_lam_viec' => 'Hà Nội',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Trưởng nhóm',
                'so_luong_tuyen' => 1,
                'muc_luong' => 25000000,
                'kinh_nghiem_yeu_cau' => '2 - 3 năm',
                'ngay_het_han' => Carbon::now()->addDays(15),
            ],
            [
                'tieu_de' => 'Thực tập sinh Frontend (ReactJS)',
                'mo_ta_cong_viec' => "Hỗ trợ cắt HTML/CSS từ file thiết kế Figma.\nTham gia phát triển các UI components bằng ReactJS.\nĐược đào tạo và làm việc trực tiếp với các anh chị Senior.",
                'dia_diem_lam_viec' => 'Đà Nẵng',
                'hinh_thuc_lam_viec' => 'Thực tập',
                'cap_bac' => 'Thực tập sinh',
                'so_luong_tuyen' => 5,
                'muc_luong' => 5000000,
                'kinh_nghiem_yeu_cau' => 'Không yêu cầu',
                'ngay_het_han' => Carbon::now()->addDays(45),
            ],
            [
                'tieu_de' => 'Nhân viên Tuyển dụng (HR)',
                'mo_ta_cong_viec' => "Tìm kiếm, sàng lọc hồ sơ ứng viên trên các nền tảng.\nTổ chức phỏng vấn, đánh giá ứng viên.\nXây dựng văn hóa doanh nghiệp.",
                'dia_diem_lam_viec' => 'Quận 7, TP.HCM',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 2,
                'muc_luong' => 12000000,
                'kinh_nghiem_yeu_cau' => '1 - 2 năm',
                'ngay_het_han' => Carbon::now()->addDays(10),
            ],
            [
                'tieu_de' => 'Data Analyst',
                'mo_ta_cong_viec' => "Phân tích dữ liệu kinh doanh.\nXây dựng dashboard báo cáo.\nĐưa ra insights hỗ trợ ban giám đốc.",
                'dia_diem_lam_viec' => 'Remote',
                'hinh_thuc_lam_viec' => 'Remote',
                'cap_bac' => 'Chuyên viên',
                'so_luong_tuyen' => 1,
                'muc_luong' => 45000000,
                'kinh_nghiem_yeu_cau' => 'Trên 5 năm',
                'ngay_het_han' => Carbon::now()->subDays(5), // Tin đã hết hạn
            ],
            [
                'tieu_de' => 'Thiết kế đồ họa (Designer)',
                'mo_ta_cong_viec' => "Thiết kế ấn phẩm truyền thông (banner, poster).\nHỗ trợ thiết kế giao diện UI/UX.\nChỉnh sửa video cơ bản.",
                'dia_diem_lam_viec' => 'Quận 3, TP.HCM',
                'hinh_thuc_lam_viec' => 'Bán thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 3,
                'muc_luong' => 8000000,
                'kinh_nghiem_yeu_cau' => 'Dưới 1 năm',
                'ngay_het_han' => Carbon::now()->addDays(20),
            ]
        ];

        // Tạo 6 tin cho công ty đầu tiên (để có đủ case test)
        $congTy1 = $congTys->first();
        foreach ($mauTin as $index => $tin) {
            $record = TinTuyenDung::create(array_merge($tin, [
                'cong_ty_id' => $congTy1->id,
                'trang_thai' => $index == 4 ? 0 : 1, // Tin Data Analyst bị tạm ngưng
                'luot_xem' => rand(10, 500)
            ]));
            
            // Random gắn 1-2 ngành nghề
            $record->nganhNghes()->attach($nganhNghes->random(rand(1, 2))->pluck('id'));
        }

        // Tạo 15 tin ngẫu nhiên cho các công ty còn lại
        for ($i = 0; $i < 15; $i++) {
            $cty = $congTys->random();
            $record = TinTuyenDung::create([
                'tieu_de' => 'Cần tuyển vị trí số ' . ($i + 1),
                'mo_ta_cong_viec' => 'Mô tả công việc chung mẫu...',
                'dia_diem_lam_viec' => ['TP.HCM', 'Hà Nội', 'Đà Nẵng', 'Cần Thơ'][rand(0, 3)],
                'hinh_thuc_lam_viec' => TinTuyenDung::HINH_THUC_LIST[array_rand(TinTuyenDung::HINH_THUC_LIST)],
                'cap_bac' => ['Nhân viên', 'Quản lý', 'Thực tập sinh'][rand(0, 2)],
                'so_luong_tuyen' => rand(1, 5),
                'muc_luong' => rand(5, 30) * 1000000,
                'kinh_nghiem_yeu_cau' => rand(1, 4) . ' năm',
                'ngay_het_han' => rand(0, 1) ? Carbon::now()->addDays(rand(5, 60)) : Carbon::now()->subDays(rand(1, 10)),
                'cong_ty_id' => $cty->id,
                'trang_thai' => rand(0, 10) > 2 ? 1 : 0, // 80% hoạt động
                'luot_xem' => rand(0, 100)
            ]);
            $record->nganhNghes()->attach($nganhNghes->random(rand(1, 3))->pluck('id'));
        }

        echo "✅ TinTuyenDungSeeder: Đã tạo 21 tin tuyển dụng mẫu!\n";
    }
}
