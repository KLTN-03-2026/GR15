<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        if (!Schema::hasTable('nguoi_dung_ky_nangs')) {
            Schema::create('nguoi_dung_ky_nangs', function (Blueprint $table) {
                $table->bigIncrements('id');
                $table->unsignedBigInteger('nguoi_dung_id');
                $table->unsignedBigInteger('ky_nang_id');
                $table->tinyInteger('muc_do')->default(1);
                $table->integer('nam_kinh_nghiem')->default(0);
                $table->integer('so_chung_chi')->default(0);
                $table->string('hinh_anh')->nullable();
                $table->string('nguon_du_lieu', 50)->nullable();
                $table->decimal('do_tin_cay', 5, 2)->nullable();
                $table->timestamps();

                $table->foreign('nguoi_dung_id')
                    ->references('id')
                    ->on('nguoi_dungs')
                    ->onDelete('cascade');

                $table->foreign('ky_nang_id')
                    ->references('id')
                    ->on('ky_nangs')
                    ->onDelete('cascade');

                $table->unique(['nguoi_dung_id', 'ky_nang_id'], 'ndkn_nguoi_dung_ky_nang_unique');
            });
        }

        if (!Schema::hasTable('ket_qua_matchings')) {
            Schema::create('ket_qua_matchings', function (Blueprint $table) {
                $table->bigIncrements('id');
                $table->unsignedBigInteger('ho_so_id');
                $table->unsignedBigInteger('tin_tuyen_dung_id');
                $table->float('diem_phu_hop');
                $table->float('diem_ky_nang')->nullable();
                $table->float('diem_kinh_nghiem')->nullable();
                $table->float('diem_hoc_van')->nullable();
                $table->json('chi_tiet_diem')->nullable();
                $table->json('matched_skills_json')->nullable();
                $table->json('missing_skills_json')->nullable();
                $table->text('explanation')->nullable();
                $table->text('danh_sach_ky_nang_thieu')->nullable();
                $table->string('model_version', 50)->default('local-matching-v1');
                $table->timestamp('thoi_gian_match')->useCurrent();
                $table->timestamps();

                $table->foreign('ho_so_id')
                    ->references('id')
                    ->on('ho_sos')
                    ->onDelete('cascade');

                $table->foreign('tin_tuyen_dung_id')
                    ->references('id')
                    ->on('tin_tuyen_dungs')
                    ->onDelete('cascade');

                $table->unique(['ho_so_id', 'tin_tuyen_dung_id', 'model_version'], 'kqm_unique_match');
            });
        }

        if (!Schema::hasTable('tu_van_nghe_nghieps')) {
            Schema::create('tu_van_nghe_nghieps', function (Blueprint $table) {
                $table->bigIncrements('id');
                $table->unsignedBigInteger('nguoi_dung_id');
                $table->unsignedBigInteger('ho_so_id')->nullable();
                $table->string('nghe_de_xuat', 150);
                $table->float('muc_do_phu_hop');
                $table->json('goi_y_ky_nang_bo_sung')->nullable();
                $table->longText('bao_cao_chi_tiet')->nullable();
                $table->string('model_version', 50)->default('local-career-report-v1');
                $table->timestamps();

                $table->foreign('nguoi_dung_id')
                    ->references('id')
                    ->on('nguoi_dungs')
                    ->onDelete('cascade');

                $table->foreign('ho_so_id')
                    ->references('id')
                    ->on('ho_sos')
                    ->onDelete('set null');
            });
        }

        if (Schema::hasTable('ung_tuyens')) {
            Schema::table('ung_tuyens', function (Blueprint $table) {
                if (!Schema::hasColumn('ung_tuyens', 'hinh_thuc_phong_van')) {
                    $table->string('hinh_thuc_phong_van', 50)->nullable()->after('ngay_hen_phong_van');
                }

                if (!Schema::hasColumn('ung_tuyens', 'link_phong_van')) {
                    $table->string('link_phong_van')->nullable()->after('hinh_thuc_phong_van');
                }

                if (!Schema::hasColumn('ung_tuyens', 'nguoi_phong_van')) {
                    $table->string('nguoi_phong_van')->nullable()->after('link_phong_van');
                }

                if (!Schema::hasColumn('ung_tuyens', 'trang_thai_tham_gia_phong_van')) {
                    $table->tinyInteger('trang_thai_tham_gia_phong_van')->default(0)->after('nguoi_phong_van');
                }

                if (!Schema::hasColumn('ung_tuyens', 'thoi_gian_phan_hoi_phong_van')) {
                    $table->timestamp('thoi_gian_phan_hoi_phong_van')->nullable()->after('trang_thai_tham_gia_phong_van');
                }

                if (!Schema::hasColumn('ung_tuyens', 'da_rut_don')) {
                    $table->boolean('da_rut_don')->default(false)->after('thoi_gian_phan_hoi_phong_van');
                }

                if (!Schema::hasColumn('ung_tuyens', 'thoi_gian_rut_don')) {
                    $table->timestamp('thoi_gian_rut_don')->nullable()->after('da_rut_don');
                }
            });
        }
    }

    public function down(): void
    {
        if (Schema::hasTable('ung_tuyens')) {
            Schema::table('ung_tuyens', function (Blueprint $table) {
                foreach ([
                    'thoi_gian_rut_don',
                    'da_rut_don',
                    'thoi_gian_phan_hoi_phong_van',
                    'trang_thai_tham_gia_phong_van',
                    'nguoi_phong_van',
                    'link_phong_van',
                    'hinh_thuc_phong_van',
                ] as $column) {
                    if (Schema::hasColumn('ung_tuyens', $column)) {
                        $table->dropColumn($column);
                    }
                }
            });
        }

        Schema::dropIfExists('tu_van_nghe_nghieps');
        Schema::dropIfExists('ket_qua_matchings');
        Schema::dropIfExists('nguoi_dung_ky_nangs');
    }
};
