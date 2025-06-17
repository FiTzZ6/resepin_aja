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
        Schema::create('bahan_resep', function (Blueprint $table) {
            $table->id('id_bahan'); 
            $table->integer('id_resep'); 
            $table->string('nama_bahan');
            $table->integer('jml_bahan');
            $table->enum('stn_bahan', ['Buah', 'gr', 'ml']);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('bahan_resep');
    }
};