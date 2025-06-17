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
        Schema::create('langkah_resep', function (Blueprint $table) {
            $table->id('id_langkah'); // custom primary key
            $table->integer('id_resep'); // foreign key ke reseps
            $table->integer('urutan'); // urutan langkah
            $table->text('cara_langkah'); // deskripsi langkah
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('langkah_resep');
    }
};
