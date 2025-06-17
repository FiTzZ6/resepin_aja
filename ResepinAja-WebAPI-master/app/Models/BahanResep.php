<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class BahanResep extends Model
{
    use HasFactory;
    protected $table = 'bahan_resep';

    protected $primaryKey = 'id_bahan';

    public $incrementing = false;

    protected $fillable = [
        'id_resep',
        'nama_bahan',
        'jml_bahan',
        'stn_bahan'
    ];

    public function resep()
    {
        return $this->belongsTo(Resep::class, 'id_resep');
    }
}
