<?php

namespace Database\Seeders;

use App\Models\NguoiDung;
use App\Models\TinTuyenDung;
use Illuminate\Database\Seeder;

class LuuTinSeeder extends Seeder
{
    public function run(): void
    {
        // Lấy tất cả ứng viên (vai_tro = 0)
        $ungViens = NguoiDung::where('vai_tro', 0)->get();
        // Lấy tất cả tin tuyển dụng đang hoạt động
        $tins = TinTuyenDung::where('trang_thai', 1)->get();

        if ($ungViens->isEmpty() || $tins->isEmpty()) {
            return;
        }

        // Tạo lưu tin ngẫu nhiên
        foreach ($ungViens as $uv) {
            // Mỗi người dùng lưu từ 0-5 tin
            $tinLuus = $tins->random(rand(0, 5))->pluck('id');
            
            // Dùng syncWithoutDetaching nếu chạy nhiều lần
            $uv->tinDaLuus()->syncWithoutDetaching($tinLuus);
        }

        // Tạo chắc chắn UV1 lưu tin ID=1 (để postman dễ test)
        $uv1 = NguoiDung::where('email', 'ung.vien1@kltn.com')->first();
        if ($uv1 && $tins->first()) {
            $uv1->tinDaLuus()->syncWithoutDetaching([$tins->first()->id]);
        }

        echo "✅ LuuTinSeeder: Ứng viên đã lưu tin mẫu thành công!\n";
    }
}
