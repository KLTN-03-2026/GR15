<?php

namespace Database\Seeders;

use App\Models\NguoiDung;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class NguoiDungSeeder extends Seeder
{
    /**
     * Seed dữ liệu bảng nguoi_dungs theo nhóm người dùng gần với bối cảnh thật.
     */
    public function run(): void
    {
        NguoiDung::create([
            'ho_ten' => 'Nguyễn Minh Quân',
            'email' => 'admin@kltn.com',
            'email_verified_at' => now(),
            'mat_khau' => Hash::make('Admin@123'),
            'so_dien_thoai' => '0901234567',
            'ngay_sinh' => '1990-01-15',
            'gioi_tinh' => 'nam',
            'dia_chi' => '27 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh',
            'vai_tro' => NguoiDung::VAI_TRO_ADMIN,
            'cap_admin' => NguoiDung::CAP_ADMIN_SUPER_ADMIN,
            'trang_thai' => 1,
        ]);

        $adminThuongCoDinh = [
            [
                'ho_ten' => 'Lê Anh Khoa',
                'email' => 'admin.ops1@kltn.com',
                'so_dien_thoai' => '0902345678',
                'ngay_sinh' => '1992-03-11',
                'gioi_tinh' => 'nam',
                'dia_chi' => '88 Cách Mạng Tháng 8, Quận 10, TP. Hồ Chí Minh',
            ],
            [
                'ho_ten' => 'Ngô Thị Bảo Ngân',
                'email' => 'admin.ops2@kltn.com',
                'so_dien_thoai' => '0903456789',
                'ngay_sinh' => '1994-08-26',
                'gioi_tinh' => 'nu',
                'dia_chi' => '15 Trần Hưng Đạo, Hải Châu, Đà Nẵng',
            ],
            [
                'ho_ten' => 'Phạm Đức Hưng',
                'email' => 'admin.ops3@kltn.com',
                'so_dien_thoai' => '0904567891',
                'ngay_sinh' => '1991-12-08',
                'gioi_tinh' => 'nam',
                'dia_chi' => '41 Kim Mã, Ba Đình, Hà Nội',
            ],
        ];

        foreach ($adminThuongCoDinh as $adminThuong) {
            NguoiDung::create([
                'ho_ten' => $adminThuong['ho_ten'],
                'email' => $adminThuong['email'],
                'email_verified_at' => now(),
                'mat_khau' => Hash::make('Admin@123'),
                'so_dien_thoai' => $adminThuong['so_dien_thoai'],
                'ngay_sinh' => $adminThuong['ngay_sinh'],
                'gioi_tinh' => $adminThuong['gioi_tinh'],
                'dia_chi' => $adminThuong['dia_chi'],
                'vai_tro' => NguoiDung::VAI_TRO_ADMIN,
                'cap_admin' => NguoiDung::CAP_ADMIN_ADMIN,
                'trang_thai' => 1,
            ]);
        }

        $nhaTuyenDungCoDinh = [
            [
                'ho_ten' => 'Trần Gia Huy',
                'email' => 'tuyen.dung1@kltn.com',
                'so_dien_thoai' => '0912345678',
                'ngay_sinh' => '1987-04-12',
                'gioi_tinh' => 'nam',
                'dia_chi' => '102 Pasteur, Quận 3, TP. Hồ Chí Minh',
            ],
            [
                'ho_ten' => 'Võ Ngọc Anh',
                'email' => 'tuyen.dung2@kltn.com',
                'so_dien_thoai' => '0923456789',
                'ngay_sinh' => '1990-09-23',
                'gioi_tinh' => 'nu',
                'dia_chi' => '58 Nguyễn Văn Linh, Hải Châu, Đà Nẵng',
            ],
            [
                'ho_ten' => 'Phan Quốc Thịnh',
                'email' => 'tuyen.dung3@kltn.com',
                'so_dien_thoai' => '0934567801',
                'ngay_sinh' => '1985-11-05',
                'gioi_tinh' => 'nam',
                'dia_chi' => '19 Duy Tân, Cầu Giấy, Hà Nội',
            ],
        ];

        foreach ($nhaTuyenDungCoDinh as $nhaTuyenDung) {
            NguoiDung::create([
                'ho_ten' => $nhaTuyenDung['ho_ten'],
                'email' => $nhaTuyenDung['email'],
                'email_verified_at' => now(),
                'mat_khau' => Hash::make('NTD@123456'),
                'so_dien_thoai' => $nhaTuyenDung['so_dien_thoai'],
                'ngay_sinh' => $nhaTuyenDung['ngay_sinh'],
                'gioi_tinh' => $nhaTuyenDung['gioi_tinh'],
                'dia_chi' => $nhaTuyenDung['dia_chi'],
                'vai_tro' => NguoiDung::VAI_TRO_NHA_TUYEN_DUNG,
                'trang_thai' => 1,
            ]);
        }

        NguoiDung::create([
            'ho_ten' => 'Đặng Mỹ Linh',
            'email' => 'tuyen.dung.khoa@kltn.com',
            'email_verified_at' => now(),
            'mat_khau' => Hash::make('NTD@123456'),
            'so_dien_thoai' => '0945678012',
            'ngay_sinh' => '1989-02-17',
            'gioi_tinh' => 'nu',
            'dia_chi' => '201 Hoàng Văn Thụ, Phú Nhuận, TP. Hồ Chí Minh',
            'vai_tro' => NguoiDung::VAI_TRO_NHA_TUYEN_DUNG,
            'trang_thai' => 0,
        ]);

        $ungVienCoDinh = [
            [
                'ho_ten' => 'Phạm Văn An',
                'email' => 'ung.vien1@kltn.com',
                'so_dien_thoai' => '0934567890',
                'ngay_sinh' => '1999-11-05',
                'gioi_tinh' => 'nam',
                'dia_chi' => '12 Trần Phú, Ba Đình, Hà Nội',
            ],
            [
                'ho_ten' => 'Lê Thị Bình',
                'email' => 'ung.vien2@kltn.com',
                'so_dien_thoai' => '0945678901',
                'ngay_sinh' => '2000-07-22',
                'gioi_tinh' => 'nu',
                'dia_chi' => '89 Pasteur, Bình Thạnh, TP. Hồ Chí Minh',
            ],
            [
                'ho_ten' => 'Nguyễn Hoàng Long',
                'email' => 'ung.vien3@kltn.com',
                'so_dien_thoai' => '0956789012',
                'ngay_sinh' => '1997-03-14',
                'gioi_tinh' => 'nam',
                'dia_chi' => '43 Nguyễn Tri Phương, Hải Châu, Đà Nẵng',
            ],
            [
                'ho_ten' => 'Trương Khánh Vy',
                'email' => 'ung.vien4@kltn.com',
                'so_dien_thoai' => '0967890123',
                'ngay_sinh' => '1998-12-01',
                'gioi_tinh' => 'nu',
                'dia_chi' => '17 Võ Văn Tần, Quận 3, TP. Hồ Chí Minh',
            ],
            [
                'ho_ten' => 'Bùi Đức Nam',
                'email' => 'ung.vien5@kltn.com',
                'so_dien_thoai' => '0978901234',
                'ngay_sinh' => '1996-06-19',
                'gioi_tinh' => 'nam',
                'dia_chi' => '75 Trần Duy Hưng, Cầu Giấy, Hà Nội',
            ],
        ];

        foreach ($ungVienCoDinh as $ungVien) {
            NguoiDung::create([
                'ho_ten' => $ungVien['ho_ten'],
                'email' => $ungVien['email'],
                'email_verified_at' => now(),
                'mat_khau' => Hash::make('UV@123456'),
                'so_dien_thoai' => $ungVien['so_dien_thoai'],
                'ngay_sinh' => $ungVien['ngay_sinh'],
                'gioi_tinh' => $ungVien['gioi_tinh'],
                'dia_chi' => $ungVien['dia_chi'],
                'vai_tro' => NguoiDung::VAI_TRO_UNG_VIEN,
                'trang_thai' => 1,
            ]);
        }

        NguoiDung::create([
            'ho_ten' => 'Hoàng Minh Tuấn',
            'email' => 'ung.vien.khoa@kltn.com',
            'email_verified_at' => now(),
            'mat_khau' => Hash::make('UV@123456'),
            'so_dien_thoai' => '0987654321',
            'ngay_sinh' => '1998-04-18',
            'gioi_tinh' => 'nam',
            'dia_chi' => '34 Lý Thường Kiệt, Hoàn Kiếm, Hà Nội',
            'vai_tro' => NguoiDung::VAI_TRO_UNG_VIEN,
            'trang_thai' => 0,
        ]);

        NguoiDung::factory()->nhaTuyenDung()->count(6)->create([
            'email_verified_at' => now(),
        ]);
        NguoiDung::factory()->ungVien()->count(8)->create([
            'email_verified_at' => now(),
        ]);

        $this->command->info('✅ NguoiDungSeeder: Đã tạo dữ liệu tài khoản gần với tình huống thực tế.');
        $this->command->table(
            ['Nhóm', 'Số lượng', 'Ghi chú'],
            [
                ['Super Admin', '1', 'admin@kltn.com / Admin@123'],
                ['Admin thường', '3', 'admin.ops1/2/3@kltn.com / Admin@123'],
                ['Nhà tuyển dụng hoạt động', '3 cố định + 6 factory', 'Mật khẩu: NTD@123456 hoặc password123'],
                ['Nhà tuyển dụng bị khóa', '1', 'tuyen.dung.khoa@kltn.com'],
                ['Ứng viên hoạt động', '5 cố định + 8 factory', 'Mật khẩu: UV@123456 hoặc password123'],
                ['Ứng viên bị khóa', '1', 'ung.vien.khoa@kltn.com'],
                ['Tổng cộng', '28', 'Phân bố theo nhiều tỉnh thành'],
            ]
        );
    }
}
