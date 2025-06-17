<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;
    protected $primaryKey = 'id_user';

    protected $fillable = [
        'username',
        'password',
        'deskripsi_user',
        'no_hp',
        'role',
    ];

    protected $hidden = [
        'password',
    ];
}