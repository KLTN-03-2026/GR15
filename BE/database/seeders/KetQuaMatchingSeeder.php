<?php

namespace Database\Seeders;

use App\Models\HoSo;
use App\Models\KetQuaMatching;
use App\Models\TinTuyenDung;
use Illuminate\Database\Seeder;

class KetQuaMatchingSeeder extends Seeder
{
    public function run(): void
    {
        $hoSos = HoSo::all();
        $tins = TinTuyenDung::where('trang_thai', 1)->get();

        if ($hoSos->isEmpty() || $tins->isEmpty()) {
            return;
        }

        // Tạo mảng mô phỏng lý do chấm điểm JSON
        $reasons = [
            'ky_nang_hop' => ['PHP', 'Laravel', 'MySQL'],
            'ky_nang_khong_hop' => ['AWS'],
            'muc_luong_hop' => true,
            'so_nam_kn_hop_tuong_doi' => false
        ];

        // Lấy riêng 2 user mẫu (nếu tồn tại) để tập trung Test UI
        $uv1 = $hoSos->filter(fn($hs) => $hs->nguoiDung->email === 'ung.vien1@kltn.com');
        $uv2 = $hoSos->filter(fn($hs) => $hs->nguoiDung->email === 'ung.vien2@kltn.com');

        $targetCVs = $uv1->concat($uv2);

        // Nếu không có 2 user này, lấy toàn bộ
        if ($targetCVs->isEmpty()) {
            $targetCVs = $hoSos;
        }

        foreach ($targetCVs as $hoSo) {
            // Pick ngẫu nhiên 3-5 tin cho mỗi CV
            $soLuongTin = rand(3, 5);
            $tinsDeMatch = $tins->random(min($soLuongTin, $tins->count()));

            foreach ($tinsDeMatch as $tin) {
                // Đảm bảo unique
                $exists = KetQuaMatching::where('ho_so_id', $hoSo->id)
                    ->where('tin_tuyen_dung_id', $tin->id)
                    ->exists();

                if (!$exists) {
                    $diem = rand(60, 95) + (rand(0, 99) / 100); // 60.00 đến 95.99
                    
                    KetQuaMatching::create([
                        'ho_so_id' => $hoSo->id,
                        'tin_tuyen_dung_id' => $tin->id,
                        'diem_phu_hop' => $diem,
                        'chi_tiet_diem' => $reasons,
                        'danh_sach_ky_nang_thieu' => ($diem < 80) ? 'AWS, Tiếng Anh (Giao tiếp), Redis' : null,
                        'model_version' => 'v1.0-tfidf',
                        'thoi_gian_match' => now()->subHours(rand(1, 24))
                    ]);
                }
            }
        }
        
        echo "✅ KetQuaMatchingSeeder: Các ứng viên đã nhận được Danh sách Việc Làm Gợi Ý từ AI thuật toán (v1.0)!\n";
    }
}
