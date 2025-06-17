<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class AlatResep extends Model
{
    use HasFactory;
    protected $table = 'alat_resep';

    protected $primaryKey = 'id_alat';

    public $incrementing = false;

    protected $fillable = [
        'id_resep', 'nama_alat',
    ];

    public function resep()
    {
        return $this->belongsTo(Resep::class, 'id_resep');
    }
}
