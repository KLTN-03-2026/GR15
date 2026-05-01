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
        $ntds = NguoiDung::where('vai_tro', NguoiDung::VAI_TRO_NHA_TUYEN_DUNG)->get();

        if ($ntds->isEmpty()) {
            $this->command->warn('⚠️ Chưa có nhà tuyển dụng. Hãy chạy NguoiDungSeeder trước.');
            return;
        }

        $nganhNghes = NganhNghe::where('trang_thai', NganhNghe::TRANG_THAI_HIEN_THI)->get();
        $tong = 0;

        $congTyTheoEmail = [
            'tuyen.dung1@kltn.com' => [
                'ten_cong_ty' => 'TechViet Solutions',
                'ma_so_thue' => '0314827561',
                'mo_ta' => 'Doanh nghiệp công nghệ phát triển nền tảng SaaS cho bán lẻ, logistics và vận hành nội bộ. Đội ngũ tập trung vào web app, mobile app và tích hợp dữ liệu thời gian thực.',
                'dia_chi' => '25 Nguyễn Thị Minh Khai, Quận 1, TP. Hồ Chí Minh',
                'dien_thoai' => '02838246891',
                'email' => 'careers@techviet.vn',
                'website' => 'https://techviet.vn',
                'nganh' => 'Công nghệ thông tin',
                'quy_mo' => '51-200',
            ],
            'tuyen.dung2@kltn.com' => [
                'ten_cong_ty' => 'DigiGrowth Agency',
                'ma_so_thue' => '0401985236',
                'mo_ta' => 'Agency chuyên performance marketing, social commerce và vận hành nội dung đa nền tảng cho doanh nghiệp SME và startup.',
                'dia_chi' => '88 Bạch Đằng, Hải Châu, Đà Nẵng',
                'dien_thoai' => '02363876543',
                'email' => 'talent@digigrowth.vn',
                'website' => 'https://digigrowth.vn',
                'nganh' => 'Marketing / Truyền thông',
                'quy_mo' => '11-50',
            ],
            'tuyen.dung3@kltn.com' => [
                'ten_cong_ty' => 'NorthStar Analytics',
                'ma_so_thue' => '0109172648',
                'mo_ta' => 'Công ty tư vấn dữ liệu và phân tích vận hành, triển khai dashboard BI, data warehouse và các mô hình dự báo cho khối tài chính và bán lẻ.',
                'dia_chi' => '14 Duy Tân, Cầu Giấy, Hà Nội',
                'dien_thoai' => '02437654321',
                'email' => 'jobs@northstar-analytics.vn',
                'website' => 'https://northstar-analytics.vn',
                'nganh' => 'Công nghệ thông tin',
                'quy_mo' => '11-50',
            ],
            'tuyen.dung.khoa@kltn.com' => [
                'ten_cong_ty' => 'UrbanHire Services',
                'ma_so_thue' => '0319158420',
                'mo_ta' => 'Đơn vị cung ứng nhân sự văn phòng và dịch vụ tuyển dụng thuê ngoài cho doanh nghiệp vừa và nhỏ.',
                'dia_chi' => '201 Hoàng Văn Thụ, Phú Nhuận, TP. Hồ Chí Minh',
                'dien_thoai' => '02839995566',
                'email' => 'contact@urbanhire.vn',
                'website' => 'https://urbanhire.vn',
                'nganh' => 'Nhân sự / Hành chính',
                'quy_mo' => '11-50',
                'trang_thai' => CongTy::TRANG_THAI_TAM_NGUNG,
            ],
        ];

        foreach ($congTyTheoEmail as $email => $data) {
            $ntd = $ntds->firstWhere('email', $email);
            if (!$ntd) {
                continue;
            }

            $nganh = $nganhNghes->firstWhere('ten_nganh', $data['nganh']);

            CongTy::create([
                'nguoi_dung_id' => $ntd->id,
                'ten_cong_ty' => $data['ten_cong_ty'],
                'ma_so_thue' => $data['ma_so_thue'],
                'mo_ta' => $data['mo_ta'],
                'dia_chi' => $data['dia_chi'],
                'dien_thoai' => $data['dien_thoai'],
                'email' => $data['email'],
                'website' => $data['website'],
                'nganh_nghe_id' => $nganh?->id,
                'quy_mo' => $data['quy_mo'],
                'trang_thai' => $data['trang_thai'] ?? CongTy::TRANG_THAI_HOAT_DONG,
            ]);
            $tong++;
        }

        $mauCongTyChoFactory = [
            [
                'ten_cong_ty' => 'Mekong Commerce',
                'mo_ta' => 'Đơn vị thương mại điện tử vận hành chuỗi gian hàng đa sàn, chú trọng growth và tối ưu chuyển đổi.',
                'dia_chi' => '9 Trần Văn Khéo, Ninh Kiều, Cần Thơ',
                'quy_mo' => '51-200',
                'email_domain' => 'mekongcommerce.vn',
                'nganh' => 'Kinh doanh / Bán hàng',
            ],
            [
                'ten_cong_ty' => 'BlueOrbit Cloud',
                'mo_ta' => 'Công ty hạ tầng cloud và managed services phục vụ khách hàng doanh nghiệp trong khu vực Đông Nam Á.',
                'dia_chi' => '6A Tôn Đức Thắng, Ba Đình, Hà Nội',
                'quy_mo' => '51-200',
                'email_domain' => 'blueorbitcloud.vn',
                'nganh' => 'Công nghệ thông tin',
            ],
            [
                'ten_cong_ty' => 'Sunrise Education Hub',
                'mo_ta' => 'Tổ chức edtech phát triển nền tảng học trực tuyến, quản lý khóa học và nội dung đào tạo cho doanh nghiệp.',
                'dia_chi' => '42 Lê Lợi, Hải Châu, Đà Nẵng',
                'quy_mo' => '11-50',
                'email_domain' => 'sunriseedu.vn',
                'nganh' => 'Giáo dục / Đào tạo',
            ],
            [
                'ten_cong_ty' => 'GreenLog Supply Chain',
                'mo_ta' => 'Doanh nghiệp tối ưu vận tải, kho bãi và phân phối bằng hệ thống theo dõi đơn hàng và dữ liệu vận hành thời gian thực.',
                'dia_chi' => '128 Xa Lộ Hà Nội, TP. Thủ Đức, TP. Hồ Chí Minh',
                'quy_mo' => '201-500',
                'email_domain' => 'greenlog.vn',
                'nganh' => 'Vận chuyển / Giao nhận',
            ],
            [
                'ten_cong_ty' => 'Lumiere Creative Studio',
                'mo_ta' => 'Studio sáng tạo nội dung, branding và thiết kế trải nghiệm số cho thương hiệu tiêu dùng và startup.',
                'dia_chi' => '17 Nguyễn Văn Cừ, Ninh Kiều, Cần Thơ',
                'quy_mo' => '11-50',
                'email_domain' => 'lumierestudio.vn',
                'nganh' => 'Thiết kế / Sáng tạo nghệ thuật',
            ],
            [
                'ten_cong_ty' => 'FinCore Advisory',
                'mo_ta' => 'Đơn vị tư vấn tài chính doanh nghiệp, kế toán quản trị và chuyển đổi số cho khối SME.',
                'dia_chi' => '55 Phan Chu Trinh, Hoàn Kiếm, Hà Nội',
                'quy_mo' => '11-50',
                'email_domain' => 'fincoreadvisory.vn',
                'nganh' => 'Tài chính / Đầu tư',
            ],
            [
                'ten_cong_ty' => 'Healium Care Network',
                'mo_ta' => 'Mạng lưới dịch vụ y tế số kết nối phòng khám, chăm sóc khách hàng và vận hành hồ sơ sức khỏe điện tử.',
                'dia_chi' => '210 Điện Biên Phủ, Bình Thạnh, TP. Hồ Chí Minh',
                'quy_mo' => '51-200',
                'email_domain' => 'healiumcare.vn',
                'nganh' => 'Y tế / Chăm sóc sức khỏe',
            ],
        ];

        $ntdConLai = $ntds->filter(function ($ntd) {
            return !in_array($ntd->email, [
                'tuyen.dung1@kltn.com',
                'tuyen.dung2@kltn.com',
                'tuyen.dung3@kltn.com',
                'tuyen.dung.khoa@kltn.com',
            ], true);
        })->values();

        foreach ($ntdConLai as $index => $ntd) {
            $mau = $mauCongTyChoFactory[$index % count($mauCongTyChoFactory)];
            $nganh = $nganhNghes->firstWhere('ten_nganh', $mau['nganh']) ?? $nganhNghes->first();

            CongTy::create([
                'nguoi_dung_id' => $ntd->id,
                'ten_cong_ty' => $mau['ten_cong_ty'] . ' ' . ($index + 1),
                'ma_so_thue' => '1000000' . str_pad((string) ($index + 1), 3, '0', STR_PAD_LEFT),
                'mo_ta' => $mau['mo_ta'],
                'dia_chi' => $mau['dia_chi'],
                'dien_thoai' => '0283' . str_pad((string) (456700 + $index), 6, '0', STR_PAD_LEFT),
                'email' => 'hr' . ($index + 1) . '@' . $mau['email_domain'],
                'website' => 'https://www.' . $mau['email_domain'],
                'logo' => null,
                'nganh_nghe_id' => $nganh?->id,
                'quy_mo' => $mau['quy_mo'],
                'trang_thai' => $ntd->trang_thai ? CongTy::TRANG_THAI_HOAT_DONG : CongTy::TRANG_THAI_TAM_NGUNG,
            ]);
            $tong++;
        }

        $this->command->info("✅ CongTySeeder: Đã tạo {$tong} công ty với thông tin gần thực tế.");
    }
}
