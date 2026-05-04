<?php

namespace Database\Seeders;

use App\Models\NguoiDung;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class NhaTuyenDungChuaCoCongTySeeder extends Seeder
{
    public function run(): void
    {
        NguoiDung::firstOrCreate(
            ['email' => 'tuyen.dung.nocongty@kltn.com'],
            [
                'ho_ten' => 'Nguyễn Thanh Phương',
                'email_verified_at' => now(),
                'mat_khau' => Hash::make('NTD@123456'),
                'so_dien_thoai' => '0911223344',
                'ngay_sinh' => '1991-06-21',
                'gioi_tinh' => 'nu',
                'dia_chi' => '45 Nguyễn Hữu Cảnh, Bình Thạnh, TP. Hồ Chí Minh',
                'vai_tro' => NguoiDung::VAI_TRO_NHA_TUYEN_DUNG,
                'trang_thai' => 1,
            ],
        );

        $this->command?->info('✅ NhaTuyenDungChuaCoCongTySeeder: Đã đảm bảo có 1 nhà tuyển dụng chưa thuộc công ty nào.');
    }
}
