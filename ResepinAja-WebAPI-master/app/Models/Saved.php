<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Saved extends Model
{
    use HasFactory;
    protected $table = 'saved';

    protected $primaryKey = 'id_saved';

    protected $fillable = [
        'id_user', 'id_resep'
    ];
    
    public function resep()
    {
        return $this->belongsTo(Resep::class, 'id_resep');
    }
}
