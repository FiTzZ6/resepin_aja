<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Resep extends Model
{
    use HasFactory;
    protected $table = 'resep';

    protected $primaryKey = 'id_resep';

    protected $fillable = [
        'judul',
        'gambar',
        'deskripsi',
        'wkt_masak',
        'prs_masak',
        'ktg_masak',
        'id_user',
    ];

    public function user()
    {
        return $this->belongsTo(User::class, 'id_user', 'id_user');
    }

    public function bahanReseps()
    {
        return $this->hasMany(BahanResep::class, 'id_resep', 'id_resep');
    }

    public function langkahReseps()
    {
        return $this->hasMany(LangkahResep::class, 'id_resep', 'id_resep');
    }
    public function alatReseps()
    {
        return $this->hasMany(AlatResep::class, 'id_resep', 'id_resep');
    }
}
