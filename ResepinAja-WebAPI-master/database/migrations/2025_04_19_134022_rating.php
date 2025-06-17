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
        Schema::create('rating', function (Blueprint $table) {
            $table->id('id_rating'); // primary key
            $table->integer('id_resep'); // foreign key ke reseps
            $table->integer('bintang'); // rating bintang
            $table->integer('id_user'); // user yang memberikan rating
            $table->text('komentar')->nullable(); // komentar yang diberikan oleh user
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('rating');
    }
};
