<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Rating extends Model
{
    use HasFactory;
    protected $table = 'rating';

    protected $primaryKey = 'id_rating';

    protected $fillable = [
        'id_resep', 'bintang', 'id_user', 'komentar',
    ];

    public function resep()
    {
        return $this->belongsTo(Resep::class, 'id_resep');
    }
}
