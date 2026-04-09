<?php

namespace Database\Seeders;

use App\Models\KyNang;
use App\Models\NguoiDung;
use App\Models\NguoiDungKyNang;
use Illuminate\Database\Seeder;

class NguoiDungKyNangSeeder extends Seeder
{
    /**
     * Seed dữ liệu bảng nguoi_dung_ky_nangs.
     * Gắn kỹ năng + chứng chỉ cá nhân cho các ứng viên.
     */
    public function run(): void
    {
        $ungViens = NguoiDung::where('vai_tro', 0)->get();

        if ($ungViens->isEmpty()) {
            $this->command->warn('⚠️ Chưa có ứng viên. Hãy chạy NguoiDungSeeder trước.');
            return;
        }

        $kyNangs = KyNang::all();

        if ($kyNangs->isEmpty()) {
            $this->command->warn('⚠️ Chưa có kỹ năng. Hãy chạy KyNangSeeder trước.');
            return;
        }

        $tong = 0;

        // --- UV 1: Full-stack Developer ---
        $uv1 = $ungViens->firstWhere('email', 'ung.vien1@kltn.com');
        if ($uv1) {
            $kyNangUV1 = [
                ['ten' => 'PHP', 'muc_do' => 4, 'nam' => 3, 'cc' => 1, 'anh' => 'php-cert.jpg'],
                ['ten' => 'Laravel', 'muc_do' => 4, 'nam' => 3, 'cc' => 1, 'anh' => 'laravel-cert.jpg'],
                ['ten' => 'JavaScript', 'muc_do' => 3, 'nam' => 2, 'cc' => 0, 'anh' => null],
                ['ten' => 'React', 'muc_do' => 3, 'nam' => 2, 'cc' => 0, 'anh' => null],
                ['ten' => 'MySQL', 'muc_do' => 4, 'nam' => 3, 'cc' => 1, 'anh' => 'mysql-cert.jpg'],
                ['ten' => 'Docker', 'muc_do' => 2, 'nam' => 1, 'cc' => 0, 'anh' => null],
                ['ten' => 'Git', 'muc_do' => 4, 'nam' => 3, 'cc' => 0, 'anh' => null],
                ['ten' => 'REST API', 'muc_do' => 5, 'nam' => 3, 'cc' => 0, 'anh' => null],
                ['ten' => 'Tiếng Anh', 'muc_do' => 3, 'nam' => 5, 'cc' => 2, 'anh' => 'ielts-cert.jpg'],
            ];

            foreach ($kyNangUV1 as $kn) {
                $kyNang = $kyNangs->firstWhere('ten_ky_nang', $kn['ten']);
                if ($kyNang) {
                    NguoiDungKyNang::create([
                        'nguoi_dung_id' => $uv1->id,
                        'ky_nang_id' => $kyNang->id,
                        'muc_do' => $kn['muc_do'],
                        'nam_kinh_nghiem' => $kn['nam'],
                        'so_chung_chi' => $kn['cc'],
                        'hinh_anh' => $kn['anh'],
                    ]);
                    $tong++;
                }
            }
        }

        // --- UV 2: Frontend Developer ---
        $uv2 = $ungViens->firstWhere('email', 'ung.vien2@kltn.com');
        if ($uv2) {
            $kyNangUV2 = [
                ['ten' => 'JavaScript', 'muc_do' => 5, 'nam' => 4, 'cc' => 1, 'anh' => 'js-cert.png'],
                ['ten' => 'TypeScript', 'muc_do' => 4, 'nam' => 2, 'cc' => 0, 'anh' => null],
                ['ten' => 'React', 'muc_do' => 5, 'nam' => 3, 'cc' => 1, 'anh' => 'react-cert.png'],
                ['ten' => 'Vue.js', 'muc_do' => 3, 'nam' => 1, 'cc' => 0, 'anh' => null],
                ['ten' => 'Next.js', 'muc_do' => 3, 'nam' => 1, 'cc' => 0, 'anh' => null],
                ['ten' => 'Figma', 'muc_do' => 2, 'nam' => 1, 'cc' => 0, 'anh' => null],
                ['ten' => 'Git', 'muc_do' => 3, 'nam' => 2, 'cc' => 0, 'anh' => null],
            ];

            foreach ($kyNangUV2 as $kn) {
                $kyNang = $kyNangs->firstWhere('ten_ky_nang', $kn['ten']);
                if ($kyNang) {
                    NguoiDungKyNang::create([
                        'nguoi_dung_id' => $uv2->id,
                        'ky_nang_id' => $kyNang->id,
                        'muc_do' => $kn['muc_do'],
                        'nam_kinh_nghiem' => $kn['nam'],
                        'so_chung_chi' => $kn['cc'],
                        'hinh_anh' => $kn['anh'],
                    ]);
                    $tong++;
                }
            }
        }

        // Gắn random cho các UV còn lại
        $uvConLai = $ungViens->whereNotIn('email', ['ung.vien1@kltn.com', 'ung.vien2@kltn.com']);
        foreach ($uvConLai as $uv) {
            $randomKyNangs = $kyNangs->random(min(rand(3, 6), $kyNangs->count()));
            foreach ($randomKyNangs as $kn) {
                NguoiDungKyNang::create([
                    'nguoi_dung_id' => $uv->id,
                    'ky_nang_id' => $kn->id,
                    'muc_do' => rand(1, 5),
                    'nam_kinh_nghiem' => rand(0, 8),
                    'so_chung_chi' => rand(0, 2),
                    'hinh_anh' => null,
                ]);
                $tong++;
            }
        }

        $this->command->info("✅ NguoiDungKyNangSeeder: Đã tạo {$tong} bản ghi kỹ năng (kèm chứng chỉ) cho ứng viên!");
    }
}
