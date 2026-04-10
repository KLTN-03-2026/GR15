<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('market_stats_daily', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->date('stat_date');
            $table->unsignedBigInteger('nganh_nghe_id')->nullable();
            $table->integer('avg_salary')->nullable();
            $table->integer('median_salary')->nullable();
            $table->integer('demand_count')->default(0);
            $table->json('top_skills')->nullable();
            $table->timestamp('created_at')->nullable()->useCurrent();

            $table->foreign('nganh_nghe_id')
                ->references('id')
                ->on('nganh_nghes')
                ->onDelete('set null');

            $table->unique(['stat_date', 'nganh_nghe_id'], 'market_stats_daily_unique');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('market_stats_daily');
    }
};
