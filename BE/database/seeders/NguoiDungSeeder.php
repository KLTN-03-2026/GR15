<?php

namespace Database\Seeders;

use App\Models\NguoiDung;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class NguoiDungSeeder extends Seeder
{
    /**
     * Seed dữ liệu bảng nguoi_dungs.
     *
     * Tạo:
     *  - 1 Admin cố định
     *  - 5 Nhà tuyển dụng (2 cố định + 2 ngẫu nhiên + 1 bị khoá)
     *  - 11 Ứng viên (3 cố định + 7 ngẫu nhiên + 1 bị khoá)
     */
    public function run(): void
    {
        // =========================================
        // ADMIN - Tài khoản quản trị viên
        // =========================================
        NguoiDung::create([
            'ho_ten' => 'Super Admin',
            'email' => 'admin@kltn.com',
            'mat_khau' => Hash::make('Admin@123'),
            'so_dien_thoai' => '0901234567',
            'ngay_sinh' => '1990-01-15',
            'gioi_tinh' => 'nam',
            'dia_chi' => '123 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh',
            'vai_tro' => NguoiDung::VAI_TRO_ADMIN,
            'trang_thai' => 1,
        ]);

        // =========================================
        // NHÀ TUYỂN DỤNG - Cố định (dễ test)
        // =========================================
        NguoiDung::create([
            'ho_ten' => 'Nguyễn Văn Tuyển',
            'email' => 'tuyen.dung1@kltn.com',
            'mat_khau' => Hash::make('NTD@123456'),
            'so_dien_thoai' => '0912345678',
            'ngay_sinh' => '1985-06-20',
            'gioi_tinh' => 'nam',
            'dia_chi' => '45 Lê Lợi, Quận 3, TP. Hồ Chí Minh',
            'vai_tro' => NguoiDung::VAI_TRO_NHA_TUYEN_DUNG,
            'trang_thai' => 1,
        ]);

        NguoiDung::create([
            'ho_ten' => 'Trần Thị Lan',
            'email' => 'tuyen.dung2@kltn.com',
            'mat_khau' => Hash::make('NTD@123456'),
            'so_dien_thoai' => '0923456789',
            'ngay_sinh' => '1988-03-10',
            'gioi_tinh' => 'nu',
            'dia_chi' => '67 Hoàng Diệu, Hải Châu, Đà Nẵng',
            'vai_tro' => NguoiDung::VAI_TRO_NHA_TUYEN_DUNG,
            'trang_thai' => 1,
        ]);

        // =========================================
        // ỨNG VIÊN - Cố định (dễ test)
        // =========================================
        NguoiDung::create([
            'ho_ten' => 'Phạm Văn An',
            'email' => 'ung.vien1@kltn.com',
            'mat_khau' => Hash::make('UV@123456'),
            'so_dien_thoai' => '0934567890',
            'ngay_sinh' => '1999-11-05',
            'gioi_tinh' => 'nam',
            'dia_chi' => '12 Trần Phú, Ba Đình, Hà Nội',
            'vai_tro' => NguoiDung::VAI_TRO_UNG_VIEN,
            'trang_thai' => 1,
        ]);

        NguoiDung::create([
            'ho_ten' => 'Lê Thị Bình',
            'email' => 'ung.vien2@kltn.com',
            'mat_khau' => Hash::make('UV@123456'),
            'so_dien_thoai' => '0945678901',
            'ngay_sinh' => '2000-07-22',
            'gioi_tinh' => 'nu',
            'dia_chi' => '89 Pasteur, Quận Bình Thạnh, TP. Hồ Chí Minh',
            'vai_tro' => NguoiDung::VAI_TRO_UNG_VIEN,
            'trang_thai' => 1,
        ]);

        // Ứng viên bị khoá (để test case tài khoản bị khoá)
        NguoiDung::create([
            'ho_ten' => 'Hoàng Minh Tuấn',
            'email' => 'ung.vien.khoa@kltn.com',
            'mat_khau' => Hash::make('UV@123456'),
            'so_dien_thoai' => '0956789012',
            'ngay_sinh' => '1998-04-18',
            'gioi_tinh' => 'nam',
            'dia_chi' => '34 Lý Thường Kiệt, Hoàn Kiếm, Hà Nội',
            'vai_tro' => NguoiDung::VAI_TRO_UNG_VIEN,
            'trang_thai' => 0,
        ]);

        // =========================================
        // DỮ LIỆU NGẪU NHIÊN bằng Factory
        // =========================================
        NguoiDung::factory()->nhaTuyenDung()->count(2)->create();
        NguoiDung::factory()->nhaTuyenDung()->inactive()->count(1)->create();
        NguoiDung::factory()->ungVien()->count(7)->create();
        NguoiDung::factory()->ungVien()->inactive()->count(1)->create();

        $this->command->info('✅ NguoiDungSeeder: Đã tạo dữ liệu thành công!');
        $this->command->table(
            ['Vai trò', 'Email', 'Mật khẩu'],
            [
                ['Admin', 'admin@kltn.com', 'Admin@123'],
                ['Nhà tuyển dụng', 'tuyen.dung1@kltn.com', 'NTD@123456'],
                ['Nhà tuyển dụng', 'tuyen.dung2@kltn.com', 'NTD@123456'],
                ['Ứng viên', 'ung.vien1@kltn.com', 'UV@123456'],
                ['Ứng viên', 'ung.vien2@kltn.com', 'UV@123456'],
                ['Ứng viên (🔒khoá)', 'ung.vien.khoa@kltn.com', 'UV@123456'],
                ['Ngẫu nhiên', '...factory generated...', 'password123'],
            ]
        );
    }
}
