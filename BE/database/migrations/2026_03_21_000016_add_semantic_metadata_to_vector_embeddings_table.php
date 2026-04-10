<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('vector_embeddings', function (Blueprint $table) {
            $table->string('embedding_hash', 64)->nullable()->after('model_name');
            $table->json('metadata_json')->nullable()->after('embedding_hash');

            $table->index('embedding_hash', 'vector_embeddings_hash_idx');
            $table->unique(['entity_type', 'entity_id', 'chunk_index'], 'vector_embeddings_entity_chunk_unique');
        });
    }

    public function down(): void
    {
        Schema::table('vector_embeddings', function (Blueprint $table) {
            $table->dropUnique('vector_embeddings_entity_chunk_unique');
            $table->dropIndex('vector_embeddings_hash_idx');
            $table->dropColumn(['embedding_hash', 'metadata_json']);
        });
    }
};
