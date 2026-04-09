<?php

namespace Database\Seeders;

use App\Models\HoSo;
use App\Models\TinTuyenDung;
use App\Models\UngTuyen;
use Illuminate\Database\Seeder;

class UngTuyenSeeder extends Seeder
{
    public function run(): void
    {
        // Lấy tất cả các tin tuyển dụng và hồ sơ có sẵn
        $tins = TinTuyenDung::all();
        $hoSos = HoSo::all();

        if ($tins->isEmpty() || $hoSos->isEmpty()) {
            return;
        }

        // Tạo ứng tuyển ngẫu nhiên
        // Đảm bảo không nộp cùng 1 tin bằng 2 hồ sơ của cùng 1 user,
        // để đơn giản, ta lặp qua từng user, bốc 1 hồ sơ của user đó nộp vô 1 tin.
        
        // Nhóm hồ sơ theo người dùng
        $hoSoByUser = $hoSos->groupBy('nguoi_dung_id');

        foreach ($hoSoByUser as $userId => $hoSosCuaUser) {
            // Lấy 1-3 tin tuyển dụng ngẫu nhiên để nộp
            $soLuongTinUngTuyen = rand(1, 3);
            $tinsDeNop = $tins->random(min($soLuongTinUngTuyen, $tins->count()));

            foreach ($tinsDeNop as $tin) {
                // Random lấy 1 hồ sơ của user này để nộp
                $hoSoDeNop = $hoSosCuaUser->random();

                // Kiểm tra xem user này đã nộp vô tin này trc đó chưa (trong lần loop trước)
                $daNop = UngTuyen::where('tin_tuyen_dung_id', $tin->id)
                    ->whereHas('hoSo', function($q) use ($userId) {
                        $q->where('nguoi_dung_id', $userId);
                    })->exists();
                
                if (!$daNop) {
                    $trangThaiRandom = UngTuyen::TRANG_THAI_LIST[array_rand(UngTuyen::TRANG_THAI_LIST)];
                    
                    $data = [
                        'tin_tuyen_dung_id' => $tin->id,
                        'ho_so_id' => $hoSoDeNop->id,
                        'thu_xin_viec' => (rand(1, 100) > 30) ? 'Chào nhà tuyển dụng, tôi thấy công việc rất phù hợp với năng lực và định hướng phát triển của mình. Kính mong anh/chị xem xét CV đính kèm ạ.' : null,
                        'trang_thai' => $trangThaiRandom,
                        'thoi_gian_ung_tuyen' => now()->subDays(rand(0, 10))->subHours(rand(0, 24))
                    ];

                    if ($trangThaiRandom == UngTuyen::TRANG_THAI_CHAP_NHAN || $trangThaiRandom == UngTuyen::TRANG_THAI_TU_CHOI) {
                        $data['ngay_hen_phong_van'] = now()->addDays(rand(1, 14));
                        $data['ghi_chu'] = 'Hẹn bạn lúc 9h sáng.';
                        
                        if ($trangThaiRandom == UngTuyen::TRANG_THAI_CHAP_NHAN) {
                            $data['ket_qua_phong_van'] = 'Ứng viên tiềm năng, pass kỹ thuật.';
                        } else {
                            $data['ket_qua_phong_van'] = 'Chưa phù hợp định hướng tại thời điểm hiện tại.';
                        }
                    }

                    UngTuyen::create($data);
                }
            }
        }

        echo "✅ UngTuyenSeeder: Ứng viên đã nộp hồ sơ mẫu thành công!\n";
    }
}
