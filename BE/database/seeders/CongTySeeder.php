<?php

namespace Database\Seeders;

use App\Models\CongTy;
use App\Models\NganhNghe;
use App\Models\NguoiDung;
use Illuminate\Database\Seeder;

class CongTySeeder extends Seeder
{
    public function run(): void
    {
        $ntds = NguoiDung::where('vai_tro', 1)->get();

        if ($ntds->isEmpty()) {
            $this->command->warn('⚠️ Chưa có NTD. Hãy chạy NguoiDungSeeder trước.');
            return;
        }

        $nganhNghes = NganhNghe::where('trang_thai', 1)->get();
        $tong = 0;

        // --- NTD 1: Công ty công nghệ ---
        $ntd1 = $ntds->firstWhere('email', 'tuyen.dung1@kltn.com');
        if ($ntd1) {
            $nnCNTT = $nganhNghes->firstWhere('ten_nganh', 'Công nghệ thông tin');
            CongTy::create([
                'nguoi_dung_id' => $ntd1->id,
                'ten_cong_ty' => 'TechViet Solutions',
                'ma_so_thue' => '0123456789',
                'mo_ta' => 'Công ty phát triển phần mềm hàng đầu Việt Nam, chuyên về giải pháp web & mobile cho doanh nghiệp.',
                'dia_chi' => '123 Nguyễn Huệ, Quận 1, TP.HCM',
                'dien_thoai' => '028-1234-5678',
                'email' => 'hr@techviet.vn',
                'website' => 'https://techviet.vn',
                'logo' => 'techviet-logo.png',
                'nganh_nghe_id' => $nnCNTT?->id,
                'quy_mo' => '51-200',
                'trang_thai' => CongTy::TRANG_THAI_HOAT_DONG,
            ]);
            $tong++;
        }

        // --- NTD 2: Công ty marketing ---
        $ntd2 = $ntds->firstWhere('email', 'tuyen.dung2@kltn.com');
        if ($ntd2) {
            $nnMarketing = $nganhNghes->firstWhere('ten_nganh', 'Marketing - Truyền thông');
            CongTy::create([
                'nguoi_dung_id' => $ntd2->id,
                'ten_cong_ty' => 'DigiGrowth Agency',
                'ma_so_thue' => '9876543210',
                'mo_ta' => 'Agency digital marketing sáng tạo, chuyên chiến lược branding và performance marketing.',
                'dia_chi' => '456 Lê Lợi, Quận 3, TP.HCM',
                'dien_thoai' => '028-9876-5432',
                'email' => 'career@digigrowth.vn',
                'website' => 'https://digigrowth.vn',
                'logo' => 'digigrowth-logo.png',
                'nganh_nghe_id' => $nnMarketing?->id,
                'quy_mo' => '11-50',
                'trang_thai' => CongTy::TRANG_THAI_HOAT_DONG,
            ]);
            $tong++;
        }

        // Tạo thêm vài công ty mẫu cho NTD khác (nếu có)
        $ntdConLai = $ntds->whereNotIn('email', ['tuyen.dung1@kltn.com', 'tuyen.dung2@kltn.com']);
        $congTyMau = [
            ['ten' => 'CloudNine Tech', 'mo_ta' => 'Công ty cloud computing & DevOps', 'quy_mo' => '201-500', 'dia_chi' => '789 Hai Bà Trưng, Hà Nội'],
            ['ten' => 'GreenFinance Corp', 'mo_ta' => 'Công ty tài chính xanh', 'quy_mo' => '500+', 'dia_chi' => '321 Trần Hưng Đạo, Đà Nẵng'],
            ['ten' => 'StartupHub VN', 'mo_ta' => 'Vườn ươm khởi nghiệp', 'quy_mo' => '1-10', 'dia_chi' => '99 Nguyễn Văn Linh, TP.HCM'],
        ];

        $i = 0;
        foreach ($ntdConLai as $ntd) {
            if ($i >= count($congTyMau))
                break;
            $mau = $congTyMau[$i];
            $nn = $nganhNghes->random();
            CongTy::create([
                'nguoi_dung_id' => $ntd->id,
                'ten_cong_ty' => $mau['ten'],
                'ma_so_thue' => '100000000' . $i,
                'mo_ta' => $mau['mo_ta'],
                'dia_chi' => $mau['dia_chi'],
                'nganh_nghe_id' => $nn->id,
                'quy_mo' => $mau['quy_mo'],
                'trang_thai' => CongTy::TRANG_THAI_HOAT_DONG,
            ]);
            $tong++;
            $i++;
        }

        $this->command->info("✅ CongTySeeder: Đã tạo {$tong} công ty thành công!");
    }
}
