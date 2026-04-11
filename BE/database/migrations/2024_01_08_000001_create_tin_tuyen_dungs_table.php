<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('tin_tuyen_dungs', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->string('tieu_de', 200);
            $table->text('mo_ta_cong_viec')->nullable();
            $table->string('dia_diem_lam_viec', 255)->nullable();
            $table->string('hinh_thuc_lam_viec', 50)->nullable()->comment('Toàn thời gian, Bán thời gian, Remote...');
            $table->string('cap_bac', 50)->nullable()->comment('Thực tập sinh, Nhân viên, Quản lý...');
            $table->integer('so_luong_tuyen')->default(1);
            $table->integer('muc_luong')->nullable()->comment('Mức lương ước tính (VNĐ)');
            $table->integer('muc_luong_tu')->nullable();
            $table->integer('muc_luong_den')->nullable();
            $table->string('don_vi_luong', 20)->nullable()->default('VND');
            $table->string('kinh_nghiem_yeu_cau', 100)->nullable();
            $table->string('trinh_do_yeu_cau', 100)->nullable();
            $table->dateTime('ngay_het_han')->nullable();
            $table->integer('luot_xem')->default(0);
            $table->unsignedBigInteger('cong_ty_id');
            $table->tinyInteger('trang_thai')->default(1)->comment('1: hoat_dong, 0: tam_ngung');
            $table->timestamp('published_at')->nullable();
            $table->timestamp('reactivated_at')->nullable();
            $table->timestamps();

            $table->foreign('cong_ty_id')
                ->references('id')
                ->on('cong_tys')
                ->onDelete('cascade');

            $table->index('cong_ty_id');
            $table->index('trang_thai');
            $table->index('ngay_het_han');
        });

        Schema::create('chi_tiet_nganh_nghes', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->unsignedBigInteger('tin_tuyen_dung_id');
            $table->unsignedBigInteger('nganh_nghe_id');
            $table->timestamps();

            $table->foreign('tin_tuyen_dung_id')
                ->references('id')
                ->on('tin_tuyen_dungs')
                ->onDelete('cascade');

            $table->foreign('nganh_nghe_id')
                ->references('id')
                ->on('nganh_nghes')
                ->onDelete('cascade');

            $table->unique(['tin_tuyen_dung_id', 'nganh_nghe_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('chi_tiet_nganh_nghes');
        Schema::dropIfExists('tin_tuyen_dungs');
    }
};
