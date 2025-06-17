<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('resep', function (Blueprint $table) {
            $table->id('id_resep');                      // primary key auto-increment
            $table->string('judul');
            $table->string('gambar');
            $table->text('deskripsi');
            $table->string('wkt_masak');
            $table->string('prs_masak');
            $table->integer('id_user');                   // harus sama tipe dengan users.id_user
            $table->timestamps();

        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('resep');
    }
};