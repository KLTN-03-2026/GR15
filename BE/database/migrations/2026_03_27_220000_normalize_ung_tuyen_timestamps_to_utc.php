<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::statement("
            UPDATE ung_tuyens
            SET
                thoi_gian_ung_tuyen = CASE
                    WHEN thoi_gian_ung_tuyen IS NOT NULL THEN DATE_SUB(thoi_gian_ung_tuyen, INTERVAL 7 HOUR)
                    ELSE NULL
                END,
                thoi_gian_phan_hoi_phong_van = CASE
                    WHEN thoi_gian_phan_hoi_phong_van IS NOT NULL THEN DATE_SUB(thoi_gian_phan_hoi_phong_van, INTERVAL 7 HOUR)
                    ELSE NULL
                END,
                thoi_gian_rut_don = CASE
                    WHEN thoi_gian_rut_don IS NOT NULL THEN DATE_SUB(thoi_gian_rut_don, INTERVAL 7 HOUR)
                    ELSE NULL
                END
        ");
    }

    public function down(): void
    {
        DB::statement("
            UPDATE ung_tuyens
            SET
                thoi_gian_ung_tuyen = CASE
                    WHEN thoi_gian_ung_tuyen IS NOT NULL THEN DATE_ADD(thoi_gian_ung_tuyen, INTERVAL 7 HOUR)
                    ELSE NULL
                END,
                thoi_gian_phan_hoi_phong_van = CASE
                    WHEN thoi_gian_phan_hoi_phong_van IS NOT NULL THEN DATE_ADD(thoi_gian_phan_hoi_phong_van, INTERVAL 7 HOUR)
                    ELSE NULL
                END,
                thoi_gian_rut_don = CASE
                    WHEN thoi_gian_rut_don IS NOT NULL THEN DATE_ADD(thoi_gian_rut_don, INTERVAL 7 HOUR)
                    ELSE NULL
                END
        ");
    }
};
