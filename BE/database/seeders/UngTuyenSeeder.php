<?php

namespace Database\Seeders;

use App\Models\HoSo;
use App\Models\TinTuyenDung;
use App\Models\UngTuyen;
use Carbon\Carbon;
use Illuminate\Database\Seeder;

class UngTuyenSeeder extends Seeder
{
    private function nowUtc(): Carbon
    {
        return Carbon::now('UTC');
    }

    public function run(): void
    {
        $hoSos = HoSo::with('nguoiDung')->get();
        $tins = TinTuyenDung::with('congTy')->get()->keyBy('tieu_de');

        if ($tins->isEmpty() || $hoSos->isEmpty()) {
            return;
        }

        $nowUtc = $this->nowUtc();

        $ungTuyenCoDinh = [
            [
                'email' => 'ung.vien1@kltn.com',
                'ho_so' => 'Backend Developer Laravel/PHP',
                'tin' => 'Backend Developer Laravel',
                'trang_thai' => UngTuyen::TRANG_THAI_DA_XEM,
                'thu_xin_viec' => 'Tôi có 3 năm kinh nghiệm phát triển backend với PHP/Laravel, từng làm các hệ thống CRM và quản trị nội bộ. Tôi tin nền tảng về API, MySQL và tối ưu truy vấn sẽ phù hợp với nhu cầu tuyển dụng của công ty.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(6)->setHour(2)->setMinute(15),
            ],
            [
                'email' => 'ung.vien5@kltn.com',
                'ho_so' => 'QA Engineer Manual/Automation',
                'tin' => 'QA Engineer (Manual/API)',
                'trang_thai' => UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN,
                'thu_xin_viec' => 'Tôi từng kiểm thử web admin, mobile web và API cho các dự án SaaS, có kinh nghiệm viết test case và phối hợp xác nhận lỗi với đội phát triển. Mong muốn được trao đổi thêm về quy trình QA hiện tại của công ty.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(4)->setHour(7)->setMinute(5),
                'ngay_hen_phong_van' => $nowUtc->copy()->addDays(3)->setHour(2)->setMinute(0),
                'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_DA_XAC_NHAN,
                'thoi_gian_phan_hoi_phong_van' => $nowUtc->copy()->subDay()->setHour(3)->setMinute(30),
                'hinh_thuc_phong_van' => 'Online',
                'nguoi_phong_van' => 'Trần Gia Huy',
                'link_phong_van' => 'https://meet.google.com/qa-techviet-round1',
                'ket_qua_phong_van' => 'Ứng viên phù hợp với vai trò QA dự án web admin, giao tiếp rõ ràng và nắm tốt quy trình kiểm thử.',
                'ghi_chu' => 'Phỏng vấn vòng 1 với QA Lead và PM.',
            ],
            [
                'email' => 'ung.vien4@kltn.com',
                'ho_so' => 'Digital Marketing Executive',
                'tin' => 'Digital Marketing Executive',
                'trang_thai' => UngTuyen::TRANG_THAI_DA_XEM,
                'thu_xin_viec' => 'Tôi đã trực tiếp triển khai và tối ưu các chiến dịch Meta Ads, Google Ads cho ngành làm đẹp và giáo dục, có thói quen theo dõi số liệu hằng ngày và cải thiện nội dung theo hiệu quả chuyển đổi.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(5)->setHour(1)->setMinute(40),
            ],
            [
                'email' => 'ung.vien2@kltn.com',
                'ho_so' => 'Frontend Developer Vue/React',
                'tin' => 'Content Marketing Intern',
                'trang_thai' => UngTuyen::TRANG_THAI_TU_CHOI,
                'thu_xin_viec' => 'Tôi muốn tìm môi trường có thể học thêm về nội dung số và phối hợp đa phòng ban. Dù nền tảng chính là frontend và thiết kế, tôi có khả năng viết nội dung cho landing page và social media.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(7)->setHour(12)->setMinute(10),
                'ket_qua_phong_van' => 'Hồ sơ có nền tảng tốt nhưng chưa phù hợp định hướng vị trí content internship toàn thời gian.',
                'ghi_chu' => 'Khuyến khích ứng viên theo dõi vị trí thiết kế hoặc frontend khi công ty mở lại.',
            ],
            [
                'email' => 'ung.vien3@kltn.com',
                'ho_so' => 'Data Analyst BI',
                'tin' => 'Data Analyst',
                'trang_thai' => UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN,
                'thu_xin_viec' => 'Tôi có hơn 4 năm làm báo cáo vận hành và phân tích dữ liệu kinh doanh bằng SQL, Power BI và Python. Tôi đặc biệt hứng thú với các bài toán chuẩn hóa dữ liệu và xây dashboard phục vụ ra quyết định.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(3)->setHour(3)->setMinute(20),
                'ngay_hen_phong_van' => $nowUtc->copy()->addDays(2)->setHour(7)->setMinute(0),
                'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_CHO_XAC_NHAN,
                'hinh_thuc_phong_van' => 'Offline',
                'nguoi_phong_van' => 'Phan Quốc Thịnh',
                'ket_qua_phong_van' => 'Hồ sơ nổi bật ở mảng BI và SQL, cần trao đổi sâu hơn về kinh nghiệm xử lý dữ liệu lớn.',
                'ghi_chu' => 'Mời ứng viên làm case study ngắn trong buổi phỏng vấn.',
            ],
            [
                'email' => 'ung.vien1@kltn.com',
                'ho_so' => 'Full-stack Developer cho doanh nghiệp SME',
                'tin' => 'Frontend Developer Vue.js',
                'trang_thai' => UngTuyen::TRANG_THAI_QUA_PHONG_VAN,
                'thu_xin_viec' => 'Tôi có thể đảm nhiệm cả phần frontend Vue.js lẫn backend API trong môi trường team nhỏ. Kinh nghiệm phối hợp nhiều vai trò giúp tôi thích nghi nhanh với các dự án SME cần người làm xuyên stack.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(8)->setHour(6)->setMinute(25),
                'ngay_hen_phong_van' => $nowUtc->copy()->subDays(1)->setHour(2)->setMinute(30),
                'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_DA_XAC_NHAN,
                'thoi_gian_phan_hoi_phong_van' => $nowUtc->copy()->subDays(3)->setHour(9)->setMinute(10),
                'hinh_thuc_phong_van' => 'Online',
                'nguoi_phong_van' => 'Nguyễn Thu Hà',
                'link_phong_van' => 'https://meet.google.com/frontend-techviet-round2',
                'ket_qua_phong_van' => 'Ứng viên có tư duy sản phẩm tốt, trả lời ổn phần Vue.js và phối hợp liên phòng ban.',
                'ghi_chu' => 'Đang chờ quản lý phê duyệt offer nội bộ.',
            ],
            [
                'email' => 'ung.vien3@kltn.com',
                'ho_so' => 'Data Analyst BI',
                'tin' => 'BI Developer',
                'trang_thai' => UngTuyen::TRANG_THAI_TRUNG_TUYEN,
                'thu_xin_viec' => 'Tôi muốn tham gia vị trí BI Developer vì có kinh nghiệm xây dashboard quản trị và làm việc với stakeholder để chuẩn hóa chỉ số dữ liệu. Tôi tin có thể đóng góp nhanh cho các dự án BI đang triển khai.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(12)->setHour(1)->setMinute(50),
                'ngay_hen_phong_van' => $nowUtc->copy()->subDays(6)->setHour(7)->setMinute(30),
                'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_DA_XAC_NHAN,
                'thoi_gian_phan_hoi_phong_van' => $nowUtc->copy()->subDays(7)->setHour(8)->setMinute(0),
                'hinh_thuc_phong_van' => 'Offline',
                'nguoi_phong_van' => 'Phan Quốc Thịnh',
                'ket_qua_phong_van' => 'Ứng viên đạt yêu cầu về SQL, Power BI và khả năng làm việc với dữ liệu kinh doanh thực tế.',
                'ghi_chu' => 'Đã thống nhất mức lương và ngày nhận việc dự kiến.',
            ],
            [
                'email' => 'ung.vien4@kltn.com',
                'ho_so' => 'Digital Marketing Executive',
                'tin' => 'Graphic Designer Marketing',
                'trang_thai' => UngTuyen::TRANG_THAI_DA_XEM,
                'da_rut_don' => true,
                'thoi_gian_rut_don' => $nowUtc->copy()->subDays(2)->setHour(4)->setMinute(45),
                'thu_xin_viec' => 'Tôi có thể phối hợp chặt với team content và ads để tối ưu creative theo từng chiến dịch. Sau khi cân nhắc định hướng cá nhân, tôi xin rút hồ sơ để tập trung vào vị trí performance phù hợp hơn.',
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(9)->setHour(2)->setMinute(40),
                'ngay_hen_phong_van' => $nowUtc->copy()->addDay()->setHour(3)->setMinute(15),
                'trang_thai_tham_gia_phong_van' => UngTuyen::PHONG_VAN_KHONG_THAM_GIA,
                'thoi_gian_phan_hoi_phong_van' => $nowUtc->copy()->subDays(2)->setHour(4)->setMinute(45),
                'hinh_thuc_phong_van' => 'Online',
                'nguoi_phong_van' => 'Võ Ngọc Anh',
                'link_phong_van' => 'https://meet.google.com/digigrowth-design-round1',
                'ghi_chu' => 'Ứng viên chủ động rút đơn trước lịch phỏng vấn.',
            ],
        ];

        $tong = 0;

        foreach ($ungTuyenCoDinh as $item) {
            $hoSo = $hoSos->first(function ($record) use ($item) {
                return $record->nguoiDung?->email === $item['email']
                    && $record->tieu_de_ho_so === $item['ho_so'];
            });
            $tin = $tins->get($item['tin']);

            if (!$hoSo || !$tin) {
                continue;
            }

            UngTuyen::create([
                'tin_tuyen_dung_id' => $tin->id,
                'ho_so_id' => $hoSo->id,
                'trang_thai' => $item['trang_thai'],
                'da_rut_don' => $item['da_rut_don'] ?? false,
                'thoi_gian_rut_don' => $item['thoi_gian_rut_don'] ?? null,
                'thu_xin_viec' => $item['thu_xin_viec'],
                'ngay_hen_phong_van' => $item['ngay_hen_phong_van'] ?? null,
                'trang_thai_tham_gia_phong_van' => $item['trang_thai_tham_gia_phong_van'] ?? null,
                'thoi_gian_phan_hoi_phong_van' => $item['thoi_gian_phan_hoi_phong_van'] ?? null,
                'hinh_thuc_phong_van' => $item['hinh_thuc_phong_van'] ?? null,
                'nguoi_phong_van' => $item['nguoi_phong_van'] ?? null,
                'link_phong_van' => $item['link_phong_van'] ?? null,
                'ket_qua_phong_van' => $item['ket_qua_phong_van'] ?? null,
                'ghi_chu' => $item['ghi_chu'] ?? null,
                'thoi_gian_ung_tuyen' => $item['thoi_gian_ung_tuyen'],
            ]);

            $tong++;
        }

        $hoSoCongKhai = $hoSos->where('trang_thai', HoSo::TRANG_THAI_CONG_KHAI)->values();
        $tinHoatDong = $tins->filter(fn ($tin) => $tin->trang_thai === TinTuyenDung::TRANG_THAI_HOAT_DONG)->values();

        foreach ($hoSoCongKhai as $hoSo) {
            $ungVienId = $hoSo->nguoi_dung_id;
            $daCoUngTuyen = UngTuyen::where('ho_so_id', $hoSo->id)->exists();

            if ($daCoUngTuyen || !$ungVienId || $tinHoatDong->isEmpty()) {
                continue;
            }

            $tin = $tinHoatDong->random();
            $trangThai = collect([
                UngTuyen::TRANG_THAI_CHO_DUYET,
                UngTuyen::TRANG_THAI_DA_XEM,
                UngTuyen::TRANG_THAI_DA_XEM,
                UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN,
                UngTuyen::TRANG_THAI_TU_CHOI,
            ])->random();

            $duocHenPhongVan = $trangThai === UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN;
            $biTuChoi = $trangThai === UngTuyen::TRANG_THAI_TU_CHOI;

            UngTuyen::create([
                'tin_tuyen_dung_id' => $tin->id,
                'ho_so_id' => $hoSo->id,
                'trang_thai' => $trangThai,
                'da_rut_don' => false,
                'thu_xin_viec' => 'Tôi quan tâm đến vị trí này vì nội dung công việc phù hợp với kinh nghiệm và định hướng phát triển hiện tại. Mong có cơ hội trao đổi thêm để hiểu rõ hơn về sản phẩm, phạm vi công việc và kỳ vọng của công ty.',
                'ngay_hen_phong_van' => $duocHenPhongVan
                    ? $nowUtc->copy()->addDays(rand(1, 6))->setHour(rand(1, 8))->setMinute([0, 15, 30, 45][array_rand([0, 15, 30, 45])])
                    : null,
                'trang_thai_tham_gia_phong_van' => $duocHenPhongVan ? [UngTuyen::PHONG_VAN_CHO_XAC_NHAN, UngTuyen::PHONG_VAN_DA_XAC_NHAN][array_rand([UngTuyen::PHONG_VAN_CHO_XAC_NHAN, UngTuyen::PHONG_VAN_DA_XAC_NHAN])] : null,
                'thoi_gian_phan_hoi_phong_van' => $duocHenPhongVan && rand(0, 100) > 45
                    ? $nowUtc->copy()->subHours(rand(4, 30))
                    : null,
                'hinh_thuc_phong_van' => $duocHenPhongVan ? (rand(0, 1) ? 'Online' : 'Offline') : null,
                'nguoi_phong_van' => $duocHenPhongVan ? $tin->congTy?->ten_cong_ty . ' HR Team' : null,
                'link_phong_van' => $duocHenPhongVan && rand(0, 1)
                    ? 'https://meet.google.com/interview-' . strtolower(str_replace(' ', '-', (string) $tin->id . '-' . $hoSo->id))
                    : null,
                'ket_qua_phong_van' => $biTuChoi
                    ? 'Hồ sơ phù hợp ở mức cơ bản nhưng công ty ưu tiên ứng viên có kinh nghiệm sát hơn với vị trí.'
                    : null,
                'ghi_chu' => $biTuChoi
                    ? 'Lưu hồ sơ cho đợt tuyển dụng tiếp theo.'
                    : ($duocHenPhongVan ? 'Đơn seed tự động ở trạng thái đã hẹn phỏng vấn.' : null),
                'thoi_gian_ung_tuyen' => $nowUtc->copy()->subDays(rand(1, 9))->setHour(rand(1, 12))->setMinute(rand(0, 59)),
            ]);

            $tong++;
        }

        $this->command->info("✅ UngTuyenSeeder: Đã tạo {$tong} lượt ứng tuyển với dữ liệu phong phú và khớp flow mới.");
    }
}
