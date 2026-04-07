<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::statement('ALTER TABLE tin_tuyen_dungs MODIFY ngay_het_han DATETIME NULL');
    }

    public function down(): void
    {
        DB::statement('ALTER TABLE tin_tuyen_dungs MODIFY ngay_het_han DATE NULL');
    }
};
