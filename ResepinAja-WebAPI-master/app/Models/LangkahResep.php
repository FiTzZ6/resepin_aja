<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LangkahResep extends Model
{
    use HasFactory;
    protected $table = 'langkah_resep';

    protected $primaryKey = 'id_langkah';

    public $incrementing = false;

    protected $fillable = [
        'id_resep', 'urutan', 'cara_langkah',
    ];

    public function resep()
    {
        return $this->belongsTo(Resep::class, 'id_resep');
    }
}
