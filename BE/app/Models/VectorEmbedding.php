<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class VectorEmbedding extends Model
{
    use HasFactory;

    protected $table = 'vector_embeddings';

    protected $fillable = [
        'entity_type',
        'entity_id',
        'chunk_index',
        'text_content',
        'embedding_vector',
        'model_name',
        'embedding_hash',
        'metadata_json',
    ];

    protected $casts = [
        'entity_id' => 'integer',
        'chunk_index' => 'integer',
        'embedding_vector' => 'array',
        'metadata_json' => 'array',
    ];
}
