<?php

namespace Database\Seeders;

use App\Models\HoSo;
use App\Models\TuVanNgheNghiep;
use Illuminate\Database\Seeder;

class TuVanNgheNghiepSeeder extends Seeder
{
    public function run(): void
    {
        $hoSos = HoSo::all();

        if ($hoSos->isEmpty()) {
            return;
        }

        // Định hướng nghề nghiệp ngẫu nhiên
        $jobs = [
            ['nghe_de_xuat' => 'Lập trình viên Backend (PHP/Laravel)', 'skills' => 'Docker, CI/CD, Redis, Kiến trúc Microservices'],
            ['nghe_de_xuat' => 'Chuyên viên Phân tích Dữ liệu (Data Analyst)', 'skills' => 'Python, Pandas, SQL Server nâng cao, Tableau'],
            ['nghe_de_xuat' => 'Kỹ sư Cầu nối (BrSE)', 'skills' => 'Tiếng Nhật (N2), CMMI, Kỹ năng Đàm phán'],
            ['nghe_de_xuat' => 'Chuyên viên An toàn thông tin (Cyber Security)', 'skills' => 'CEH, Pentest, Mạng máy tính nâng cao'],
        ];

        // Lấy User mẫu phục vụ việc Login & Demo
        $uv1 = $hoSos->filter(fn($hs) => $hs->nguoiDung->email === 'ung.vien1@kltn.com');
        $uv2 = $hoSos->filter(fn($hs) => $hs->nguoiDung->email === 'ung.vien2@kltn.com');

        $targetCvs = $uv1->concat($uv2);

        if ($targetCvs->isEmpty()) {
            $targetCvs = $hoSos->random(min(5, $hoSos->count()));
        }

        foreach ($targetCvs as $hoSo) {
            // Lấy 1 hoặc 2 lời khuyên
            $advices = collect($jobs)->random(rand(1, 2));

            foreach ($advices as $adv) {
                // Kiểm tra trùng lặp
                $exists = TuVanNgheNghiep::where('nguoi_dung_id', $hoSo->nguoi_dung_id)
                    ->where('nghe_de_xuat', $adv['nghe_de_xuat'])
                    ->exists();

                if (!$exists) {
                    TuVanNgheNghiep::create([
                        'nguoi_dung_id' => $hoSo->nguoi_dung_id,
                        'ho_so_id' => $hoSo->id,
                        'nghe_de_xuat' => $adv['nghe_de_xuat'],
                        'muc_do_phu_hop' => rand(65, 95) + (rand(0, 99) / 100), // VD: 85.50
                        'goi_y_ky_nang_bo_sung' => $adv['skills'],
                        'created_at' => now()->subDays(rand(0, 7)),
                    ]);
                }
            }
        }
        
        echo "✅ TuVanNgheNghiepSeeder: Báo cáo Tư Vấn (AI) đã được tạo cho Ứng viên!\n";
    }
}
