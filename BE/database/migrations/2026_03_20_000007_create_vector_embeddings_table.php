<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('vector_embeddings', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->enum('entity_type', ['ho_so', 'tin_tuyen_dung', 'ai_chat_message', 'tu_van_nghe_nghiep']);
            $table->unsignedBigInteger('entity_id');
            $table->integer('chunk_index')->default(0);
            $table->longText('text_content');
            $table->json('embedding_vector');
            $table->string('model_name', 100);
            $table->timestamps();

            $table->index(['entity_type', 'entity_id'], 'vector_embeddings_entity_idx');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('vector_embeddings');
    }
};
