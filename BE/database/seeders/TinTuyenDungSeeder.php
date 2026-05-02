<?php

namespace Database\Seeders;

use App\Models\CongTy;
use App\Models\NganhNghe;
use App\Models\TinTuyenDung;
use Carbon\Carbon;
use Illuminate\Database\Seeder;

class TinTuyenDungSeeder extends Seeder
{
    public function run(): void
    {
        $congTys = CongTy::all()->keyBy('ten_cong_ty');
        $nganhNghes = NganhNghe::all()->keyBy('ten_nganh');

        if ($congTys->isEmpty() || $nganhNghes->isEmpty()) {
            return;
        }

        $tinMau = [
            [
                'cong_ty' => 'TechViet Solutions',
                'tieu_de' => 'Backend Developer Laravel',
                'mo_ta_cong_viec' => "Tham gia phát triển hệ thống quản trị bán hàng và API phục vụ mobile app.\nPhối hợp với BA và frontend để phân tích yêu cầu, thiết kế database và triển khai tính năng mới.\nTối ưu hiệu năng truy vấn, xử lý bug production và hỗ trợ release định kỳ.",
                'dia_diem_lam_viec' => 'Quận 1, TP. Hồ Chí Minh',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 2,
                'muc_luong_tu' => 18000000,
                'muc_luong_den' => 28000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 2 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Cao đẳng/Đại học',
                'ngay_het_han' => Carbon::now()->addDays(24),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 286,
                'nganh_nghes' => ['Công nghệ thông tin', 'Lập trình Backend'],
            ],
            [
                'cong_ty' => 'TechViet Solutions',
                'tieu_de' => 'QA Engineer (Manual/API)',
                'mo_ta_cong_viec' => "Thiết kế test case, test checklist cho các module web admin và API.\nPhối hợp với developer để tái hiện lỗi, xác nhận fix và đảm bảo chất lượng trước khi release.\nTham gia cải tiến quy trình kiểm thử và quản lý defect trên Jira.",
                'dia_diem_lam_viec' => 'Quận 1, TP. Hồ Chí Minh',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 1,
                'muc_luong_tu' => 14000000,
                'muc_luong_den' => 22000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 2 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Cao đẳng/Đại học',
                'ngay_het_han' => Carbon::now()->addDays(18),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 173,
                'nganh_nghes' => ['Công nghệ thông tin', 'Kiểm thử phần mềm (QA)'],
            ],
            [
                'cong_ty' => 'TechViet Solutions',
                'tieu_de' => 'Frontend Developer Vue.js',
                'mo_ta_cong_viec' => "Phát triển giao diện cho dashboard quản trị, cổng khách hàng và các module nội bộ trên nền tảng web.\nLàm việc với UI/UX designer để chuyển thiết kế thành giao diện responsive, tối ưu trải nghiệm trên nhiều kích thước màn hình.\nTích hợp API, xử lý state và phối hợp review code cùng team backend.",
                'dia_diem_lam_viec' => 'Quận 1, TP. Hồ Chí Minh',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 2,
                'muc_luong_tu' => 16000000,
                'muc_luong_den' => 25000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 2 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Cao đẳng/Đại học',
                'ngay_het_han' => Carbon::now()->addDays(26),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 228,
                'nganh_nghes' => ['Công nghệ thông tin', 'Lập trình Frontend'],
            ],
            [
                'cong_ty' => 'TechViet Solutions',
                'tieu_de' => 'DevOps Engineer',
                'mo_ta_cong_viec' => "Quản lý môi trường staging, production và tối ưu quy trình CI/CD cho các dự án web app, API và worker.\nThiết lập monitoring, logging, backup dữ liệu và phối hợp xử lý các sự cố hạ tầng khi có phát sinh.\nƯu tiên ứng viên có kinh nghiệm Docker, Linux, Nginx và cloud service cơ bản.",
                'dia_diem_lam_viec' => 'Quận 1, TP. Hồ Chí Minh',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Senior',
                'so_luong_tuyen' => 1,
                'muc_luong_tu' => 25000000,
                'muc_luong_den' => 38000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 3 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Đại học',
                'ngay_het_han' => Carbon::now()->addDays(32),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 157,
                'nganh_nghes' => ['Công nghệ thông tin', 'DevOps / SysAdmin'],
            ],
            [
                'cong_ty' => 'DigiGrowth Agency',
                'tieu_de' => 'Digital Marketing Executive',
                'mo_ta_cong_viec' => "Lên kế hoạch và triển khai chiến dịch Facebook Ads, Google Ads cho khách hàng ngành bán lẻ và giáo dục.\nTheo dõi CPL, ROAS, CTR, tối ưu ngân sách theo tuần và báo cáo kết quả cho account manager.\nPhối hợp content, design để sản xuất landing page và bộ creative phù hợp từng nhóm khách hàng.",
                'dia_diem_lam_viec' => 'Hải Châu, Đà Nẵng',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 2,
                'muc_luong_tu' => 12000000,
                'muc_luong_den' => 18000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 1-2 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Đại học',
                'ngay_het_han' => Carbon::now()->addDays(21),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 241,
                'nganh_nghes' => ['Marketing / Truyền thông', 'Digital Marketing'],
            ],
            [
                'cong_ty' => 'DigiGrowth Agency',
                'tieu_de' => 'Content Marketing Intern',
                'mo_ta_cong_viec' => "Hỗ trợ viết nội dung social, blog SEO và email marketing dưới sự hướng dẫn của team lead.\nTham gia nghiên cứu insight khách hàng, tổng hợp keyword và lên outline bài viết.\nPhù hợp với sinh viên năm cuối hoặc người mới đi làm muốn học quy trình content bài bản.",
                'dia_diem_lam_viec' => 'Hải Châu, Đà Nẵng',
                'hinh_thuc_lam_viec' => 'Thực tập',
                'cap_bac' => 'Thực tập sinh',
                'so_luong_tuyen' => 3,
                'muc_luong_tu' => 3000000,
                'muc_luong_den' => 5000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Không yêu cầu kinh nghiệm',
                'trinh_do_yeu_cau' => 'Sinh viên năm 3 trở lên',
                'ngay_het_han' => Carbon::now()->addDays(27),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 119,
                'nganh_nghes' => ['Marketing / Truyền thông', 'Content Marketing'],
            ],
            [
                'cong_ty' => 'DigiGrowth Agency',
                'tieu_de' => 'Graphic Designer Marketing',
                'mo_ta_cong_viec' => "Thiết kế banner, key visual, social post và landing page theo định hướng chiến dịch của team account và performance.\nPhối hợp content để phát triển bộ creative phù hợp từng tệp khách hàng, đảm bảo đúng deadline và guideline thương hiệu.\nThành thạo Figma hoặc Adobe Illustrator, có tư duy bố cục tốt và cập nhật xu hướng thiết kế số.",
                'dia_diem_lam_viec' => 'Hải Châu, Đà Nẵng',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 1,
                'muc_luong_tu' => 10000000,
                'muc_luong_den' => 16000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 1-2 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Cao đẳng/Đại học',
                'ngay_het_han' => Carbon::now()->addDays(19),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 143,
                'nganh_nghes' => ['Marketing / Truyền thông', 'Thiết kế đồ hoạ'],
            ],
            [
                'cong_ty' => 'DigiGrowth Agency',
                'tieu_de' => 'Account Executive',
                'mo_ta_cong_viec' => "Làm đầu mối tiếp nhận nhu cầu từ khách hàng, phối hợp với team nội bộ để triển khai chiến dịch và theo dõi tiến độ công việc.\nChuẩn bị proposal, timeline, biên bản họp và cập nhật tình trạng dự án định kỳ.\nPhù hợp với ứng viên có kỹ năng giao tiếp tốt, cẩn thận trong quản lý đầu việc và yêu thích môi trường agency.",
                'dia_diem_lam_viec' => 'Hải Châu, Đà Nẵng',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 1,
                'muc_luong_tu' => 9000000,
                'muc_luong_den' => 14000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 1 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Đại học',
                'ngay_het_han' => Carbon::now()->addDays(22),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 131,
                'nganh_nghes' => ['Marketing / Truyền thông', 'Content Marketing'],
            ],
            [
                'cong_ty' => 'NorthStar Analytics',
                'tieu_de' => 'Data Analyst',
                'mo_ta_cong_viec' => "Khai thác dữ liệu từ nhiều nguồn, làm sạch dữ liệu và xây dựng dashboard theo nhu cầu kinh doanh.\nPhân tích xu hướng doanh thu, hiệu quả vận hành và đưa ra insight hỗ trợ các phòng ban.\nLàm việc với SQL, Power BI hoặc Tableau, phối hợp với data engineer trong các dự án chuẩn hóa dữ liệu.",
                'dia_diem_lam_viec' => 'Cầu Giấy, Hà Nội',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Chuyên viên',
                'so_luong_tuyen' => 2,
                'muc_luong_tu' => 20000000,
                'muc_luong_den' => 32000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 2-4 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Đại học',
                'ngay_het_han' => Carbon::now()->addDays(30),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 312,
                'nganh_nghes' => ['Công nghệ thông tin', 'Phân tích dữ liệu'],
            ],
            [
                'cong_ty' => 'NorthStar Analytics',
                'tieu_de' => 'BI Developer',
                'mo_ta_cong_viec' => "Xây dựng data model, dashboard quản trị và các báo cáo định kỳ cho khối tài chính, vận hành và bán hàng.\nTiếp nhận yêu cầu từ stakeholder, chuẩn hóa số liệu và bảo đảm tính nhất quán của chỉ số trên toàn hệ thống.\nƯu tiên ứng viên có kinh nghiệm Power BI, SQL Server và ETL cơ bản.",
                'dia_diem_lam_viec' => 'Cầu Giấy, Hà Nội',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 1,
                'muc_luong_tu' => 18000000,
                'muc_luong_den' => 26000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 2 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Đại học',
                'ngay_het_han' => Carbon::now()->subDays(3),
                'trang_thai' => TinTuyenDung::TRANG_THAI_TAM_NGUNG,
                'luot_xem' => 167,
                'nganh_nghes' => ['Công nghệ thông tin', 'Phân tích dữ liệu'],
            ],
            [
                'cong_ty' => 'NorthStar Analytics',
                'tieu_de' => 'Data Engineer',
                'mo_ta_cong_viec' => "Thiết kế pipeline thu thập và xử lý dữ liệu từ nhiều nguồn như CRM, ERP, file batch và API đối tác.\nPhối hợp cùng đội analyst để chuẩn hóa dữ liệu đầu vào, tối ưu lịch chạy và giám sát chất lượng dữ liệu.\nƯu tiên ứng viên có nền tảng SQL tốt, làm việc được với Python hoặc công cụ ETL phổ biến.",
                'dia_diem_lam_viec' => 'Cầu Giấy, Hà Nội',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'so_luong_tuyen' => 1,
                'muc_luong_tu' => 22000000,
                'muc_luong_den' => 34000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 2-4 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Đại học',
                'ngay_het_han' => Carbon::now()->addDays(28),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 209,
                'nganh_nghes' => ['Công nghệ thông tin', 'Phân tích dữ liệu'],
            ],
            [
                'cong_ty' => 'NorthStar Analytics',
                'tieu_de' => 'Business Analyst',
                'mo_ta_cong_viec' => "Thu thập yêu cầu từ khách hàng doanh nghiệp, mô tả luồng nghiệp vụ và chuyển hóa thành tài liệu đặc tả cho đội data và kỹ thuật.\nTheo dõi tiến độ triển khai, hỗ trợ UAT và bảo đảm phạm vi dự án được kiểm soát rõ ràng.\nCần khả năng giao tiếp tốt, tư duy hệ thống và kinh nghiệm làm việc với dashboard hoặc báo cáo doanh nghiệp là lợi thế.",
                'dia_diem_lam_viec' => 'Cầu Giấy, Hà Nội',
                'hinh_thuc_lam_viec' => 'Toàn thời gian',
                'cap_bac' => 'Chuyên viên',
                'so_luong_tuyen' => 1,
                'muc_luong_tu' => 17000000,
                'muc_luong_den' => 26000000,
                'don_vi_luong' => 'VND/tháng',
                'kinh_nghiem_yeu_cau' => 'Từ 2 năm kinh nghiệm',
                'trinh_do_yeu_cau' => 'Đại học',
                'ngay_het_han' => Carbon::now()->addDays(23),
                'trang_thai' => TinTuyenDung::TRANG_THAI_HOAT_DONG,
                'luot_xem' => 154,
                'nganh_nghes' => ['Công nghệ thông tin', 'Phân tích dữ liệu'],
            ],
        ];

        $tong = 0;

        foreach ($tinMau as $tin) {
            $congTy = $congTys->get($tin['cong_ty']);
            if (!$congTy) {
                continue;
            }

            $record = TinTuyenDung::create([
                'tieu_de' => $tin['tieu_de'],
                'mo_ta_cong_viec' => $tin['mo_ta_cong_viec'],
                'dia_diem_lam_viec' => $tin['dia_diem_lam_viec'],
                'hinh_thuc_lam_viec' => $tin['hinh_thuc_lam_viec'],
                'cap_bac' => $tin['cap_bac'],
                'so_luong_tuyen' => $tin['so_luong_tuyen'],
                'muc_luong_tu' => $tin['muc_luong_tu'],
                'muc_luong_den' => $tin['muc_luong_den'],
                'don_vi_luong' => $tin['don_vi_luong'],
                'kinh_nghiem_yeu_cau' => $tin['kinh_nghiem_yeu_cau'],
                'trinh_do_yeu_cau' => $tin['trinh_do_yeu_cau'],
                'ngay_het_han' => $tin['ngay_het_han'],
                'cong_ty_id' => $congTy->id,
                'trang_thai' => $tin['trang_thai'],
                'luot_xem' => $tin['luot_xem'],
            ]);

            $nganhIds = collect($tin['nganh_nghes'])
                ->map(fn ($ten) => $nganhNghes->get($ten)?->id)
                ->filter()
                ->values();

            if ($nganhIds->isNotEmpty()) {
                $record->nganhNghes()->attach($nganhIds);
            }

            $tong++;
        }

        $tinPhatSinh = [
            [
                'prefix' => 'Chuyên viên vận hành thương mại điện tử',
                'dia_diem' => 'Ninh Kiều, Cần Thơ',
                'hinh_thuc' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'muc_tu' => 10000000,
                'muc_den' => 15000000,
                'kinh_nghiem' => 'Từ 1 năm kinh nghiệm',
                'trinh_do' => 'Cao đẳng/Đại học',
                'nganh_nghes' => ['Kinh doanh / Bán hàng', 'Thương mại điện tử'],
                'mo_ta_cong_viec' => "Quản lý danh mục sản phẩm, tồn kho và chương trình khuyến mãi trên sàn thương mại điện tử hoặc website bán hàng.\nTheo dõi hiệu quả vận hành đơn hàng, tỷ lệ hoàn và phối hợp với bộ phận marketing để tối ưu doanh số.\nPhù hợp với ứng viên chủ động, nắm được quy trình xử lý đơn và có kỹ năng làm việc với số liệu cơ bản.",
            ],
            [
                'prefix' => 'Nhân viên chăm sóc khách hàng online',
                'dia_diem' => 'Ninh Kiều, Cần Thơ',
                'hinh_thuc' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'muc_tu' => 8000000,
                'muc_den' => 12000000,
                'kinh_nghiem' => 'Ưu tiên có 6 tháng kinh nghiệm',
                'trinh_do' => 'Trung cấp/Cao đẳng',
                'nganh_nghes' => ['Kinh doanh / Bán hàng', 'Nhân viên kinh doanh'],
                'mo_ta_cong_viec' => "Tư vấn khách hàng qua chat, hotline và các kênh mạng xã hội, hỗ trợ xử lý đơn hàng và phản hồi khiếu nại cơ bản.\nPhối hợp với kho vận và bộ phận bán hàng để bảo đảm trải nghiệm khách hàng xuyên suốt.\nYêu cầu giao tiếp rõ ràng, kiên nhẫn và làm việc được theo ca trong khung giờ hành chính mở rộng.",
            ],
            [
                'prefix' => 'Cloud Support Engineer',
                'dia_diem' => 'Ba Đình, Hà Nội',
                'hinh_thuc' => 'Remote',
                'cap_bac' => 'Nhân viên',
                'muc_tu' => 15000000,
                'muc_den' => 24000000,
                'kinh_nghiem' => 'Từ 1-3 năm kinh nghiệm',
                'trinh_do' => 'Đại học',
                'nganh_nghes' => ['Công nghệ thông tin', 'DevOps / SysAdmin'],
                'mo_ta_cong_viec' => "Theo dõi hạ tầng cloud, hỗ trợ cấu hình tài nguyên, xử lý ticket vận hành và phối hợp với đội dự án để xử lý sự cố.\nTham gia tài liệu hóa quy trình triển khai, backup và giám sát dịch vụ.\nƯu tiên ứng viên có kinh nghiệm Linux, networking cơ bản và các dịch vụ cloud phổ biến.",
            ],
            [
                'prefix' => 'System Administrator',
                'dia_diem' => 'Ba Đình, Hà Nội',
                'hinh_thuc' => 'Toàn thời gian',
                'cap_bac' => 'Nhân viên',
                'muc_tu' => 14000000,
                'muc_den' => 22000000,
                'kinh_nghiem' => 'Từ 2 năm kinh nghiệm',
                'trinh_do' => 'Cao đẳng/Đại học',
                'nganh_nghes' => ['Công nghệ thông tin', 'DevOps / SysAdmin'],
                'mo_ta_cong_viec' => "Quản trị máy chủ nội bộ, tài khoản người dùng, chính sách phân quyền và theo dõi an toàn hệ thống cơ bản.\nPhối hợp triển khai phần mềm nội bộ, xử lý yêu cầu hỗ trợ kỹ thuật và bảo đảm hệ thống hoạt động ổn định.\nPhù hợp với ứng viên có kinh nghiệm Windows Server, Linux và tinh thần hỗ trợ người dùng tốt.",
            ],
        ];

        $congTyPhatSinh = $congTys->filter(function ($congTy, $ten) {
            return !in_array($ten, ['TechViet Solutions', 'DigiGrowth Agency', 'NorthStar Analytics'], true);
        })->values();

        foreach ($congTyPhatSinh as $index => $congTy) {
            $mauTheoCongTy = collect($tinPhatSinh)->chunk(2)->values();
            $danhSachTin = $mauTheoCongTy[$index % $mauTheoCongTy->count()];

            foreach ($danhSachTin as $mau) {
                $record = TinTuyenDung::create([
                    'tieu_de' => $mau['prefix'],
                    'mo_ta_cong_viec' => $mau['mo_ta_cong_viec'],
                    'dia_diem_lam_viec' => $mau['dia_diem'],
                    'hinh_thuc_lam_viec' => $mau['hinh_thuc'],
                    'cap_bac' => $mau['cap_bac'],
                    'so_luong_tuyen' => rand(1, 3),
                    'muc_luong_tu' => $mau['muc_tu'],
                    'muc_luong_den' => $mau['muc_den'],
                    'don_vi_luong' => 'VND/tháng',
                    'kinh_nghiem_yeu_cau' => $mau['kinh_nghiem'],
                    'trinh_do_yeu_cau' => $mau['trinh_do'],
                    'ngay_het_han' => Carbon::now()->addDays(rand(12, 35)),
                    'cong_ty_id' => $congTy->id,
                    'trang_thai' => $congTy->trang_thai,
                    'luot_xem' => rand(45, 180),
                ]);

                $nganhIds = collect($mau['nganh_nghes'])
                    ->map(fn ($ten) => $nganhNghes->get($ten)?->id)
                    ->filter()
                    ->values();

                if ($nganhIds->isNotEmpty()) {
                    $record->nganhNghes()->attach($nganhIds);
                }

                $tong++;
            }
        }

        $this->command->info("✅ TinTuyenDungSeeder: Đã tạo {$tong} tin tuyển dụng với JD và lương gần thực tế.");
    }
}
