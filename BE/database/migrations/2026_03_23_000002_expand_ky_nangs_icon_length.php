<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        DB::statement('ALTER TABLE ky_nangs MODIFY icon VARCHAR(255) NULL');
    }

    public function down(): void
    {
        DB::statement('ALTER TABLE ky_nangs MODIFY icon VARCHAR(100) NULL');
    }
};
